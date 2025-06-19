import csv
import os
import logging
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup logging
logging.basicConfig(filename="scraper.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124")
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

def get_metric_links(driver, url):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ba-table table.boxed")))
    first_table = driver.find_elements(By.CSS_SELECTOR, "div.ba-table table.boxed")[0]
    stat_cells = first_table.find_elements(By.CSS_SELECTOR, "td.datacolBlue a")
    return [(cell.text.strip(), cell.get_attribute("href")) for cell in stat_cells]

def scrape_table(driver, metric_name, url, output_folder):
    filename = metric_name.lower().replace(" ", "_") + ".csv"
    file_path = os.path.join(output_folder, filename)
    if os.path.exists(file_path):
        logging.info(f"Skipping {filename}: File exists")
        return
    
    logging.info(f"Scraping: {metric_name} from {url}")
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ba-table table.boxed")))
    
    data = []
    while True:
        tables = driver.find_elements(By.CSS_SELECTOR, "div.ba-table table.boxed")
        for table in tables:
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 8:
                        year_al = cells[0].text.strip()
                        player_al = cells[1].text.strip()
                        stat_al = cells[2].text.strip().split()[0]
                        team_al = cells[3].text.strip()
                        year_nl = cells[4].text.strip()
                        player_nl = cells[5].text.strip()
                        stat_nl = cells[6].text.strip().split()[0]
                        team_nl = cells[7].text.strip()
                        if year_al.isdigit() and year_nl.isdigit():
                            data.append([year_al, "AL", player_al, team_al, stat_al])
                            data.append([year_nl, "NL", player_nl, team_nl, stat_nl])
                except Exception as e:
                    logging.warning(f"Skipped row in {metric_name}: {e}")
        
        try:
            next_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Next')]")
            if next_button.is_enabled():
                next_button.click()
                WebDriverWait(driver, 10).until(EC.staleness_of(tables[0]))
                time.sleep(random.uniform(1, 3))  # Random delay to avoid blocks
            else:
                break
        except:
            break
    
    if data:
        os.makedirs(output_folder, exist_ok=True)
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Year", "League", "Player", "Team", metric_name])
            writer.writerows(data)
        logging.info(f"Saved: {filename}")

def main():
    output_folder = "started_csv"
    driver = setup_driver()
    years = range(1901, 1904)  # Expand as needed
    base_url = "https://www.baseball-almanac.com/yearly/yr{}a.shtml"
    
    try:
        for year in years:
            url = base_url.format(year)
            logging.info(f"Processing year: {year}")
            links_and_texts = get_metric_links(driver, url)
            for name, link in links_and_texts:
                scrape_table(driver, name, link, output_folder)
    finally:
        driver.quit()
        logging.info("Driver closed")

if __name__ == "__main__":
    main()