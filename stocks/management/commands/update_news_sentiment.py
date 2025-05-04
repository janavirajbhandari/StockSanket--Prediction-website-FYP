from django.core.management.base import BaseCommand
from stocks.models import Stock

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
from webdriver_manager.chrome import ChromeDriverManager
from deep_translator import GoogleTranslator


def dismiss_alert_if_present(driver):
    try:
        alert = driver.switch_to.alert
        print("⚠️ Dismissing unexpected alert...")
        alert.dismiss()
        time.sleep(1)
    except NoAlertPresentException:
        pass


class Command(BaseCommand):
    help = "Scrape latest news from merolagani.com and update sentiment data."

    def handle(self, *args, **kwargs):
        NEWS_FILE = "merolagani_news.csv"
        SENTIMENT_FILE = "stock_sentiment_news.csv"

        # Load already scraped titles
        existing_titles = set()
        if os.path.exists(NEWS_FILE):
            existing_titles = set(pd.read_csv(NEWS_FILE)["title"].dropna().tolist())

        # Get all company names
        company_names = list(Stock.objects.values_list("company_name", flat=True))

        # Setup Selenium
        options = Options()
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://merolagani.com/NewsList.aspx?catid=all")
        time.sleep(2)
        dismiss_alert_if_present(driver)

        # Scrape loop
        all_news = []
        new_titles = set()
        load_attempts = 0
        MAX_ATTEMPTS = 50

        while True:
            news_cards = driver.find_elements(By.CSS_SELECTOR, ".media-news")
            previous_count = len(news_cards)

            for card in news_cards:
                try:
                    title_el = card.find_element(By.CSS_SELECTOR, "h4.media-title a")
                    title = title_el.text.strip()

                    if title in existing_titles or title in new_titles:
                        continue

                    link = title_el.get_attribute("href")
                    date = card.find_element(By.CSS_SELECTOR, "span.media-label").text.strip()
                    image = card.find_element(By.CSS_SELECTOR, ".media-wrap img").get_attribute("src")

                    all_news.append({
                        "title": title,
                        "link": link,
                        "date": date,
                        "image": image
                    })
                    new_titles.add(title)

                except Exception:
                    continue

            try:
                load_more = driver.find_element(By.XPATH, "//a[contains(text(),'Load More')]")
                if load_more.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView(true);", load_more)
                    driver.execute_script("arguments[0].click();", load_more)
                    dismiss_alert_if_present(driver)
                    print("🔁 Clicked 'Load More'")
                    time.sleep(2)

                    retries = 0
                    while retries < 5:
                        current_count = len(driver.find_elements(By.CSS_SELECTOR, ".media-news"))
                        if current_count > previous_count:
                            break
                        time.sleep(1)
                        retries += 1

                    load_attempts += 1
                    if load_attempts >= MAX_ATTEMPTS:
                        print("⚠️ Max 'Load More' attempts reached.")
                        break
                else:
                    print("⛔ 'Load More' not visible anymore.")
                    break
            except NoSuchElementException:
                print("⚠️ 'Load More' button not found or no longer available.")
                break

        driver.quit()

        # Save merolagani_news.csv
        if all_news:
            new_df = pd.DataFrame(all_news)
            if os.path.exists(NEWS_FILE):
                old_df = pd.read_csv(NEWS_FILE)
                combined_df = pd.concat([old_df, new_df], ignore_index=True).drop_duplicates(subset="title")
            else:
                combined_df = new_df
            combined_df.to_csv(NEWS_FILE, index=False, encoding="utf-8-sig")
            self.stdout.write(f"✅ {len(new_df)} new news items saved to merolagani_news.csv")
        else:
            self.stdout.write("📬 No new news to append.")

        # Translate & store stock-related news
        sentiment_news = []
        for news in all_news:
            try:
                translated = GoogleTranslator(source='auto', target='en').translate(news["title"])
                for company in company_names:
                    if company.lower() in translated.lower():
                        sentiment_news.append({
                            "original": news["title"],
                            "translated": translated,
                            "company": company,
                            "link": news["link"],
                            "date": news["date"],
                            "image": news["image"]
                        })
                        break
            except Exception:
                continue

        # Save stock_sentiment_news.csv
        if sentiment_news:
            sentiment_df = pd.DataFrame(sentiment_news)
            if os.path.exists(SENTIMENT_FILE):
                old_sent = pd.read_csv(SENTIMENT_FILE)
                combined_sent = pd.concat([old_sent, sentiment_df], ignore_index=True).drop_duplicates(subset="translated")
            else:
                combined_sent = sentiment_df
            combined_sent.to_csv(SENTIMENT_FILE, index=False, encoding="utf-8-sig")
            self.stdout.write(f"✅ {len(sentiment_df)} stock-related news saved to stock_sentiment_news.csv")
        else:
            self.stdout.write("📬 No stock-related news found.")
