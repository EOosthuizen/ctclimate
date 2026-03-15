# Import libraries and assign aliases for quick reference
import pandas as pd

### Day 1 ###

# Read spreadsheet containing data
df = pd.read_csv('GlobalLandTemperaturesByMajorCity.csv')

# Inspect data frame
#print(df.head(10))  # to see first 10 lines
#print(df.info())  # to see variable types

# Inspect unique cities in dataset
cities = df['City'].unique()
#print(cities)
print(f"\n----------\nTotal unique cities found: {len(cities)}\n----------\n")

### Day 2 ###

# Create data subset for Cape Town only
ct_df = df[df['City'] == 'Cape Town'].copy()

# Process date-time string variable
ct_df['dt'] = pd.to_datetime(ct_df['dt'])
ct_df['year'] = ct_df['dt'].dt.year
print("\n----------\nDisplaying 3 header lines for CT subset:\n", ct_df.head(3), "\n----------\n")
#print(ct_df.info())
print("Cape Town has environmental data from ", min(ct_df['year']), " to ", max(ct_df['year']), ". Displaying first and last 5 entries:")

# Successfully integrated this project onto GitHub!

# Add month variable to assign seasons
def get_season(month): # create a function that inputs a month variable and returns the corresponding austral season
    if month in [12, 1, 2]:
        return 'Summer'
    elif month in [3, 4, 5]:
        return 'Autumn'
    elif month in [6, 7, 8]:
        return 'Winter'
    else:
        return 'Spring'

ct_df['month'] = ct_df['dt'].dt.month
ct_df['season'] = ct_df['month'].apply(get_season)
ct_season_df_preview = pd.concat([ct_df.head(5), ct_df.tail(5)], ignore_index=True)
print(ct_season_df_preview)

### Day 3 ###

# Create pivot table to inspect trends
season_trends = ct_df.pivot_table(values = 'AverageTemperature',
                                  index = 'year',
                                  columns = 'season')
winter_trend = season_trends['Winter'].dropna().tail(50) # annual temperature series for winter seasons
print(winter_trend.describe()) # inspect summary statistics for winter temperatures
first_decade_avg = winter_trend.head(10).mean() # calculate average temperature during first decade (starting 1964)
last_decade_avg = winter_trend.tail(10).mean() # calculate average temperature during first decade (ending 2013)
temp_shift = last_decade_avg - first_decade_avg
print(f"\n ---------- \nAverage winter temperature in first decade (1964 - 1973): {first_decade_avg:.2f} °C")
print(f"Average winter temperature in last decade (2004 - 2013): {last_decade_avg:.2f} °C")
print(f"Five-decade winter temperature shift: {temp_shift:.2f} °C")


