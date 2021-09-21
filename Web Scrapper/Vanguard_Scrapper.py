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
            url_vanguard = 'https://investor.vanguard.com/mutual-funds/profile/overview/{}'

            response = requests.get(url_vanguard.format(symbol))
            mySoup = BeautifulSoup(response.text, 'html.parser')
            htmlData = mySoup.findAll('span',{'class':'{sceIsLayer : isETF, arrange : isMutualFund, arrangeSec : isETF}'})

# class = '{sceIsLayer : isETF, arrange : isMutualFund, arrangeSec : isETF}'
            
            # extract: Duration, EXP ratio, YTD 2021, SEC Yield, Price, Last Updated
            results = [symbol, duration, schwab_dict['Net Expense Ratio'], schwab_dict['YTD Return'], schwab_dict['30-Day SEC Yield'], nav ]
            writer.writerow(results)
    
if __name__ == '__main__':
    main()
