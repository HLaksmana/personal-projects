import requests
import json
import xmltodict
import requests
import os
import csv

def getCUSIP(symbol):
    url = 'https://fidelity-investments.p.rapidapi.com/v2/auto-complete'

    querystring = {'q':symbol}

    headers = {
        'x-rapidapi-host': "fidelity-investments.p.rapidapi.com",
        'x-rapidapi-key': "d151efd3b4mshcd4f6a5e2275abfp1dd0bfjsn8089209bcbd0"
        }

    response = requests.request('GET', url, headers=headers, params=querystring)
    data = json.loads(response.text)
    return data[0]['quotes']['suggestions'][0]['cusip']

def main():
    dirname = os.path.dirname(__file__)
    symbols = []
    with open(os.path.join(dirname, 'symbols.csv')) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row:
                symbols.append(row[0])
    symbols = [s.strip() for s in symbols if s.startswith('F') or s.startswith('SP')]
    
    if os.path.isfile(os.path.join(dirname,'cusip_ref.csv')): 
        with open(os.path.join(dirname,'cusip_ref.csv')) as csvfile:
            reader = csv.reader(csvfile)
            try:
                fidelity_cusip_dict = {rows[0]:rows[1] for rows in reader}
            except IndexError:
                os.remove(os.path.join(dirname,'cusip_ref.csv'))
                fidelity_cusip_dict = {}
    else:
        fidelity_cusip_dict = {}
    
    url_fidelityApi = 'https://fundresearch.fidelity.com/api/mutual-funds/{}/{}'
    # api options:
    #   header, summary, performance-and-risk, ratings, composition, fees-and-distributions
    #   cusip
    
    if symbols[0] not in fidelity_cusip_dict:
        cusip = getCUSIP(symbols[0])
        fidelity_cusip_dict[symbols[0]] = cusip
        with open(os.path.join(dirname,'cusip_ref.csv'), 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([symbols[0],cusip])
    
    response = requests.get(url_fidelityApi.format('header',fidelity_cusip_dict[symbols[0]]))
    data = json.loads(response.text)
    navDate = data['model']['DetailsData']['detailDataList'][0]['navDataRowData'][0]['navDailyDate'].replace('/','-')
    header = ['Ticker','Duration','Expense Ratio','SEC Yield','SEC Yield info','Price','Price as of ','YTD', 'YTD as of']
    with open(os.path.join(dirname, 'fidelity_fund_data_'+ navDate +'.csv'), 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for symbol in symbols:
            print(symbol)
            if symbol not in fidelity_cusip_dict:
                cusip = getCUSIP(symbol)
                fidelity_cusip_dict[symbol] = cusip
                with open(os.path.join(dirname,'cusip_ref.csv'), 'a') as cusipRef:
                    addCusip = csv.writer(cusipRef)
                    addCusip.writerow([symbol,cusip])
                
            response = requests.get(url_fidelityApi.format('header',fidelity_cusip_dict[symbol]))
            data = json.loads(response.text)
            performance = data['model']['PerformanceAvgAnnualReturnsData']['performanceAvgAnnualReturnsDataList'][0]
            cumulativeReturnsYtd = performance['fundPerformanceRowDataList'][0]['cumulativeReturnsYtd']
            ytdAsOf = performance['ytdAsOf']
            
            details = data['model']['DetailsData']['detailDataList'][0]
            navData = details['navDataRowData'][0]
            navDate = navData['navDailyDate']
            nav = navData['navDailyAmount']['value']
            expRatioNet = details['expRatioNet']['value']
            expRatioNetAsOf = details['expRatioDate']['value']
            
            response = requests.get(url_fidelityApi.format('summary',fidelity_cusip_dict[symbol]))
            data = json.loads(response.text)
            portfolioData = data['model']['PortfolioDataData']['portfoliodataList'][0]
            duration = portfolioData['durationPeriod'] if 'durationPeriod' in portfolioData else '?'
            #durationAsOf = portfolioData['durationAsOf']['value']
            secYield = portfolioData['yield30DayEndOfMonthPct']['value']
            secYieldInfo = portfolioData['yield30DayEndOfMonthPct']['label']
            secYieldAsOf = portfolioData['yield30DayEndOfMonthAsOf']['value']
            secInfo = '%s as of %s' % (secYieldInfo,secYieldAsOf)
            #['Ticker','Duration','Expense Ratio','SEC Yield','SEC Yield info','Price','Price as of ','YTD', 'YTD as of']
            
            writer.writerow([symbol, duration, expRatioNet+'%', secYield+'%', secInfo, nav, navDate, cumulativeReturnsYtd+'%', ytdAsOf])
        
        
if __name__ == '__main__':
    main()
