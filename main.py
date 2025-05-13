import statistics as stat
import math
import random
from constants import SEASON_END
from utils import csv_to_dict, date_to_day_number
from simulated_annealing import calculate_cost, perturbate, acceptance_func

# Data Preparation
## Read Fire Rangers data
fire_rangers = csv_to_dict('fire-rangers-data.csv')
leaders_idx = [idx for idx, ranger in enumerate(fire_rangers) if ranger['Role'] == 'Leader']
bosses_idx = [idx for idx, ranger in enumerate(fire_rangers) if ranger['Role'] == 'Boss']
members_idx = [idx for idx, ranger in enumerate(fire_rangers) if ranger['Role'] == 'Member']

crews_n = math.floor(len(fire_rangers) / 4)
five_ranger_crews_n = len(fire_rangers) % 4

## Convert unavailable dates from a range to the day numbers of the season (i.e. 0, 1, 2... 122)
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

# Run Simulated Annnealing
temperature = 10000
cooling_rate = 0.9999
end_temperature = 0.0001

iterations = 0

while temperature > end_temperature:
    neighbour_solution = perturbate(solution, leaders_idx, bosses_idx, members_idx)

    if acceptance_func(fire_rangers, solution, neighbour_solution, temperature, leaders_idx, bosses_idx, avg_base_experience):
        solution = neighbour_solution
    
    iterations += 1
    if iterations % 10000 == 0:
        print(calculate_cost(fire_rangers, solution, leaders_idx, bosses_idx, avg_base_experience), temperature)
    temperature *= cooling_rate

## Print results
solution_cost = calculate_cost(fire_rangers, solution, leaders_idx, bosses_idx, avg_base_experience)
print()
print('Iterations:', iterations)
print('Final solution cost:', solution_cost)
print('Final solution:', solution)
