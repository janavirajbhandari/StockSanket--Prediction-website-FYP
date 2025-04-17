import os
import time
import pandas as pd
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

CSV_PATH = "merolagani_news.csv"
NOTEBOOK_PATH = "stock_sentiment_score.ipynb"

def scrape_latest_news():
    print("📰 Starting Merolagani News Scraper...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 10)

    driver.get("https://merolagani.com/NewsList.aspx?catid=all")
    time.sleep(2)

    news_list = []

    seen_links = set()
    if os.path.exists(CSV_PATH):
        existing_df = pd.read_csv(CSV_PATH)
        seen_links = set(existing_df["link"])

    attempt = 0
    MAX_ATTEMPTS = 50

    while attempt < MAX_ATTEMPTS:
        news_blocks = driver.find_elements(By.CSS_SELECTOR, ".media-news")

        for block in news_blocks:
            try:
                title_el = block.find_element(By.CSS_SELECTOR, "h4.media-title a")
                link = title_el.get_attribute("href")
                if link in seen_links:
                    continue

                title = title_el.text.strip()
                date = block.find_element(By.CSS_SELECTOR, "span.media-label").text.strip()
                image_el = block.find_element(By.CSS_SELECTOR, ".media-wrap img")
                image = image_el.get_attribute("src") or ""

                news_list.append({
                    "title": title,
                    "link": link,
                    "date": date,
                    "image": image
                })
                seen_links.add(link)

            except:
                continue

        try:
            load_more = driver.find_element(By.XPATH, "//a[contains(text(),'Load More')]")
            if load_more.is_displayed():
                driver.execute_script("arguments[0].click();", load_more)
                time.sleep(1.5)
                attempt += 1
            else:
                break
        except:
            break

    driver.quit()

    if news_list:
        print(f"🆕 Found {len(news_list)} new news items.")
        df_new = pd.DataFrame(news_list)
        if os.path.exists(CSV_PATH):
            df_existing = pd.read_csv(CSV_PATH)
            df_combined = pd.concat([df_existing, df_new]).drop_duplicates(subset="link")
        else:
            df_combined = df_new

        df_combined.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
        print("✅ News CSV updated.")
    else:
        print("ℹ️ No new news to update.")

def run_sentiment_notebook():
    print("🧠 Running sentiment notebook...")
    with open(NOTEBOOK_PATH) as f:
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=600, kernel_name="python3")

    try:
        ep.preprocess(nb, {'metadata': {'path': '.'}})
        print("✅ Sentiment notebook finished.")
    except Exception as e:
        print(f"❌ Failed running sentiment notebook: {e}")

if __name__ == "__main__":
    scrape_latest_news()
    run_sentiment_notebook()
