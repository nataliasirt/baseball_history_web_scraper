import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.set_page_config(page_title="MLB History Dashboard", layout="wide")
st.title("MLB History Dashboard (1876–1880)")

def load_data(query, params=()):
    try:
        if not os.path.exists("baseball.db"):
            st.error("Error: baseball.db not found. Run scrape.py, clean.py, and import_db.py first.")
            return pd.DataFrame()
        conn = sqlite3.connect("baseball.db")
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        if df.empty:
            st.warning(f"No data returned for query: {query}")
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

def get_years():
    try:
        df = load_data("SELECT DISTINCT Year FROM batting_average")
        return sorted(df["Year"].dropna().astype(int).tolist()) if not df.empty else [1876, 1877, 1878, 1879, 1880]
    except:
        return [1876, 1877, 1878, 1879, 1880]

st.sidebar.header("Filters")
years = get_years()
year = st.sidebar.selectbox("Select Year", options=[None] + years, index=0)
league = st.sidebar.selectbox("Select League", options=[None, "AL", "NL", "NA"], index=0)  # Added NA
min_home_runs = st.sidebar.slider("Minimum Home Runs", 0, 10, 2)  # Adjusted max to 10

# Visualization 1: Line Plot of Average Batting Average Over Time
st.subheader("Average Batting Average Over Time")
query = "SELECT Year, League, AVG(batting_average) as avg_ba FROM batting_average"
params = []
if year:
    query += " WHERE Year = ?"
    params.append(year)
if league:
    query += " AND League = ?" if "WHERE" in query else " WHERE League = ?"
    params.append(league)
query += " GROUP BY Year, League"
df_ba = load_data(query, params)

if not df_ba.empty:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=df_ba, x="Year", y="avg_ba", hue="League", marker="o", ax=ax)
    ax.set_title("Average Batting Average Over Time")
    ax.set_xlabel("Year")
    ax.set_ylabel("Average Batting Average")
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.warning("No batting average data available. Check database tables.")

# Visualization 2: Bar Plot of Top Home Run Hitters
st.subheader("Top 10 Home Run Leaders")
query = f"SELECT Player, Team, home_runs, Year, League FROM home_runs WHERE home_runs >= {min_home_runs}"
params = []
if year:
    query += " AND Year = ?"
    params.append(year)
if league:
    query += " AND League = ?"
    params.append(league)
query += " ORDER BY home_runs DESC LIMIT 10"
df_hr = load_data(query, params)

if not df_hr.empty:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df_hr, x="home_runs", y="Player", hue="Team", ax=ax)
    ax.set_title(f"Top 10 Home Run Leaders (Min {min_home_runs} HR)")
    ax.set_xlabel("Home Runs")
    ax.set_ylabel("Player")
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.warning("No home run data available. Check database tables or adjust filters.")

# Visualization 3: Scatter Plot of Batting Average vs. On-Base Percentage
st.subheader("Batting Average vs. On-Base Percentage")
query = """
    SELECT ba.Player, ba.Team, ba.batting_average, obp.on_base_percentage, ba.Year, ba.League
    FROM batting_average ba
    JOIN on_base_percentage obp ON ba.Year = obp.Year AND ba.Player = obp.Player
"""
params = []
if year:
    query += " WHERE ba.Year = ?"
    params.append(year)
if league:
    query += " AND ba.League = ?" if "WHERE" in query else " WHERE ba.League = ?"
    params.append(league)
df_scatter = load_data(query, params)

if not df_scatter.empty:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df_scatter, x="batting_average", y="on_base_percentage", hue="League", size="Year", ax=ax)
    ax.set_title("Batting Average vs. On-Base Percentage")
    ax.set_xlabel("Batting Average")
    ax.set_ylabel("On-Base Percentage")
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.warning("No batting average or on-base percentage data available. Check database tables.")

# Data Table
st.subheader("Filtered Data")
if not df_scatter.empty:
    st.dataframe(df_scatter)
else:
    st.warning("No data to display in table.")