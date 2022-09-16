from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import csv
import os

from webdriver_manager.chrome import ChromeDriverManager

def main():

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'symbols.csv')
    symbols = []
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            symbols.append(row[0])
    symbols = [s.strip() for s in symbols if s.startswith('PR') or s.startswith('RP')] 
    
    options = webdriver.ChromeOptions()
    options.page_load_strategy = 'normal'
    options.add_argument('--headless')
    browser = webdriver.Chrome(options=options, executable_path=os.path.join(dirname, 'chromedriver'))

    url_trowe = 'https://www.troweprice.com/personal-investing/tools/fund-research/{}'
    browser.get(url_trowe.format('PRWBX'))
    WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'#content-summary > div.jsx-1994298159.cards-wrapper > div.jsx-1994298159.card-wrapper.mobile-order-2 > div > div > div > div.jsx-1075964365 > div.jsx-1075964365.header.withdate.border > div')))
    date = browser.find_element_by_css_selector('#content-summary > div.jsx-1994298159.cards-wrapper > div.jsx-1994298159.card-wrapper.mobile-order-2 > div > div > div > div.jsx-1075964365 > div.jsx-1075964365.header.withdate.border > div').text
    date = date[date.index('f')+2:].replace('/','-')
    
    with open('trowe_data_'+ date +'.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        final_headers = ['Ticker', 'Duration', 'Expense Ratio','SEC Yield','SEC Yield info', 'YTD', 'YTD as of', 'NAV', 'NAV as of']
        writer.writerow(final_headers)
        for symbol in symbols:   
            print(symbol) 
            browser.get(url_trowe.format(symbol))
            WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="net-asset-value"]')))
            WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="content-portfolio"]/div[2]/div[7]/div/div/div/div/div/div/table/tbody/tr[1]/td[2]')))
            WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'#content-summary > div.jsx-1994298159.cards-wrapper > div.jsx-1994298159.card-wrapper.mobile-order-2 > div > div > div > div.jsx-1075964365 > div.jsx-1075964365.header.withdate.border > div')))
            nav = browser.find_element_by_xpath('//*[@id="net-asset-value"]').text
            navAsOf = browser.find_element_by_css_selector('#content-summary > div.jsx-1994298159.cards-wrapper > div.jsx-1994298159.card-wrapper.mobile-order-2 > div > div > div > div.jsx-1075964365 > div.jsx-1075964365.header.withdate.border > div').text
            ytd = browser.find_element_by_xpath('//*[@id="average-annual-supplement"]/div[1]/table/tbody/tr[1]/td[2]').text
            ytdAsOf = browser.find_element_by_xpath('//*[@id="average-annual-supplement"]/div[1]/table/tbody/tr[1]/td[1]/div').text
            netExpRatio = browser.find_element_by_xpath('//*[@id="average-annual-supplement"]/div[1]/table/tbody/tr[4]/td[2]').text
            SECYield = browser.find_element_by_xpath('//*[@id="sec-without-waiver-row"]/td[2]').text
            SECInfo = browser.find_element_by_xpath('//*[@id="sec-without-waiver-row"]/td[1]/div').text
            duration = browser.find_element_by_xpath('//*[@id="content-portfolio"]/div[2]/div[7]/div/div/div/div/div/div/table/tbody/tr[1]/td[2]').text

            row = [symbol, duration, netExpRatio, SECYield, SECInfo, ytd, ytdAsOf[ytdAsOf.index('f') + 2:-1], nav, navAsOf[navAsOf.index('f') + 2:]]
            writer.writerow(row)
        browser.quit()
            


            
    
if __name__ == '__main__':
    main()
