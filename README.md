# Baseball History Dashboard

A web scraping and visualization project for MLB statistics (1876–1880).

## Features
- Line plot: Average batting average over time by league.
- Bar plot: Top 10 home run leaders with a minimum home run filter.
- Scatter plot: Batting average vs. on-base percentage.
- Filters: Year (1876–1880), League (AL, NL, NA), Minimum Home Runs (0–10).

## Project Structure
- `.gitignore`: Excludes generated files (`baseball.db`, `started_csv/`, `cleaned_csv/`, logs) to keep the repository clean.
- To generate data:
  1. Run `python scrape.py` to create `started_csv/`.
  2. Run `python clean.py` to create `cleaned_csv/`.
  3. Run `python import_db.py` to create `baseball.db`.

## Running Locally
1. Clone the repository: `git clone <your-repo-url>`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the pipeline: `python scrape.py && python clean.py && python import_db.py`
4. Launch the dashboard: `streamlit run dashboard.py`
5. Open `http://localhost:8501` in your browser.