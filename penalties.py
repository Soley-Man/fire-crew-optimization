from utils import is_in_crew, count_overlapping_unavailabilities, is_mixed_gender, has_mixed_gender_restriction, is_certified

def personal_prefs_penalty(fire_rangers_data: list[dict[str, str]], crew: list[int]) -> int:
    '''
    Return the cost of unsatisfied personal preferences within crew.
    '''
    # Count rangers with unsatisfied 'same crew' personal preferences
    unsatisfied_rangers = 0

    for ranger_id in crew:
        if fire_rangers_data[ranger_id]['Same crew preferences']:
            # If any of the preferences are satisfied, the Ranger is satisfied
            if not any([is_in_crew(fire_rangers_data, crew, name) for name in fire_rangers_data[ranger_id]['Same crew preferences']]):
                unsatisfied_rangers += 1
    
    # Count unsatisfied 'different crew' preferences
    diff_crew_violations = 0

    for ranger_id in crew:
        for name in fire_rangers_data[ranger_id]['Different crew preferences']:
            if is_in_crew(fire_rangers_data, crew, name):
                diff_crew_violations += 1
    
    # Return cost increase
    return (unsatisfied_rangers + diff_crew_violations) * 10

def understaffing_penalty(fire_rangers_data: list[dict[str, str]], crew: list[int], leadership_indexes: list[int]) -> int:
    '''
    Return the cost of understaffing in crew.

    Precondition: len(leadership_indexes) = 2
    '''
    cost = 0

    # Check for leadership understaffing (at least one Crew Leader or Boss must be present in a crew)
    days_understaffed_leadership = count_overlapping_unavailabilities(fire_rangers_data, leadership_indexes)

    cost += days_understaffed_leadership * 500

    # Check for general understaffing (at least 3 Fire Rangers must be present in a crew)
    if len(crew) == 4:  # 4 person crew
        # At most 1 Ranger can be absent from the crew
        days_understaffed = count_overlapping_unavailabilities(fire_rangers_data, crew, n = 1)

        cost += days_understaffed * 100

    elif len(crew) == 5:  # 5 person crew
        # At most 2 rangers may be absent from the crew
        days_understaffed_by_1 = count_overlapping_unavailabilities(fire_rangers_data, crew, n = 1)
        days_understaffed_by_2 = count_overlapping_unavailabilities(fire_rangers_data, crew, n = 2)
        
        # The cost increases by 100 per day understaffed, per ranger missing
        cost += days_understaffed_by_1 * 100 + days_understaffed_by_2 * 2 * 100
    
    return cost

def mixed_crew_restrictions_penalty(fire_rangers_data: list[dict[str, str]], crew: list[int]) -> int:
    '''
    Return the cost of violations of mixed crew restrictions within crew.
    '''
    restrictions_violated = 0

    if is_mixed_gender(fire_rangers_data, crew):
        for ranger_id in crew:
            if has_mixed_gender_restriction(fire_rangers_data, ranger_id):
                restrictions_violated += 1
    
    return 500 * restrictions_violated

def fitness_certification_penalty(fire_rangers_data: list[dict[str, str]], crew: list[int], leadership_indexes: list[int]) -> int:
    '''
    Return the cost of unsatisfied fitness certification requirements.

    Precondition: len(leadership_indexes) = 2
    '''
    # Check if at least one member of Crew leadership is certified to National standards
    if not any([is_certified(fire_rangers_data, idx) for idx in leadership_indexes]):
        return 100
    
    # Check if less than 4 Rangers are certified to National standards
    amount_certified = len([ranger_id for ranger_id in crew if is_certified(fire_rangers_data, ranger_id)]) 
    if amount_certified < 4:
        return (4 - amount_certified) * 50
    
    return 0