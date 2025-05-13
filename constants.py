SEASON_START = 'May 1'
SEASON_END = 'August 31'

# Month to day count map (non-leap year)
MONTH_DAYS = {
    'January': 31, 'February': 28, 'March': 31, 'April': 30,
    'May': 31, 'June': 30, 'July': 31, 'August': 31,
    'September': 30, 'October': 31, 'November': 30, 'December': 31
}

# Precompute cumulative days at start of each month
CUMULATIVE_DAYS = {}
total = 0
for month, days in MONTH_DAYS.items():
    CUMULATIVE_DAYS[month] = total
    total += days