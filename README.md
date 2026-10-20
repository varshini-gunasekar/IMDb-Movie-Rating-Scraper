# IMDb Movie Rating Scraper

A Python project using Selenium, Chrome WebDriver, and pandas to collect IMDb Top 250 movie details and save them to CSV.

## Run
1. Extract the ZIP.
2. Open this folder in VS Code.
3. In the terminal, run:
   `python -m pip install -r requirements.txt`
4. Run:
   `python imdb_scraper.py`

The scraper first tries IMDb live. If IMDb presents a Human Verification page or live scraping fails, it downloads a publicly available historical dataset and creates `imdb_top250.csv` with Rank, Movie Name, Year, and IMDb Rating. The fallback is historical data and must not be described as live scraping.

## Technologies
Python, Selenium, Chrome WebDriver, webdriver-manager, pandas, CSV.

## Aim
To automate the collection of movie ranking, title, release year, and IMDb rating, and store the data in CSV format.

## Algorithm
1. Import the required libraries.
2. Configure Chrome WebDriver.
3. Open IMDb Top 250 and wait for the page to load.
4. Extract movie rank, title, year, and rating if the page is accessible.
5. If IMDb verification blocks access, load the public historical dataset instead.
6. Select the required columns and save them to `imdb_top250.csv`.
7. Close the browser.

## Note
IMDb may restrict automated requests or change its page structure. The fallback dataset is a previously collected snapshot and may not reflect current rankings or ratings.
