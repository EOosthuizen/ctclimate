import pandas as pd
from climate_logic import load_global_data, plot_city_season_regression, plot_city_season_kde
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

if 'view' not in st.session_state:
    st.session_state.view = 'menu'

def set_view(view_name: str):
    st.session_state.view = view_name


# Add settings bar to select country, city, and season
st.sidebar.header("Settings")
available_countries = sorted(global_df['Country'].unique())
selected_country = st.sidebar.selectbox("Select Country", available_countries)
available_cities = global_df[global_df["Country"] == selected_country]['City'].unique()
selected_city: str = str(st.sidebar.selectbox("Select City", available_cities))
city_df = global_df[global_df["City"] == selected_city]
min_year = min(city_df['year'])
max_year = max(city_df['year'])
selected_years = st.sidebar.slider("Select Year Range", min_year, max_year, value=(min_year, max_year))
start_year, end_year = selected_years
selected_season = st.sidebar.radio("Select Season", ["Summer", "Autumn", "Winter", "Spring"])
show_stats = st.sidebar.checkbox("Show Stats", value=True)

if st.session_state.view == 'menu':

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate linear regression plot"):
            set_view("reg_plot")
            st.rerun()

    with col2:
        if st.button("Generate KDE plot"):
            set_view("kde_plot")
            st.rerun()

elif st.session_state.view == "reg_plot":
    st.subheader = "Linear Regression"
    fig = plot_city_season_regression(
        city=selected_city,
        season=selected_season,
        start_year=start_year,
        end_year=end_year,
        show_stats=show_stats)
    st.pyplot(fig)

    if st.button("Back"):
        set_view("menu")
        st.rerun()

elif st.session_state.view == "kde_plot":
    st.subheader = "Density Estimate"
    fig = plot_city_season_kde(
        city=selected_city,
        season=selected_season)
    st.pyplot(fig)

    if st.button("Back"):
        set_view("menu")
        st.rerun()
# Display analysis results
