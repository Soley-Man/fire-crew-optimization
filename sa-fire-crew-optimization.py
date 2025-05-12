import csv
import random
import math
import statistics as stat
from collections import defaultdict

# Constants
SEASON_START = 'May 1'
SEASON_END = 'August 31'

# Supporting Functions
def csv_to_dict(file_path: str) -> list[dict[str: str]]:
    """
    Read a CSV file and return a list of dictionaries.
    Each dictionary represents a row, with keys as column headers.
    """
    data = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def parse_date_str(date_str: str) -> tuple[str, int]:
    """
    Parses a date string like 'May 9' into month and day.
    """
    parts = date_str.strip().split()
    return parts[0], int(parts[1])

def date_to_day_number(date_str: str) -> int:
    """
    Converts a date string (e.g. 'May 9') to a day number relative to SEASON_START.

    Args:
        date_str (str): Date in the format 'Month day', e.g., 'May 9'

    Returns:
        int: Day number relative to SEASON_START (e.g., May 1 = 0)
    """
    month, day = parse_date_str(date_str)
    start_month, start_day = parse_date_str(SEASON_START)
    input_day_of_year = CUMULATIVE_DAYS[month] + day
    start_day_of_year = CUMULATIVE_DAYS[start_month] + start_day
    return input_day_of_year - start_day_of_year

def rangers_to_crew(solution: list[int]) -> dict[int: list[int]]:
    '''
    Return a dictionary pairing crew IDs with the list of Fire Rangers in that crew.
    Fire Rangers are represented as their indexes in the solution.
    '''
    crew_assignment = defaultdict(list)
    for ranger_id, crew_id in enumerate(solution):
        crew_assignment[crew_id].append(ranger_id)
    
    return crew_assignment

def is_mixed_gender(crew: list[int]):
    """
    Return true if crew contains Rangers of mixed genders.
    The parameter crew is a list of Fire Rangers' indexes in the solution.
    """
    genders = set()

    for ranger_id in crew:
        genders.add(fire_rangers[ranger_id]["Gender"])
    
    return len(genders) > 1

def is_certified(ranger_id: int):
    """
    Return true if the Ranger has a national fitness certification.
    """
    return fire_rangers[ranger_id]["Fitness Certification"] == "National"

def has_mixed_gender_restriction(ranger_id: int):
    """
    Return true if the Ranger must not be placed in a mixed gender crew.
    """ 
    return fire_rangers[ranger_id]["Mixed Crew Restrictions"] != ''

def is_in_crew(crew: list[int], ranger_name: str):
    """
    Return true if the Ranger with ranger_name is in the crew.
    """
    for ranger_id in crew:
        if fire_rangers[ranger_id]["Name"] == ranger_name:
            return True
    return False

def count_overlapping_unavailabilities(ranger_ids: list[int], n=0):
    """
    Return the number of overlapping unavailable days for Rangers in ranger_ids.
    If n=0, only count the days when all Fire Rangers are unavailable. If n > 0, count the days when at least n fire Rangers are unavailable.
    """
    count = 0
    all_unavailabilities = []

    for id in ranger_ids:
        for unavailable_day in fire_rangers[id]["Unavailabilities"]:
            all_unavailabilities.append(unavailable_day)
    
    for day in set(all_unavailabilities):
        if n == 0 and all_unavailabilities.count(day) == len(ranger_ids):
            count += 1
        elif n > 0 and all_unavailabilities.count(day) >= n:
            count += 1

    return count

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
    "January": 31, "February": 28, "March": 31, "April": 30,
    "May": 31, "June": 30, "July": 31, "August": 31,
    "September": 30, "October": 31, "November": 30, "December": 31
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
    try:
        ranger['Same crew preferences'] = ranger['Same crew preferences'].split(',')
    except:
        pass
    try:
        ranger['Different crew preferences'] = ranger['Different crew preferences'].split(',')
    except: 
        pass

## Calculate average experience across the fire base
avg_experience_base = round( stat.mean([int(ranger["Years of Experience"]) for ranger in fire_rangers]), 2)

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

    for crew_id, ranger_ids in crew_assignment.items():
        pass

# Create Neighbour

# ...