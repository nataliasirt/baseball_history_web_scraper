import sqlite3
import pandas as pd
import logging

logging.basicConfig(filename="query.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_connection(db_name):
    try:
        return sqlite3.connect(db_name)
    except sqlite3.Error as e:
        logging.error(f"Error connecting to DB: {e}")
        return None

def show_menu():
    print("""
    === Baseball Analytics Menu ===
    1. Top 5 Batting Average by Year
    2. Most Productive Players (HR + RBI + Hits)
    3. Average On-Base % by League
    4. Team Performance by Year
    5. High Slugging & OBP Players
    6. Custom SQL Query
    0. Exit
    """)

def format_results(df):
    if df.empty:
        print("No results found.")
    else:
        print(df.to_string(index=False))

def top_batting_average_by_year(conn, year):
    query = """
        SELECT Player, Team, batting_average
        FROM batting_average
        WHERE Year = ?
        ORDER BY batting_average DESC
        LIMIT 5
    """
    df = pd.read_sql_query(query, conn, params=(year,))
    print(f"\nTop 5 Batting Averages in {year}")
    format_results(df)

def most_productive_players(conn):
    query = """
        SELECT hr.Player, hr.Team, hr.home_runs, rbi.rbi, hits.hits
        FROM home_runs hr
        JOIN rbi ON hr.Year = rbi.Year AND hr.Player = rbi.Player
        JOIN hits ON hr.Year = hits.Year AND hr.Player = hits.Player
        ORDER BY (hr.home_runs + rbi.rbi + hits.hits) DESC
        LIMIT 10
    """
    df = pd.read_sql_query(query, conn)
    print("\nMost Productive Players (HR + RBI + Hits)")
    format_results(df)

def average_on_base_by_league(conn):
    query = """
        SELECT League, ROUND(AVG(on_base_percentage), 3) as avg_obp
        FROM on_base_percentage
        GROUP BY League
        ORDER BY avg_obp DESC
    """
    df = pd.read_sql_query(query, conn)
    print("\nAverage OBP by League")
    format_results(df)

def team_performance_by_year(conn, year):
    query = """
        SELECT runs.Team, SUM(runs.runs) as total_runs,
               SUM(rbi.rbi) as total_rbi, SUM(hr.home_runs) as total_home_runs
        FROM runs
        JOIN rbi ON runs.Year = rbi.Year AND runs.Player = rbi.Player
        JOIN home_runs hr ON runs.Year = hr.Year AND runs.Player = hr.Player
        WHERE runs.Year = ?
        GROUP BY runs.Team
        ORDER BY total_runs DESC
    """
    df = pd.read_sql_query(query, conn, params=(year,))
    print(f"\nTeam Performance in {year}")
    format_results(df)

def high_slugging_and_onbase(conn, year=None, league=None, player=None):
    query = """
        SELECT sa.Player, sa.Team, sa.slugging_average, obp.on_base_percentage, sa.Year, sa.League
        FROM slugging_average sa
        JOIN on_base_percentage obp ON sa.Year = obp.Year AND sa.Player = obp.Player
        WHERE sa.slugging_average > 0.5 AND obp.on_base_percentage > 0.4
    """
    params = []
    if year:
        query += " AND sa.Year = ?"
        params.append(year)
    if league:
        query += " AND sa.League = ?"
        params.append(league.upper())
    if player:
        query += " AND sa.Player LIKE ?"
        params.append(f"%{player}%")
    
    df = pd.read_sql_query(query, conn, params=params)
    print("\nPlayers with Slugging > 0.5 and OBP > 0.4")
    format_results(df)

def custom_query(conn, query):
    try:
        df = pd.read_sql_query(query, conn)
        print("\nCustom Query Results")
        format_results(df)
    except Exception as e:
        logging.error(f"Custom query error: {e}")
        print(f"Error: {e}")

def main():
    conn = get_connection("baseball.db")
    if not conn:
        return
    
    while True:
        show_menu()
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            year = input("Enter year: ").strip()
            top_batting_average_by_year(conn, year)
        elif choice == "2":
            most_productive_players(conn)
        elif choice == "3":
            average_on_base_by_league(conn)
        elif choice == "4":
            year = input("Enter year: ").strip()
            team_performance_by_year(conn, year)
        elif choice == "5":
            year = input("Enter year (optional): ").strip() or None
            league = input("Enter league (AL/NL, optional): ").strip() or None
            player = input("Enter player (optional): ").strip() or None
            high_slugging_and_onbase(conn, year, league, player)
        elif choice == "6":
            query = input("Enter SQL query: ").strip()
            custom_query(conn, query)
        elif choice == "0":
            break
        else:
            print("Invalid choice.")
    
    conn.close()

if __name__ == "__main__":
    main()