

import scipy as sp
import pandas as pd
import requests as rq
import xlsxwriter as xlsx
import math
from iexfinance.stocks import Stock
from scipy import stats

stocks=pd.read_csv('sp_500_stocks.csv')
## this is just a list of snp stock names i would use a live index but couldnt find a free version

my_key='Tsk_d63eea9499234f5a89f5ca3188e82ea7'# i dont care if you see my key this is sandbox mode only randomised test data is taken from the api

#%%
# Function source https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]   
    
symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
    #print(symbol_strings[i])

#this function separates a big list into chunks of size 100. The last chunk is smaller as it has the remaining 5 elements.
"the reason this function is used is so that we can reduce the number of single api calls and use batch cals for every chunk"
#%%
column_names=[
    'Ticker',
    'Price',
    'Number of Shares to Buy', 
    'Price-to-Earnings Ratio',
    'PE Percentile',
    'Price-to-Book Ratio',
    'PB Percentile',
    'Price-to-Sales Ratio',
    'PS Percentile',
    'EV/EBITDA',
    'EV/EBITDA Percentile',
    'EV/GP',
    'EV/GP Percentile',
    'One-Year Price Return',
    'One-Year Price Return Percentile',
    'Value Score'
]
#creating th ecolumn names of the dataframe

dataframe = pd.DataFrame(columns = column_names)

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote,advanced-stats,stats&token={my_key}'
    data = rq.get(batch_api_call_url).json()
    for symbol in data.keys():
        enterprise_value = data[symbol]['advanced-stats']['enterpriseValue']
        ebitda = data[symbol]['advanced-stats']['EBITDA']
        gross_profit = data[symbol]['advanced-stats']['grossProfit']
        
        try:
            ev_to_ebitda = enterprise_value/ebitda
        except TypeError:
            ev_to_ebitda = sp.NaN
        
        try:
            ev_to_gross_profit = enterprise_value/gross_profit
        except TypeError:
            ev_to_gross_profit = sp.NaN
            
        dataframe = dataframe.append(
            pd.Series([
                symbol,
                data[symbol]['quote']['latestPrice'],
                'N/A',
                data[symbol]['quote']['peRatio'],
                'N/A',
                data[symbol]['advanced-stats']['priceToBook'],
                'N/A',
                data[symbol]['advanced-stats']['priceToSales'],
                'N/A',
                ev_to_ebitda,
                'N/A',
                ev_to_gross_profit,
                'N/A',
                data[symbol]['stats']['year1ChangePercent'],
                'N/A',
                'N/A'
        ],
        index = column_names),
            ignore_index = True
        )

#print(dataframe)
#%% clearing missing data and replacing it with the average

dataframe[dataframe.isnull().any(axis=1)]
for column in ['Price-to-Earnings Ratio', 'Price-to-Book Ratio','Price-to-Sales Ratio',  'EV/EBITDA','EV/GP','One-Year Price Return']:
    dataframe[column].fillna(dataframe[column].mean(), inplace = True)

#%% calculating percentiles for each metric so we can give a value score to the stocks

metrics = {
            'Price-to-Earnings Ratio': 'PE Percentile',
            'Price-to-Book Ratio':'PB Percentile',
            'Price-to-Sales Ratio': 'PS Percentile',
            'EV/EBITDA':'EV/EBITDA Percentile',
            'EV/GP':'EV/GP Percentile',
            'One-Year Price Return':'M Percentile'
}

for row in dataframe.index:
    for metric in metrics.keys():
        dataframe.loc[row, metrics[metric]] = stats.percentileofscore(dataframe[metric], dataframe.loc[row, metric])/100

# Print each percentile score to make sure it was calculated properly
for metric in metrics.values():
    print(dataframe[metric])

#Print the entire DataFrame    
#print(dataframe)

#now to calculate the value score we will take the mean of all the metric percentiles

from statistics import mean

for row in dataframe.index:
    value_percentiles = []
    for metric in metrics.keys():
        value_percentiles.append(dataframe.loc[row, metrics[metric]])
    dataframe.loc[row, 'Value Score'] = mean(value_percentiles)
    
#print(dataframe)

dataframe.sort_values(by = 'Value Score', inplace = True)
dataframe = dataframe[:20]
dataframe.reset_index(drop = True, inplace = True)

#print(dataframe)

#%% exporting output to an excel file
writer = pd.ExcelWriter('top_20_recommended_stocks.xlsx', engine='xlsxwriter')
dataframe.to_excel(writer, sheet_name='top 20 recommended stocks', index = False)
writer.save()