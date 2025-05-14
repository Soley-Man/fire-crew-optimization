import csv
import statistics as stat
from collections import defaultdict
from constants import CUMULATIVE_DAYS, SEASON_START

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

def dict_to_csv(dictionaries: list[dict[str, str]], file_path) -> None:
    '''
    Export a list of dictionaries as a csv file.
    '''
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=dictionaries[0].keys())
        writer.writeheader()
        writer.writerows(dictionaries)

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

def is_mixed_gender(fire_rangers_data: list[dict[str, str]], crew: list[int]):
    '''
    Return true if crew contains Rangers of mixed genders.
    The parameter crew is a list of Fire Rangers' indexes in the solution.
    '''
    genders = set()

    for ranger_id in crew:
        genders.add(fire_rangers_data[ranger_id]['Gender'])
    
    return len(genders) > 1

def is_certified(fire_rangers_data: list[dict[str, str]], ranger_id: int):
    '''
    Return true if the Ranger has a national fitness certification.
    '''
    return fire_rangers_data[ranger_id]['Fitness Certification'] == 'National'

def has_mixed_gender_restriction(fire_rangers_data: list[dict[str, str]], ranger_id: int):
    '''
    Return true if the Ranger must not be placed in a mixed gender crew.
    ''' 
    return fire_rangers_data[ranger_id]['Mixed Crew Restrictions'] != ''

def is_in_crew(fire_rangers_data: list[dict[str, str]], crew: list[int], ranger_name: str):
    '''
    Return true if the Ranger with ranger_name is in the crew.
    '''
    for ranger_id in crew:
        if fire_rangers_data[ranger_id]['Name'] == ranger_name:
            return True
    return False

def count_overlapping_unavailabilities(fire_rangers_data: list[dict[str, str]], ranger_ids: list[int], max_unavailable_rangers=0):
    '''
    Return the number of overlapping unavailable days for Rangers in ranger_ids.
    If max_unavailable_rangers = 0, only count the days when all Fire Rangers are unavailable.
    If max_unavailable_rangers > 0, count the days when at least n fire Rangers are unavailable.
    '''
    understaffed_days = 0
    all_unavailabilities = []

    for id in ranger_ids:
        for unavailable_day in fire_rangers_data[id]['Unavailabilities']:
            all_unavailabilities.append(unavailable_day)
    
    for day in set(all_unavailabilities):
        if max_unavailable_rangers == 0 and all_unavailabilities.count(day) == len(ranger_ids):
            understaffed_days += 1
        elif max_unavailable_rangers > 0 and all_unavailabilities.count(day) > max_unavailable_rangers:
            understaffed_days += 1

    return understaffed_days

def avg_experience(fire_rangers_data: list[dict[str, str]], crew: list[int]) -> float:
    '''
    Return the average experience of crew.
    '''
    return round( stat.mean([int(fire_rangers_data[ranger_id]['Years of Experience']) for ranger_id in crew]), 2)
