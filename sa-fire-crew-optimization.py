import csv
import random
import math
import statistics as stat
from collections import defaultdict

# Constants
SEASON_START = 'May 1'
SEASON_END = 'August 31'

# Supporting Functions
def csv_to_dict(file_path: str) -> list[dict[str, str]]:
    '''
    Read a CSV file and return a list of dictionaries.
    Each dictionary represents a row, with keys as column headers.
    '''
    data = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def parse_date_str(date_str: str) -> tuple[str, int]:
    '''
    Parses a date string like 'May 9' into month and day.
    '''
    parts = date_str.strip().split()
    return parts[0], int(parts[1])

def date_to_day_number(date_str: str) -> int:
    '''
    Converts a date string (e.g. 'May 9') to a day number relative to SEASON_START.

    Args:
        date_str (str): Date in the format 'Month day', e.g., 'May 9'

    Returns:
        int: Day number relative to SEASON_START (e.g., May 1 = 0)
    '''
    month, day = parse_date_str(date_str)
    start_month, start_day = parse_date_str(SEASON_START)
    input_day_of_year = CUMULATIVE_DAYS[month] + day
    start_day_of_year = CUMULATIVE_DAYS[start_month] + start_day
    return input_day_of_year - start_day_of_year

def rangers_to_crew(solution: list[int]) -> dict[int, list[int]]:
    '''
    Return a dictionary pairing crew IDs with the list of Fire Rangers in that crew.
    Fire Rangers are represented as their indexes in the solution.
    '''
    crew_assignment = defaultdict(list)
    for ranger_id, crew_id in enumerate(solution):
        crew_assignment[crew_id].append(ranger_id)
    
    return crew_assignment

def is_mixed_gender(crew: list[int]):
    '''
    Return true if crew contains Rangers of mixed genders.
    The parameter crew is a list of Fire Rangers' indexes in the solution.
    '''
    genders = set()

    for ranger_id in crew:
        genders.add(fire_rangers[ranger_id]['Gender'])
    
    return len(genders) > 1

def is_certified(ranger_id: int):
    '''
    Return true if the Ranger has a national fitness certification.
    '''
    return fire_rangers[ranger_id]['Fitness Certification'] == 'National'

def has_mixed_gender_restriction(ranger_id: int):
    '''
    Return true if the Ranger must not be placed in a mixed gender crew.
    ''' 
    return fire_rangers[ranger_id]['Mixed Crew Restrictions'] != ''

def is_in_crew(crew: list[int], ranger_name: str):
    '''
    Return true if the Ranger with ranger_name is in the crew.
    '''
    for ranger_id in crew:
        if fire_rangers[ranger_id]['Name'] == ranger_name:
            return True
    return False

def count_overlapping_unavailabilities(ranger_ids: list[int], n=0):
    '''
    Return the number of overlapping unavailable days for Rangers in ranger_ids.
    If n=0, only count the days when all Fire Rangers are unavailable. If n > 0, count the days when at least n fire Rangers are unavailable.
    '''
    count = 0
    all_unavailabilities = []

    for id in ranger_ids:
        for unavailable_day in fire_rangers[id]['Unavailabilities']:
            all_unavailabilities.append(unavailable_day)
    
    for day in set(all_unavailabilities):
        if n == 0 and all_unavailabilities.count(day) == len(ranger_ids):
            count += 1
        elif n > 0 and all_unavailabilities.count(day) >= n:
            count += 1

    return count

def avg_experience(crew: list[int]) -> float:
    '''
    Return the average experience of crew.
    '''
    return round( stat.mean([int(fire_rangers[ranger_id]['Years of Experience']) for ranger_id in crew]), 2)

def personal_prefs_penalty(crew: list[int]) -> int:
    '''
    Return the cost of unsatisfied personal preferences within crew.
    '''
    # Count rangers with unsatisfied 'same crew' personal preferences
    unsatisfied_rangers = 0

    for ranger_id in crew:
        if fire_rangers[ranger_id]['Same crew preferences']:
            # If any of the preferences are satisfied, the Ranger is satisfied
            if not any([is_in_crew(crew, name) for name in fire_rangers[ranger_id]['Same crew preferences']]):
                unsatisfied_rangers += 1
    
    # Count unsatisfied 'different crew' preferences
    diff_crew_violations = 0

    for ranger_id in crew:
        for name in fire_rangers[ranger_id]['Different crew preferences']:
            if is_in_crew(crew, name):
                diff_crew_violations += 1
    
    # Return cost increase
    return (unsatisfied_rangers + diff_crew_violations) * 10

def understaffing_penalty(crew: list[int], leadership_indexes: list[int]) -> int:
    '''
    Return the cost of understaffing in crew.

    Precondition: len(leadership_indexes) = 2
    '''
    cost = 0

    # Check for leadership understaffing (at least one Crew Leader or Boss must be present in a crew)
    days_understaffed_leadership = count_overlapping_unavailabilities(leadership_indexes)

    cost += days_understaffed_leadership * 500

    # Check for general understaffing (at least 3 Fire Rangers must be present in a crew)
    if len(crew) == 4:  # 4 person crew
        # At most 1 Ranger can be absent from the crew
        days_understaffed = count_overlapping_unavailabilities(crew, n = 1)

        cost += days_understaffed * 100

    elif len(crew) == 5:  # 5 person crew
        # At most 2 rangers may be absent from the crew
        days_understaffed_by_1 = count_overlapping_unavailabilities(crew, n = 1)
        days_understaffed_by_2 = count_overlapping_unavailabilities(crew, n = 2)
        
        # The cost increases by 100 per day understaffed, per ranger missing
        cost += days_understaffed_by_1 * 100 + days_understaffed_by_2 * 2 * 100
    
    return cost

def mixed_crew_restrictions_penalty(crew: list[int]) -> int:
    '''
    Return the cost of violations of mixed crew restrictions within crew.
    '''
    restrictions_violated = 0

    if is_mixed_gender(crew):
        for ranger_id in crew:
            if has_mixed_gender_restriction(ranger_id):
                restrictions_violated += 1
    
    return 500 * restrictions_violated

def fitness_certification_penalty(crew: list[int], leadership_indexes: list[int]) -> int:
    '''
    Return the cost of unsatisfied fitness certification requirements.

    Precondition: len(leadership_indexes) = 2
    '''
    # Check if at least one member of Crew leadership is certified to National standards
    if not any([is_certified(idx) for idx in leadership_indexes]):
        return 100
    
    # Check if less than 4 Rangers are certified to National standards
    amount_certified = len([ranger_id for ranger_id in crew if is_certified(ranger_id)]) 
    if amount_certified < 4:
        return (4 - amount_certified) * 50
    
    return 0

# Data Preparation
## Read Fire Rangers data
fire_rangers = csv_to_dict('fire-rangers-data.csv')
leaders_idx = [idx for idx, ranger in enumerate(fire_rangers) if ranger['Role'] == 'Leader']
bosses_idx = [idx for idx, ranger in enumerate(fire_rangers) if ranger['Role'] == 'Boss']
members_idx = [idx for idx, ranger in enumerate(fire_rangers) if ranger['Role'] == 'Member']

crews_n = math.floor(len(fire_rangers) / 4)
five_ranger_crews_n = len(fire_rangers) % 4

## Convert unavailable dates from a range to the day numbers of the season (i.e. 0, 1, 2... 122)
### Month to day count map (non-leap year)
MONTH_DAYS = {
    'January': 31, 'February': 28, 'March': 31, 'April': 30,
    'May': 31, 'June': 30, 'July': 31, 'August': 31,
    'September': 30, 'October': 31, 'November': 30, 'December': 31
}

### Precompute cumulative days at start of each month
CUMULATIVE_DAYS = {}
total = 0
for month, days in MONTH_DAYS.items():
    CUMULATIVE_DAYS[month] = total
    total += days

for ranger in fire_rangers:
    unavailabilities = []
    if ranger['Start Date']:
        start_day_num = date_to_day_number(ranger['Start Date'])
        unavailabilities.extend([n for n in range(start_day_num)])
    if ranger['End Date']:
        end_day_num = date_to_day_number(ranger['End Date'])
        unavailabilities.extend([n for n in range(end_day_num + 1, date_to_day_number(SEASON_END) + 1)]) # End Date is the last day of work
    
    ranger['Unavailabilities'] = unavailabilities

## Convert ranger preferences from string to list of names
for ranger in fire_rangers:
    same_prefs = ranger.get('Same crew preferences', '')
    ranger['Same crew preferences'] = same_prefs.split(',') if same_prefs else []

    diff_prefs = ranger.get('Different crew preferences', '')
    ranger['Different crew preferences'] = diff_prefs.split(',') if diff_prefs else []

## Calculate average experience across the fire base
avg_base_experience = round( stat.mean([int(ranger['Years of Experience']) for ranger in fire_rangers]), 2)

# Initialize Solution
crew_ids = [n for n in range(1, crews_n + 1)] * 4
crew_ids.extend( [n for n in range(1, five_ranger_crews_n + 1)] )

solution = [0 for id in range(len(crew_ids))]

## Shuffle to add randomness to initial solution
random.shuffle(leaders_idx)
random.shuffle(bosses_idx)
random.shuffle(members_idx)

for idx in leaders_idx:
    solution[idx] = crew_ids.pop(0)
for idx in bosses_idx:
    solution[idx] = crew_ids.pop(0)
for idx in members_idx:
    solution[idx] = crew_ids.pop(0)

# Cost Function
def calculate_cost(solution: list[int]) -> int:
    '''
    Return the cost of solution.
    '''
    cost = 0
    crew_assignment = rangers_to_crew(solution)
    diff_crew_base_xp = []

    for crew_id, ranger_ids in crew_assignment.items():
        leadership_idx = [idx for idx in ranger_ids if idx in leaders_idx + bosses_idx]

        # Personal Preferences Penalty
        cost += personal_prefs_penalty(ranger_ids)

        # Understaffing Penalty
        cost += understaffing_penalty(ranger_ids, leadership_idx)

        # Mixed Crew Restriction Penalty
        cost += mixed_crew_restrictions_penalty(ranger_ids)

        # Fitness Certification Penalty
        cost += fitness_certification_penalty(ranger_ids, leadership_idx)

        # Record squared difference between average crew experience and average base experience
        avg_crew_exp = avg_experience(ranger_ids)
        diff_crew_base_xp.append((avg_crew_exp - avg_base_experience) ** 2)

    # Experience Variance Penalty
    experience_variance = sum(diff_crew_base_xp) / len(crew_assignment)
    cost += experience_variance * 100

    return cost

# Create Neighbour

# ...