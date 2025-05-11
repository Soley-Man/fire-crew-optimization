import csv
import random
import math
import statistics as stat

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

# Create Neighbour

# ...