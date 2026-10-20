
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# -------------------- SAVE DATASET --------------------

def save_from_public_dataset():
    print("\nLoading public IMDb Top 250 dataset...")

    df = pd.read_csv(PUBLIC_DATASET_URL)

    df = df.rename(columns={
        "rank": "Rank",
        "name": "Movie Name",
        "year": "Year",
        "imdb_rating": "IMDb Rating"
    })

    required_columns = [
        "Rank", "Movie Name", "Year", "IMDb Rating"
    ]

    missing_columns = [
        col for col in required_columns if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing dataset columns: {missing_columns}"
        )

    df = df[required_columns].head(250)

    df.to_csv(
        "imdb_top250.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"CSV created successfully: {len(df)} movies")
    print("Source: Previously collected public dataset")
    print("\nFirst 10 movies:")
    print(df.head(10).to_string(index=False))


# -------------------- LIVE IMDb SCRAPER --------------------

def main():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1365,900")

    driver = None

    try:
        print("Connecting to IMDb Top 250...")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        driver.get(IMDB_URL)
        time.sleep(6)

        print("Page title:", driver.title)

        movies = driver.find_elements(
            By.CSS_SELECTOR,
            "li.ipc-metadata-list-summary-item"
        )

        rows = []

        for movie in movies:
            try:
                heading = movie.find_element(
                    By.CSS_SELECTOR, "h3"
                ).text.strip()

                rank = len(rows) + 1
                title = heading

                if ". " in heading:
                    first, rest = heading.split(". ", 1)

                    if first.isdigit():
                        rank = int(first)
                        title = rest

                metadata = movie.find_elements(
                    By.CSS_SELECTOR,
                    ".cli-title-metadata-item"
                )

                year = metadata[0].text if metadata else "N/A"

                ratings = movie.find_elements(
                    By.CSS_SELECTOR,
                    ".ipc-rating-star--rating"
                )

                rating = ratings[0].text if ratings else "N/A"

                rows.append({
                    "Rank": rank,
                    "Movie Name": title,
                    "Year": year,
                    "IMDb Rating": rating
                })

            except Exception:
                continue

        if rows:
            df = pd.DataFrame(rows).head(250)

            df.to_csv(
                "imdb_top250.csv",
                index=False,
                encoding="utf-8-sig"
            )

            print(f"\nLive scraping completed: {len(df)} movies saved.")
            print("\nFirst 10 movies:")
            print(df.head(10).to_string(index=False))

        else:
            print("IMDb data unavailable or blocked.")
            print("Trying the public dataset fallback...")
            save_from_public_dataset()

    except Exception as error:
        print("\nLive scraping failed:", error)
        print("Trying the public dataset fallback...")

        try:
            save_from_public_dataset()

        except Exception as fallback_error:
            print("\nDataset fallback failed:", fallback_error)
            print("Please check your internet connection and dataset URL.")

    finally:
        if driver is not None:
            driver.quit()

    print("\nProject execution finished.")


# -------------------- URL CONFIGURATION --------------------

IMDB_URL = "https://www.imdb.com/chart/top/"

PUBLIC_DATASET_URL = (
    "https://raw.githubusercontent.com/"
    "AshishJangra27/datasets/main/"
    "IMDB%20Movies/Top%20250.csv"
)


if __name__ == "__main__":
    main()
