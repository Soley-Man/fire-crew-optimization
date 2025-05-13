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