# Import libraries and assign aliases for quick reference

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np

### Day 1 ###

# Read spreadsheet containing data
global_df = pd.read_csv('GlobalLandTemperaturesByMajorCity.csv')

# Inspect unique cities in dataset
def find_cities(kaggle_dataset: pd.DataFrame,
                country: str = None):
    if country is None:
        cities = kaggle_dataset['City'].unique()
        find_cities_out: str = (f"\n----------\nFound {len(cities)} unique cities across {len(kaggle_dataset['Country'].unique())} countries total:\n"
                                f"{cities}")
    elif country in kaggle_dataset['Country'].unique():
        cities = kaggle_dataset[kaggle_dataset['Country'] == country]['City'].unique()
        find_cities_out: str = (f"\n----------\nFound {len(cities)} unique cities within {country}:\n"
                                f"{cities}")
    else:
        find_cities_out: str = f"{country} not found in dataset."
    print(find_cities_out)


### Day 2 ###

# Define function to subset global dataset by a specified city
def get_city_data(city: str) -> pd.DataFrame:
    city_data = global_df[global_df['City'] == city].copy()
    if city_data.empty:
        print(f"No data found for {city} - check spelling or capitalisation")
        start_letter = city[0].upper()
        matching_cities = global_df[global_df['City'].str.startswith(start_letter)]
        matching_cities_list = matching_cities['City'].unique().tolist
        print(f"Did you mean one of the following cities?\n{matching_cities_list}")
        return city_data
    else:
        print(f"Data loaded for {city}")
        raw_missing_count = city_data['AverageTemperature'].isnull().sum()
        city_data['dt'] = pd.to_datetime(city_data['dt'])
        city_data['year'] = city_data['dt'].dt.year
        city_data['month'] = city_data['dt'].dt.month
        city_data['season'] = city_data['month'].apply(get_season)

        missing_mask = city_data['AverageTemperature'].isnull()
        data_gap_summary = city_data[missing_mask].groupby('year').size()
        print(f"There are {raw_missing_count} monthly temperature records missing for {city}:")
        for year, count in data_gap_summary.items():
            print(f" * {year}: {count} months missing")

        print(f"Filling in missing values using linear interpolation...")

        city_data['AverageTemperature'] = city_data['AverageTemperature'].interpolate("linear")

        interpolated_missing_count = city_data['AverageTemperature'].isnull().sum()
        if interpolated_missing_count > 0:
            print(f"{interpolated_missing_count} records missing after linear interpolation! Ensure that data starts with a point to interpolate from!")
        else:
            print(f"All {raw_missing_count} missing values successfully interpolated")

        print(f"Preview:\n{city_data.head(3)}\n{city_data.tail(3)}")

        return city_data


def get_season(month): # create a function that inputs a month variable and returns the corresponding austral season
    if month in [12, 1, 2]:
        return 'Summer'
    elif month in [3, 4, 5]:
        return 'Autumn'
    elif month in [6, 7, 8]:
        return 'Winter'
    else:
        return 'Spring'

def city_show_years(city:str = None):
    city_data = get_city_data(city)
    city_start_year = city_data['year'].min()
    city_end_year = city_data['year'].max()
    print(f"{city} has environmental data from {city_start_year} to {city_end_year}.")

# Successfully integrated this project onto GitHub!

# Add month variable to assign seasons




### Day 3 ###

# Create function to create a pivot table to extract seasonal mean temperature shift
def season_trends(climate_df: pd.DataFrame,
                  season: str,
                  decades_timespan: int):
    season_trends_pivot = climate_df.pivot_table(values = 'AverageTemperature', index = 'year', columns = 'season')
    years_timespan = decades_timespan * 10
    season_trend = season_trends_pivot[season].dropna().tail(years_timespan)
    start_year = season_trend.index.min()
    end_year = season_trend.index.max()
    first_decade_avg: float = season_trend.head(10).mean()  # calculate average temperature during first decade (starting 1964)
    last_decade_avg: float = season_trend.tail(10).mean()  # calculate average temperature during first decade (ending 2013)
    temp_shift: float = last_decade_avg - first_decade_avg
    season_trend_summary = (
        f"\n---------- {season} mean temperature shift per decade since {start_year} ----------\n"
        f"Mean temperature in first decade ({start_year} - {start_year+10}) : {first_decade_avg:.2f} °C\n"
        f"Mean temperature in last decade ({end_year-10} - {end_year}): {last_decade_avg:.2f} °C\n"
        f"Mean temperature shift over the last {decades_timespan} decades: {temp_shift:.2f} °C\n")
    return season_trend_summary

#print(season_trends(climate_df = ct_df, season = 'Winter', decades_timespan = 5))
#print(season_trends(climate_df = ct_df, season = 'Winter', decades_timespan = 10))
#print(season_trends(climate_df = ct_df, season = 'Summer', decades_timespan = 10))

### Day 4 ###

# Configure seaborn and plot winter temperature regression

do_ct: bool = False

if do_ct:
    ct_df = get_city_data("Cape Town")

    sns.set_theme(style = 'whitegrid', context = 'talk')
    sns.set_palette('colorblind')
    winter_data = ct_df[ct_df['season'] == "Winter"].groupby('year')['AverageTemperature'].mean().reset_index() # combine winter data into mean annual temperatures
    winter_data_five_decades = winter_data.tail(50)
# Create plot
    plt.figure(figsize=(12, 6))
    sns.regplot(data=winter_data_five_decades, x='year', y='AverageTemperature',
                scatter_kws={'s': 50, 'alpha': 0.6},
                line_kws={'color': 'darkred', 'lw': 3})
    plt.title('Cape Town: winter warming trend (last 50 years)')
    plt.xlabel('Year')
    plt.ylabel('Average winter temp (°C)')
    plt.tight_layout()
#plt.show() # winter temperature regression plot (no statistical annotation)

### Day 5 ###

def check_years(city: str,
                start_year: int,
                end_year: int) -> bool:
    # Handle default years
    if start_year is None or end_year is None:
        print(f"Must specify start and end years!")
        return False

    # Ensure valid input year order
    if start_year > end_year:
        print(f"Invalid time interval: start year ({start_year}) must be smaller than end year ({end_year})")
        return False

    city_df = get_city_data(city)
    if city_df.empty:
        return False
    min_year = city_df['year'].min()
    max_year = city_df['year'].max()

    # Ensure start and end year are within bounds
    if not min_year <= start_year <= max_year or not min_year <= end_year <= max_year:
        print(f"Invalid start or end year(s) - must be between {min_year} and {max_year}")
        return False
    else:
        return True

def plot_city_season_regression(city: str,
                                season: str,
                                start_year: int = None,
                                end_year: int = None,
                                show_stats: bool = True) -> None:

    if not check_years(city, start_year, end_year):
        return

    # Proceed with handling and plotting
    city_df = get_city_data(city)
    if city_df.empty:
        print(f"No data found for {city} during {season}.")
        return
    city_season_data: pd.DataFrame = (
        city_df[
            (city_df['season'] == season) &
            (city_df['year'].between(start_year, end_year))
         ].groupby('year')['AverageTemperature'].mean().reset_index()
    )
    # Ensure df is populated
    if city_season_data.empty:
        print(f"No data found for {city} during {season}.")
        return

    # Proceed with plotting
    slope, intercept, r_value, p_value, std_err = stats.linregress(city_season_data['year'], city_season_data['AverageTemperature'])
    r_squared = r_value ** 2
    plt.figure(figsize=(12, 6))
    ax = sns.regplot(data=city_season_data, x='year', y='AverageTemperature', line_kws={'color': 'red'})
    stats_text = f"Slope: {slope:.4f}\n$R^2$: {r_squared:.4f}"
    if show_stats: ax.text(0.8255, 0.0288, stats_text, transform=ax.transAxes, bbox=dict(facecolor='white', alpha=1, boxstyle='square', edgecolor='black', linewidth=0.8))
    plt.title(f"{season} mean temperature: {city} ({start_year} - {end_year})")
    plt.xlabel('Year')
    plt.ylabel(f"{season} mean temp. (°C)")
    plt.show()

### Day 6 ###

# Add century label to data (3 different approaches)

if do_ct:
    ct_df = get_city_data("Cape Town")
    winter_data = ct_df[ct_df['season'] == "Winter"].groupby('year')['AverageTemperature'].mean().reset_index()
    winter_data['century'] = ((np.floor(winter_data['year'])/100)+1).astype(int) # add century labels as integers by rounding down
    winter_data['century'] = (winter_data['year'] // 100)+1 # different, more efficient logic with floor division
    def get_century_string(year): # alternatively, define function to return century as language string
        if year < 1900:
            return "19th"
        elif year < 2000:
            return "20th"
        else:
            return "21st"

    winter_data['century'] = winter_data['year'].apply(get_century_string) # apply century labels to rows
    #print(winter_data.head(), winter_data.tail()) # inspect labels

    # Generate ridge plot to compare temperature distributions by century
    plt.figure(figsize=(12, 6))
    sns.kdeplot(data=winter_data,
                x='AverageTemperature',
                hue='century',
                fill=True,
                common_norm=False, # normalise independently to prevent small sample bias from 21st century
                palette='colorblind',
                alpha=0.4,
                linewidth=0.8
                )
    plt.title('Cape Town winter temperature distribution by century', fontsize=14)
    plt.xlabel('Average winter temperature (°C)')
    plt.ylabel('Density')
    plt.grid(axis='y', alpha=0.3)
    #plt.show()



### Day 7 ###

# Created function to plot regression trend for defined season over defined interval
#plot_city_season_regression("Durban", "Winter", 1500, 2013, True)


### Day 8 ###

def plot_city_season_kde(city: str,
                         season: str) -> None:
    city_data = get_city_data(city)
    if city_data.empty:
        return

    city_season_data: pd.DataFrame = city_data[city_data['season'] == season].groupby('year')['AverageTemperature'].mean().reset_index()
    city_season_data['century'] = city_season_data['year'] // 100 + 1

    plt.figure(figsize=(12, 6))
    sns.kdeplot(data=city_season_data,
                x='AverageTemperature',
                hue='century',
                fill=True,
                common_norm=False,  # normalise independently to prevent small sample bias from 21st century
                palette='colorblind',
                alpha=0.4,
                linewidth=0.8
                )
    plt.title(f'{city} {season} temperature distribution per century ({city_season_data['year'].min()} - {city_season_data['year'].max()})', fontsize=14)
    plt.xlabel(f'Average {season} temperature (°C)')
    plt.ylabel('Density')
    plt.grid(axis='y', alpha=0.3)
    plt.show()

plot_city_season_kde("Cape Town", "Winter")