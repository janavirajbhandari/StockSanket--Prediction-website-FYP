import time
import pandas as pd
import bs4 as BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# ✅ Point this to your local chromedriver.exe
CHROMEDRIVER_PATH = r"C:\Users\Bishal\Desktop\Final Project\chromedriver.exe"

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
options.add_experimental_option('excludeSwitches', ['enable-logging'])

BASE_URL = "https://www.sharesansar.com/"

class NepseData:
    def __init__(self, scripts: str):
        self.scripts = scripts

    def price_history(self):
        driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
        driver.get(BASE_URL)
        time.sleep(2)

        driver.find_element('xpath', "//input[@placeholder='Company Name or Symbol']").send_keys(self.scripts)
        time.sleep(2)
        driver.find_element('xpath', f"//b[text() ='{self.scripts.upper()}']").click()
        time.sleep(2)
        driver.find_element('xpath', "//a[text()='Price History']").click()
        time.sleep(2)
        driver.find_element('xpath', "//option[text()='50']").click()
        time.sleep(2)

        final_df = pd.DataFrame()
        for _ in range(0, 60):
            HTMLPage = BeautifulSoup.BeautifulSoup(driver.page_source, 'html.parser')
            Table = HTMLPage.find('table', class_='table table-hover table-striped table-bordered compact dataTable no-footer')
            if not Table:
                break
            Rows = Table.find_all('tr', role="row")
            extracted_data = []
            for i in range(1, len(Rows)):
                try:
                    RowDict = {}
                    Values = Rows[i].find_all('td')
                    if len(Values) == 9:
                        RowDict["Date"] = Values[1].text.strip()
                        RowDict["Open"] = Values[2].text.strip()
                        RowDict["High"] = Values[3].text.strip()
                        RowDict["Low"] = Values[4].text.strip()
                        RowDict["Close"] = Values[5].text.strip()
                        RowDict["% change"] = Values[6].text.strip()
                        RowDict["Volume"] = Values[7].text.strip()
                        RowDict["TurnOver"] = Values[8].text.strip()
                        extracted_data.append(RowDict)
                except Exception:
                    continue
            extracted_data = pd.DataFrame(extracted_data)
            final_df = pd.concat([final_df, extracted_data], ignore_index=True)
            try:
                driver.find_element('xpath', "//a[text()='Next']").click()
            except Exception:
                break
            time.sleep(2)

        driver.quit()
        return final_df
