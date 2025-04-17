from django.core.management.base import BaseCommand
from stocks.models import Stock
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

class Command(BaseCommand):
    help = "Auto-fetches and updates NEPSE company_id for stocks."

    def handle(self, *args, **options):
        base_url = "https://www.nepalstock.com/"
        chrome_driver_path = r"C:\Users\Bishal\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
        stocks = Stock.objects.filter(company_id__isnull=True)

        for stock in stocks:
            try:
                chrome_options = Options()
                # Comment this out for debugging
                # chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--no-sandbox")

                service = Service(executable_path=chrome_driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)

                self.stdout.write(f"🔍 Searching for: {stock.symbol}")
                driver.get(base_url)

                wait = WebDriverWait(driver, 10)
                search_box = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[placeholder*="Symbol or Company Name"]')
                ))

                search_box.click()
                search_box.clear()
                search_box.send_keys(stock.symbol)
                time.sleep(1)

                # Wait and click first dropdown suggestion
                dropdown_item = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".dropdown-item")
                ))
                driver.execute_script("arguments[0].click();", dropdown_item)

                # Wait for redirect
                wait.until(lambda d: "/company/detail/" in d.current_url)
                current_url = driver.current_url

                match = re.search(r"/company/detail/(\d+)", current_url)
                if match:
                    company_id = int(match.group(1))
                    stock.company_id = company_id
                    stock.save()
                    self.stdout.write(self.style.SUCCESS(f"✅ {stock.symbol} → ID: {company_id}"))
                else:
                    self.stdout.write(self.style.WARNING(f"❌ No ID found in URL for {stock.symbol}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error for {stock.symbol}: {e}"))

            finally:
                # Close the driver after each symbol
                driver.quit()

        self.stdout.write(self.style.SUCCESS("🎉 Finished updating all company IDs!"))
