import random
from utils import rangers_to_crew, avg_experience
from penalties import personal_prefs_penalty, understaffing_penalty, mixed_crew_restrictions_penalty, fitness_certification_penalty

# Cost Function
def calculate_cost(fire_rangers_data: list[dict[str, str]], solution: list[int], leaders_indexes: list[int], bosses_indexes: list[int], avg_base_experience: float) -> int:
    '''
    Return the cost of solution.
    '''
    cost = 0
    crew_assignment = rangers_to_crew(solution)
    diff_crew_base_xp = []

    for crew_id, ranger_ids in crew_assignment.items():
        leadership_idndexes = [idx for idx in ranger_ids if idx in leaders_indexes + bosses_indexes]

        # Personal Preferences Penalty
        cost += personal_prefs_penalty(fire_rangers_data, ranger_ids)

        # Understaffing Penalty
        cost += understaffing_penalty(fire_rangers_data, ranger_ids, leadership_idndexes)

        # Mixed Crew Restriction Penalty
        cost += mixed_crew_restrictions_penalty(fire_rangers_data, ranger_ids)

        # Fitness Certification Penalty
        cost += fitness_certification_penalty(fire_rangers_data, ranger_ids, leadership_idndexes)

        # Record squared difference between average crew experience and average base experience
        avg_crew_exp = avg_experience(fire_rangers_data, ranger_ids)
        diff_crew_base_xp.append((avg_crew_exp - avg_base_experience) ** 2)

    # Experience Variance Penalty
    experience_variance = sum(diff_crew_base_xp) / len(crew_assignment)
    cost += experience_variance * 100

    return round(cost)

# Perturbation Function
def perturbate(solution, leaders_indexes, bosses_indexes, members_indexes):
    '''
    Return a neighbour of solution by swapping two Crew Leaders,
    Crew Bosses, or Crew Members in order to maintain a valid solution.
    '''

    crew_assignment = rangers_to_crew(solution)

    # Randomly select a crew
    first_crew_id = random.choice(list(crew_assignment.keys()))

    # Randomly select a Ranger from the crew
    first_ranger_id = random.choice(crew_assignment[first_crew_id])

    # Randomly select a second crew
    other_crews = list(crew_assignment.keys())
    other_crews.remove(first_crew_id)
    second_crew_id = random.choice(other_crews)

    # From the second crew, randomly select a Ranger with the same role as the first
    if first_ranger_id in leaders_indexes:
        for ranger_id in crew_assignment[second_crew_id]:
            if ranger_id in leaders_indexes:
                second_ranger_id = ranger_id
    elif first_ranger_id in bosses_indexes:
        for ranger_id in crew_assignment[second_crew_id]:
            if ranger_id in bosses_indexes:
                second_ranger_id = ranger_id
    elif first_ranger_id in members_indexes:
        crew_members = [ranger_id for ranger_id in crew_assignment[second_crew_id] if ranger_id in members_indexes]
        second_ranger_id = random.choice(crew_members)
    
    # Swap the two Rangers
    neighbour_solution = solution[:]
    neighbour_solution[first_ranger_id] = second_crew_id
    neighbour_solution[second_ranger_id] = first_crew_id

    return neighbour_solution
