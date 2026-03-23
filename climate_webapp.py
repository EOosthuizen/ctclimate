import pandas as pd
from climate_logic import load_global_data, plot_city_season_regression
import streamlit as st

### Day 9 ###

# Implement a web interface
st.title("Global Climate Explorer")

# Load and cache dataset so it doesn't get re-loaded with every user input
@st.cache_data
def load_cache_global_data() -> pd.DataFrame:
    df = load_global_data()
    return df

global_df = load_cache_global_data()

# Add settings bar to select country, city, and season
st.sidebar.header("Settings")
selected_country = st.sidebar.selectbox("Select Country", global_df['Country'].unique())
available_cities = global_df[global_df["Country"] == selected_country]['City'].unique()
selected_city: str = str(st.sidebar.selectbox("Select City", available_cities))
city_df = global_df[global_df["City"] == selected_city]
min_year = min(city_df['year'])
max_year = max(city_df['year'])
selected_years = st.sidebar.slider("Select Year Range", min_year, max_year, value=(min_year, max_year))
start_year, end_year = selected_years
selected_season = st.sidebar.radio("Select Season", ["Summer", "Autumn", "Winter", "Spring"])
show_stats = st.sidebar.checkbox("Show Stats", value=True)

# Display analysis results
st.subheader(f"Climate Explorer results for {selected_city}, {selected_country}: {selected_season}")
if st.button("Generate linear regression plot"):
    fig = plot_city_season_regression(
        city=selected_city,
        season=selected_season,
        start_year=start_year,
        end_year=end_year,
        show_stats=show_stats)
    st.pyplot(fig)