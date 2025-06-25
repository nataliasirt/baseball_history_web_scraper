import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Major League Baseball History Dashboard", layout="wide")
st.title("Major League Baseball History Dashboard")

@st.cache_data
def load_data(query, params=()):
    try:
        conn = sqlite3.connect("baseball.db")
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Sidebar filters
year = st.sidebar.selectbox("Select Year", options=["All Years"] + list(range(1901, 2025)), index=0)
league = st.sidebar.selectbox("Select League", options=["All Leagues", "AL", "NL"], index=0)

# Helper function to create dynamic titles
def create_title(base_title, year, league):
    title = base_title
    if year != "All Years":
        title += f" in {year}"
    if league != "All Leagues":
        title += f" ({league})"
    return title

# Visualization 1: Batting Average Trends
query = "SELECT CAST(Year AS INTEGER) as Year, League, AVG(batting_average) as avg_ba FROM batting_average"
params = []
if year != "All Years":
    query += " WHERE CAST(Year AS INTEGER) = ?"
    params = (year,)
if league != "All Leagues":
    query += " AND League = ?" if "WHERE" in query else " WHERE League = ?"
    params += (league,)
query += " GROUP BY Year, League"
df_ba = load_data(query, params)

if not df_ba.empty:
    title = create_title("Batting Average National League vs American League", year, league)
    fig1 = px.line(df_ba, x="Year", y="avg_ba", color="League", title=title)
    fig1.update_layout(yaxis_title="Average Batting")
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.warning("No batting average data available for the selected filters.")

# Visualization 2: Home Run Hitters
query = "SELECT Player, Team, home_runs, Year, League FROM home_runs"
params = []
if year != "All Years":
    query += " WHERE CAST(Year AS INTEGER) = ?"
    params = (year,)
if league != "All Leagues":
    query += " AND League = ?" if "WHERE" in query else " WHERE League = ?"
    params += (league,)
query += " ORDER BY home_runs DESC"
if year == "All Years":
    query += " LIMIT 10"
else:
    query += " LIMIT 5"  # Show up to 5 players when a specific year is selected
df_hr = load_data(query, params)

if not df_hr.empty:
    title = create_title("Top Home Run Hitters", year, league)
    fig2 = px.bar(df_hr, x="home_runs", y="Player", color="Team", title=title, orientation='h')
    fig2.update_layout(xaxis_title="Home Runs", bargap=0.10, height=500)
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No home run data available for the selected filters.")

# Visualization 3: Hit Leaders
query = "SELECT Player, Team, hits, Year, League FROM hits"
params = []
if year != "All Years":
    query += " WHERE CAST(Year AS INTEGER) = ?"
    params.append(year)
if league != "All Leagues":
    query += " AND League = ?" if "WHERE" in query else " WHERE League = ?"
    params.append(league)
query += " ORDER BY hits DESC"
if year == "All Years":
    query += " LIMIT 10"
else:
    query += " LIMIT 5"  # Show up to 5 players when a specific year is selected
df_hits = load_data(query, params)

if not df_hits.empty:
    title = create_title("Top Hit Leaders", year, league)
    fig3 = px.bar(df_hits, x="Player", y="hits", color="Team", title=title)
    fig3.update_layout(yaxis_title="Hits")
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("No hits data available for the selected filters.")

# Data Table
st.subheader("Filtered Data")
if not df_hits.empty:
    st.dataframe(df_hits)
else:
    st.warning("No data available to display.")