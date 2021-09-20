from bs4 import BeautifulSoup
import requests
import csv
import os

def main():

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'symbols.csv')
    symbols = []
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            symbols.append(row[0])
    symbols = [s.strip() for s in symbols]    
    dataHeaders = ['SYMBOL', 'DURATION', 'EXP. RATIO', 'YTD 2021','SEC YIELD', 'PRICE']

    with open('scrappedData.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(dataHeaders)
        for symbol in symbols:   
            print(symbol) 
            url_schwab = 'https://www.schwab.wallst.com/Prospect/Research/MutualFunds/Summary.asp?symbol={}'
            url_morningstar = 'https://www.morningstar.com/funds/xnas/{}/quote'

            response = requests.get(url_schwab.format(symbol))
            mySoup = BeautifulSoup(response.text, 'html.parser')
            table = mySoup.find('div',{'id':'detailsWrapper'})
            rows = table.findAll('table',{'class':'tableType1'})
            headers = []
            output = []
            schwab_dict = {}
            for row in rows:
                schwabData = row.find('tbody').find('tr').findAll('td')
                colNames = row.find('tbody').find('tr').findAll('th')
                colNames = [ele.text.strip() for ele in colNames]
                schwabData = [ele.text.strip() for ele in schwabData]

                output.append([ele for ele in schwabData if ele]) 
                headers.append([ele for ele in colNames if ele])
            #[['52 Week Range'], ['YTD Return'], ['Gross Expense Ratio'], ['Net Expense Ratio'], ['Tax-Equivalent Yield'], ['30-Day SEC Yield'], ["Distribution Yield], ['Most Recent Distribution'], ['Availability'], ['Manager Tenure']]
            #[['$9.92 - $10.01'], ['0.91%as of 09/02/2021'], ['0.68%'], ['0.68%'], ['--'], ['1.42%'], ['1.65%'], ['$0.0118'], ['Open'], ['2011']]
            headers[1] = ['YTD Return']
            headers[6] = ['Distribution Yield']
            for i in range(len(headers)):
                schwab_dict[headers[i][0]] = output[i][0]


            response = requests.get(url_morningstar.format(symbol))
            mySoup = BeautifulSoup(response.text, 'html.parser')
            htmlData = mySoup.findAll('span',{'class':'mdc-data-point mdc-data-point--number'})

            duration = htmlData[-1].text.strip()
            nav = htmlData[0].text.strip()

            # extract: Duration, EXP ratio, YTD 2021, SEC Yield, Price, Last Updated
            results = [symbol, duration, schwab_dict['Net Expense Ratio'], schwab_dict['YTD Return'], schwab_dict['30-Day SEC Yield'], nav ]
            writer.writerow(results)
    
if __name__ == '__main__':
    main()
