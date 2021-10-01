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
    dataHeaders = ['SYMBOL', 'DURATION', 'EXP. RATIO', 'YTD 2021','YTD as of','SEC YIELD', 'PRICE']

    with open('scrappedData.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(dataHeaders)
        url_schwab = 'https://www.schwab.wallst.com/Prospect/Research/MutualFunds/Summary.asp?symbol={}'
        url_morningstar = 'https://www.morningstar.com/funds/xnas/{}/quote'
        for symbol in symbols:   
            print(symbol) 
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
            htmlData = mySoup.find('div', {'class': 'fund-quote__data'})
            tableItems = htmlData.findAll('div', {'class': 'fund-quote__item'})
            tableDict = {}
            for item in tableItems:
                k = item.findAll('span')
                tableDict[k[0].text.strip()] = k[1].text.strip().replace('\t', '').replace('\n', '')
                
            ytd = schwab_dict['YTD Return'][:schwab_dict['YTD Return'].index('%') + 1]
            ytd_asOf = schwab_dict['YTD Return'][schwab_dict['YTD Return'].index('%') + 1:]
            duration = tableDict['Effective Duration'] if 'Effective Duration' in tableDict else '?'
            nav = tableDict['NAV / 1-Day Return'] if 'NAV / 1-Day Return' in tableDict else '?'
            results = [symbol, duration, schwab_dict['Net Expense Ratio'], ytd, ytd_asOf, schwab_dict['30-Day SEC Yield'], nav ]
            writer.writerow(results)
    
if __name__ == '__main__':
    main()
