from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
import os
import csv
import time
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

def main():

    url_vanguard = 'https://investor.vanguard.com/investment-products/mutual-funds/profile/{}'
    
    #Selectors for vanguard profiles, extracts data from characteristics table
   
    dirname = os.path.dirname(__file__)
    symbols = []
    with open(os.path.join(dirname, 'symbols.csv')) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row:
                symbols.append(row[0])
    symbols = [s.strip() for s in symbols if s.startswith('V')]    
    
    options = webdriver.ChromeOptions()
    options.page_load_strategy = 'normal'
    options.add_argument("--window-size=1025,690")
    options.add_argument('--headless')
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    
    # Selectors
    expRatio_Selector = '#Dashboard > div.container > div > div.col-md-6.col-lg-4.ml-xs-4 > dashboard-stats > div > div:nth-child(3) > div:nth-child(1) > h4'
    ytd_Selector = '#Dashboard > div.container > div > div.col-md-6.col-lg-4.ml-xs-4 > dashboard-stats > div > div:nth-child(3) > div:nth-child(2) > h4'
    ytdAsOf_Selector = '#Dashboard > div.container > div > div.col-md-6.col-lg-4.ml-xs-4 > dashboard-stats > div > div:nth-child(3) > div:nth-child(2) > p.caption.rps-grey.rps-paragraph-three.db-data-body'
    NAV_Selector = '#Dashboard > div.container > div > div.col-md-6.col-lg-4.ml-xs-4 > dashboard-stats > div > div:nth-child(4) > div:nth-child(2) > h4'
    NAVasOf_Selector = '#Dashboard > div.container > div > div.col-md-6.col-lg-4.ml-xs-4 > dashboard-stats > div > div:nth-child(4) > div:nth-child(2) > p.caption.rps-grey.rps-paragraph-three.db-data-body'
    
    secYield_Selector = '#price_section > div.ng-star-inserted > app-closing-price > div.ng-star-inserted > div > div.col-lg-4.col-sm-4.col-xs-2.col-6.ng-star-inserted > div > h4 > h4:nth-child(1)'
    secYieldAsOf_Selector = '#price_section > div.ng-star-inserted > app-closing-price > div.ng-star-inserted > div > div.col-lg-4.col-sm-4.col-xs-2.col-6.ng-star-inserted > div > h4 > p'
   
    durationTable_Selector = '#characteristics-tabset > characteristics-contianer > div > div > div > fixed-income-characteristic > div > div > table'
    
    #edge case: Duration table accessed through tab selection
    otherDuration_Selector = '#characteristics-tabset > characteristics-contianer > div > div > fixed-income-characteristic > div > div > table'
    button_Selector = '#vui-tab-2'
    portfolioComp_XPATH = './/*[@data-c11n-tab-id="portfolio-composition"]'
    characteristicsTable_Selector = '#characteristics-tabset > characteristics-contianer'
    
    with open(os.path.join(dirname, 'vanguard_fund_data_' + datetime.now().strftime('%d-%m-%Y_%H-%M') + '.csv'), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        final_headers = ['SYMBOL', 'DURATION', 'EXP RATIO', 'YTD' ,'YIELD', 'NAV', 'YTD as of', 'SEC YIELD info','NAV as of']
        writer.writerow(final_headers)
        for s in symbols:
            browser.get(url_vanguard.format(s.lower()))
            WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, expRatio_Selector)))
            expRatio = browser.find_element(by=By.CSS_SELECTOR, value=expRatio_Selector).text
            ytd = browser.find_element(by=By.CSS_SELECTOR, value=ytd_Selector).text
            ytdAsOf = browser.find_element(by=By.CSS_SELECTOR, value=ytdAsOf_Selector).text
            NAV = browser.find_element(by=By.CSS_SELECTOR, value=NAV_Selector).text
            NAVasOf = browser.find_element(by=By.CSS_SELECTOR, value=NAVasOf_Selector).text
            
            try:
                secYield = browser.find_element(by=By.CSS_SELECTOR, value=secYield_Selector).text
                secYieldAsOf = browser.find_element(by=By.CSS_SELECTOR, value=secYieldAsOf_Selector).text
            except NoSuchElementException:
                secYield = 'NA'
                secYieldAsOf = 'NA'

            try:
                durationTable = browser.find_element(by=By.CSS_SELECTOR, value=durationTable_Selector)
            except NoSuchElementException:
                
                try:
                    browser.execute_script("arguments[0].scrollIntoView(true);", browser.find_element(by=By.CSS_SELECTOR, value=characteristicsTable_Selector))
                    time.sleep(1)
                    browser.find_element(by=By.XPATH, value=portfolioComp_XPATH).click()
                    time.sleep(1.5)
                except ElementClickInterceptedException:
                    browser.execute_script("arguments[0].scrollIntoView(true);", browser.find_element(by=By.CSS_SELECTOR, value=characteristicsTable_Selector))
                    time.sleep(1)
                    browser.find_element(by=By.XPATH, value=portfolioComp_XPATH).click()
                    time.sleep(1.5)
                
                attempts = 0
                while(attempts < 4):
                    try:
                        browser.find_element(by=By.CSS_SELECTOR, value=button_Selector).click()
                        break
                    except ElementClickInterceptedException:
                        browser.find_element(by=By.XPATH, value=portfolioComp_XPATH).click()
                        time.sleep(1.5)
                        attempts += 1
                    except NoSuchElementException:
                        browser.find_element(by=By.XPATH, value=portfolioComp_XPATH).click()
                        time.sleep(1.5)
                        browser.find_element(by=By.CSS_SELECTOR, value=button_Selector+'8').click()
                WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, otherDuration_Selector)))
                durationTable = browser.find_element(by=By.CSS_SELECTOR, value=otherDuration_Selector)
                
                
            
            avgDuration = 'NA'
            durRows = durationTable.find_elements(by=By.TAG_NAME, value = 'tr')
            
            for row in durRows[1:]:
                cols = row.find_elements(by=By.TAG_NAME, value='td')
                if(cols[0].text == 'Average duration'):
                    averageDuration = cols[1].text
                    break
            writer.writerow([s, averageDuration, expRatio, ytd, secYield, NAV, ytdAsOf, secYieldAsOf, NAVasOf])
                    
            print(s, 'complete\n')

        
if __name__ == '__main__':
    main()
