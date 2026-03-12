# Import libraries and assign aliases for quick reference
import pandas as pd

### Day 1 ###

# Read spreadsheet containing data
df = pd.read_csv('GlobalLandTemperaturesByMajorCity.csv')

# Inspect data frame
print(df.head(10))  # to see first 10 lines
print(df.info())  # to see variable types

# Inspect unique cities in dataset
cities = df['City'].unique()
print(cities)
print(f"Total unique cities found: {len(cities)}")

### Day 2 ###

# Create data subset for Cape Town only
ct_df = df[df['City'] == 'Cape Town'].copy()

# Process date-time string variable
ct_df['dt'] = pd.to_datetime(ct_df['dt'])
ct_df['year'] = ct_df['dt'].dt.year
print(ct_df.head(10))
print(ct_df.info())
print("Cape Town has environmental data from ", min(ct_df['year']), " to ", max(ct_df['year']))

#Also, successfully integrated this project onto GitHub!
