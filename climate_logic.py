# Import libraries and assign aliases for quick reference

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pandas import DataFrame
from scipy import stats
import numpy as np
from typing import Optional, List
from statsmodels.tsa.seasonal import seasonal_decompose

### Day 1 ###

# Read spreadsheet containing data
def load_global_data() -> pd.DataFrame:
    df: pd.DataFrame = pd.read_csv('GlobalLandTemperaturesByMajorCity.csv')
    df['AverageTemperature'] = pd.to_numeric(df['AverageTemperature'], errors='coerce')
    df['dt'] = pd.to_datetime(df['dt'])
    df['year'] = df['dt'].dt.year.astype(int)
    df['month'] = df['dt'].dt.month.astype(int)
    df['season'] = df['month'].apply(get_season)
    return df

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
    global_data: DataFrame = load_global_data().copy()
    city_data = global_data[global_data['City'] == city]

    if city_data.empty:
        print(f'No data found for "{city}" - check spelling or capitalisation')
        start_letter = city[0].upper()
        matching_cities = global_data[global_data['City'].str.startswith(start_letter)]
        matching_cities_list = matching_cities['City'].unique().tolist()
        print(f"Did you mean one of the following cities?\n{matching_cities_list}")
        return city_data
    else:
        print(f"Data loaded for {city}")
        missing_mask = city_data['AverageTemperature'].isnull()
        raw_missing_count = missing_mask.sum()
        data_gap_summary = city_data[missing_mask].groupby('year').size()
        print(f"There are {raw_missing_count} monthly temperature records missing for {city}:")
        for year, count in data_gap_summary.items():
            print(f" * {year}: {count} months missing")
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
                line_kws={'color': 'red', 'lw': 3})
    plt.title('Cape Town: winter warming trend (last 50 years)')
    plt.xlabel('Year')
    plt.ylabel('Average winter temp (°C)')
    plt.tight_layout()
#plt.show() # winter temperature regression plot (no statistical annotation)

### Day 5 ###

def check_years(city_df: pd.DataFrame,
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
                                show_stats: bool = True) -> Optional[plt.Figure]:
    city_df = get_city_data(city)
    if not check_years(city_df, start_year, end_year):
        return None

    # Proceed with handling and plotting
    if city_df.empty:
        print(f"No data found for {city} during {season}.")
        return None
    city_season_data: pd.DataFrame = (
        city_df[
            (city_df['season'] == season) &
            (city_df['year'].between(start_year, end_year))
         ].groupby('year')['AverageTemperature'].mean().reset_index()
    )
    # Ensure df is populated
    if city_season_data.empty:
        print(f"No data found for {city} during {season}.")
        return None

    # Proceed with plotting
    clean_city_season_data = city_season_data.dropna(subset=['AverageTemperature', 'year'])
    slope, intercept, r_value, p_value, std_err = stats.linregress(clean_city_season_data['year'], clean_city_season_data['AverageTemperature'])
    r_squared = r_value ** 2
    fig, ax = plt.subplots(figsize=(12, 6))
    ax = sns.regplot(data=city_season_data, x='year', y='AverageTemperature', line_kws={'color': 'red'})
    stats_text = f"Slope: {slope:.4f}\n$R^2$: {r_squared:.4f}"
    if show_stats: ax.text(0.8255, 0.0288, stats_text, transform=ax.transAxes, bbox=dict(facecolor='white', alpha=1, boxstyle='square', edgecolor='black', linewidth=0.8))
    plt.title(f"{season} mean temperature: {city} ({start_year} - {end_year})")
    plt.xlabel('Year')
    plt.ylabel(f"{season} mean temp. (°C)")
    return fig

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

### Day 8 ###

def plot_city_season_kde(city: str,
                         season: str) -> Optional[plt.Figure]:
    city_data = get_city_data(city)
    if city_data.empty:
        return None

    city_season_data: pd.DataFrame = city_data[city_data['season'] == season].groupby('year')['AverageTemperature'].mean().reset_index()
    city_season_data['century'] = city_season_data['year'] // 100 + 1

    fig = plt.figure(figsize=(12, 6))
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
    return fig


### Day 10 ###

# Define function to transform data into time-series format
def prepare_time_series(df: pd.DataFrame) -> pd.DataFrame:
    ts = df.set_index('dt')['AverageTemperature'].resample('MS').mean()
    ts_df = ts.to_frame(name='AverageTemperature')
    ts_df['is_interpolated'] = ts_df['AverageTemperature'].isnull()
    ts_df['AverageTemperature'] = ts_df['AverageTemperature'].interpolate(method='linear')

    return ts_df

def plot_local_interpolation(ts_df: pd.DataFrame) -> List[plt.Figure]:
    figs = []

    gap_years = pd.DatetimeIndex(ts_df[ts_df['is_interpolated']].index).year.unique()

    for year in gap_years:
        subset = ts_df[f"{year-1}-01-01":f"{year+1}-12-31"]
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(subset.index, subset['AverageTemperature'], color = 'gray', alpha = 0.3, label = "Full series")
        ax.scatter(subset[~subset['is_interpolated']].index, subset[~subset['is_interpolated']]['AverageTemperature'], color = 'blue', alpha = 0.5, label = "Actual series")
        ax.scatter(subset[subset['is_interpolated']].index, subset[subset['is_interpolated']]['AverageTemperature'], color = 'red', alpha = 0.5, label = "Interpolated series")

        ax.set_title(f"Interpolation overview plot for {year-2}-01-01 to {year+2}-12-31")
        ax.legend()
        figs.append(fig)
    return figs

if do_ct:
    (prepare_time_series(get_city_data("Cape Town")))
    plt.show()

### Day 11 ###

def analyse_climate_components(ts_df: pd.DataFrame) -> plt.Figure:
    series = ts_df['AverageTemperature']
    decomposition = seasonal_decompose(series, model = 'additive', period = 12)

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=4, ncols=1, figsize=(12, 12), sharex=True)
    plt.suptitle(f"Climate time series decomposition", fontsize=18, fontweight='bold', y=1)

    decomposition.observed.plot(ax = ax1, color = 'blue', alpha = 0.5)
    decomposition.trend.rolling(window = 60, center = True,).mean().plot(ax = ax2, color = 'red', alpha = 0.5)
    decomposition.seasonal.plot(ax = ax3, color = 'green', alpha = 0.5)
    decomposition.resid.plot(ax = ax4, color = 'black', marker = '.', alpha = 0.5, linestyle = 'none')
    plt.tight_layout()
    return fig

analyse_climate_components(prepare_time_series(get_city_data("Cape Town")))
plt.show()