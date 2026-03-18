# Import libraries and assign aliases for quick reference
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np

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

print(season_trends(climate_df = ct_df, season = 'Winter', decades_timespan = 5))
print(season_trends(climate_df = ct_df, season = 'Winter', decades_timespan = 10))
print(season_trends(climate_df = ct_df, season = 'Summer', decades_timespan = 10))

### Day 4 ###

# Configure seaborn and plot winter temperature regression
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
plt.show()

### Day 5 ###

# Calculate regression statistics
slope, intercept, r_value, p_value, std_err = stats.linregress(
    winter_data_five_decades['year'],
    winter_data_five_decades['AverageTemperature']
)
r_squared = r_value ** 2
#stats_text = f'Slope: {slope:.4f} °C/year\n$R^2$: {r_squared:.4f}\np-value: {p_value:.4f}' #
#print(stats_text)

# Create annotated regression plot function
def plot_climate_trend(climate_df: pd.DataFrame,
                       plot_title: str,
                       x_lab: str,
                       y_lab: str,
                       slope_val: float,
                       r2_val: float
                       ) -> None:
    plt.figure(figsize=(12, 6))
    ax = sns.regplot(data=climate_df, x='year', y='AverageTemperature', line_kws={'color': 'red'})
    stats_text = f"Slope: {slope_val:.4f}\n$R^2$: {r2_val:.4f}"
    ax.text(0.8255, 0.0288, stats_text, transform=ax.transAxes, bbox=dict(facecolor='white', alpha=1, boxstyle='square', edgecolor='black', linewidth=0.8))
    plt.title(plot_title)
    plt.xlabel(x_lab)
    plt.ylabel(y_lab)
    plt.show()

# Create plot annotated with regression statistics
title = 'Cape Town: winter warming trend (last 50 years)'
x_label = 'Year'
y_label = 'Average winter temp (°C)'
plot_climate_trend(winter_data_five_decades, title, x_label, y_label, slope, r_squared)

### Day 6 ###

# Add century label to data (3 different approaches)
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
print(winter_data.head(), winter_data.tail()) # inspect labels

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
plt.show()

