from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import os
import csv

def extractOverviewTable(htmlTable):
    table = htmlTable.find('tbody')
    rows = table.findAll('tr')
    returnDict = {}
    for row in rows:
        cols = row.findAll('td')
        key = cols[0].find('span').text.replace('\n', '')
        value = cols[1].text.replace('\n', '')
        if 'Layer' in key:
            key = key[:key.index('Layer')] 
        returnDict[key] = value
        
    return returnDict
    

def extractReturnsTable(htmlTable):
    table = htmlTable.findAll('tbody')
    rowData = []
    dataDict = {}
    for row in table[1:]:
        rowEntry = row.find('tr',{'class':'productEntry'})
        cols = rowEntry.findAll('td')
        rowData = [c.text.strip().replace('\n', '').replace('\t', '').replace(',', '') for c in cols[1:]]
        if '%' in rowData[7]:
            rowData[7] = rowData[7].replace('A', '').replace('J', '').replace('B', '').replace('C', '').replace('G', '')
            rowData.append(rowData[7][rowData[7].index('%') + 1:])
            rowData[-1] = rowData[-1][:rowData[-1].index('y') + 1] + " " + rowData[-1][rowData[-1].index('y') + 1:]
            rowData[7] = rowData[7][:rowData[7].index('%') + 1]
            
        dataDict[rowData[1]] = rowData[1:]
    return dataDict

def main():

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
    options.add_argument('--headless')
    browser = webdriver.Chrome(options=options, executable_path=os.path.join(dirname, 'chromedriver'))
    symbol = 'vbirx'
    url_vanguard = 'https://investor.vanguard.com/mutual-funds/profile/overview/{}'
    url_vanguardReturns = 'https://investor.vanguard.com/mutual-funds/list#/mutual-funds/asset-class/month-end-returns'
    
    # Scrape Data from Vanguard month-end-returns table
    browser.get(url_vanguardReturns)
    # wait until the data table loads in on the page
    WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div[3]/div[3]/div[1]/div/div[1]/div[2]/div[6]/div[2]/div[2]/div/table')))
    html = browser.page_source
    mySoup = BeautifulSoup(html, 'html.parser')
    htmlData = mySoup.findAll('div',{'class':'scrollingTables'})
    htmlDataTable = htmlData[-1].find('table')
    # returnsTableDict: key -> String: ticker, returns -> list: data
    returnsTableDict = extractReturnsTable(htmlDataTable)
    htmlHeaders = htmlData[0].find('thead').findAll('tr')
    
    returnsTableHeaders = []
    for headerRow in htmlHeaders:
        headerRow = headerRow.findAll('th')
        headers = []
        for header in headerRow:
            text = header.find('span').text
            text = text[:text.index('\xa0')] if '\xa0' in text else text
            headers.append(text)
        returnsTableHeaders.append(headers)
        date = returnsTableHeaders[0][4][returnsTableHeaders[0][4].index('f') + 2:].replace('/','-')
    with open(os.path.join(dirname, 'vanguard_fund_data_'+ date +'.csv'), 'w') as csvfile:
        writer = csv.writer(csvfile)
        final_headers = ['Ticker', 'Duration', 'Expense Ratio','SEC Yield','SEC Yield info', returnsTableHeaders[0][4],'YTD ' + returnsTableHeaders[0][6].lower()]
        writer.writerow(final_headers)
        overviewDataDict = {}
        for symbol in symbols:
            print('Beginning data retrieval for', symbol)
            while 'Average duration' not in overviewDataDict: 
                browser.get(url_vanguard.format(symbol))
                WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.XPATH,'/html/body/div[1]/div[3]/div[3]/div[1]/div/div[1]/div/div/div/div[2]/div/div[2]/div[4]/div[2]/div[2]/div[1]/div/table/tbody/tr[4]')))
                time.sleep(.02)
                html = browser.page_source
                mySoup = BeautifulSoup(html, 'html.parser')
                htmlData = mySoup.findAll('table',{'role':'presentation'})
                overviewDataDict = extractOverviewTable(htmlData[2])
            #               ['SYMBOL', 'DURATION',                      'EXP. RATIO',                   'SEC YIELD',                'SEC Yield as of',          'PRICE',                'YTD']
            final_data_row = [symbol, overviewDataDict['Average duration'] ,returnsTableDict[symbol][2], returnsTableDict[symbol][6], returnsTableDict[symbol][-1], returnsTableDict[symbol][3], returnsTableDict[symbol][7] ]
            writer.writerow(final_data_row)
            overviewDataDict = {}
            print(symbol, 'data retrieval complete\n')
    browser.quit()

        
if __name__ == '__main__':
    main()
