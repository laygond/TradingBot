# Import all packages needed
import pandas as pd
import numpy as np
import config as cf
from progressbar import progressbar
from webull import webull # for paper trading, import 'paper_webull'
from pyrh import Robinhood
import json
import yfinance as yf
from get_all_tickers import get_tickers as gt
import pandas_datareader.data as web
import datetime
import os, sys
import csv
import time

# NOTE:
# - Yfinance API has a 2,000 API calls per hour limit. Otherwise you will be banned
# - For get_all_tickers to work, update get_tickers.py to that of dbondi's fix 
# https://github.com/shilewenuw/get_all_tickers/issues/15

# Helper Function
def print_decorator(func):
    """
    Overload Print function to pretty print Dictionaries 
    """
    def wrapped_func(*args,**kwargs):
        if isinstance(*args, dict):
            return func(json.dumps(*args, sort_keys=True, indent=2, default=str))
        else:
            return func(*args,**kwargs)
    return wrapped_func
print = print_decorator(print)


# Login to Robinhood
rh = Robinhood()
rh.login(username=cf.ROBINHOOD_USERNAME, password=cf.ROBINHOOD_PASSWORD, challenge_type='sms')
try: 
    print("[INFO] Welcome to Robinhood Lord "+ rh.user()['first_name'])
except Exception as e:
    print(e)
    print("[ERROR] login to robinhood failed.")

# Login to Webull
wb = webull()
wb.login(cf.WEBULL_USERNAME, cf.WEBULL_PASSWORD)
try: 
    print(wb.get_account_id())
except Exception as e:
    print(e)
    print("[ERROR] login to webull failed.")

# Robinhood Current Portfolio Value
print("===Robinhood Portfolio Value===")
print(f"Cash  : ${rh.portfolios()['withdrawable_amount']}")
print(f"Stocks: ${rh.portfolios()['market_value']}")
print(f"Total : ${rh.portfolios()['equity']}")
print("")

# Stocks Owned in Robinhood
print("===My Robinhood Stocks===")
for s in rh.securities_owned()['results']:
    sample_instrument = rh.get_url(s['instrument'])
    print(f"Name  : {sample_instrument['simple_name']}")
    print(f"Symbol: {sample_instrument['symbol']}")
    print(f"Shares: {s['quantity']}")
    print(f"Price : {rh.quote_data(sample_instrument['symbol'])['last_trade_price']}")
    print(f"Average Cost: {s['average_buy_price']}")
    # print("Quote")
    # print(rh.quote_data(sample_instrument['symbol']))
    # print("Fundamentals")
    # print(rh.get_fundamentals(sample_instrument['symbol']))
    print("")

# ------------WEBULL SECTION MOHAMMAD---------------
# TODO:
#   - Retrieve Current Portfolio Value and Stocks Owned
#   - Explore and retrieve Good Analysis indicators that might be useful


# print(wb.get_account())

#Grab all active stocks on webull
data = wb.active_gainer_loser(direction='gainer', rank_type='afterMarket', count=50)
# wb.active_gainer_loser('active', 9999)

#Convert to dataframe
# data = pd.DataFrame(data)

# print(np.shape(data))
# print(data.symbol)
print(data['data'][0]['ticker']['symbol'])

# #Add columns and zero values for ratings data
# data['ratingTotal'] = np.zeros(len(data.tickerId))
# data['ratingAnalysis'] = np.zeros(len(data.tickerId))
# data['underPerform'] = np.zeros(len(data.tickerId))
# data['buy'] = np.zeros(len(data.tickerId))
# data['sell'] = np.zeros(len(data.tickerId))
# data['strongBuy'] = np.zeros(len(data.tickerId))
# data['hold'] = np.zeros(len(data.tickerId))

# #Add columns and zero values for targetPrice data
# data['targetLow'] = np.zeros(len(data.tickerId))
# data['targetHigh'] = np.zeros(len(data.tickerId))
# data['current'] = np.zeros(len(data.tickerId))
# data['mean'] = np.zeros(len(data.tickerId))

# #Loop through all of the stocks
# for i in progressbar(range(len(data.symbol))):
#     try: 
#         stock = wb.get_analysis(data.loc[i,'symbol'])
#         #Ratings
#         data.loc[i,'ratingTotal'] = stock['rating']['ratingAnalysisTotals']
#         data.loc[i,'ratingAnalysis'] = stock['rating']['ratingAnalysis']
#         data.loc[i,'underPerform'] = stock['rating']['ratingSpread']['underPerform']
#         data.loc[i,'buy'] = stock['rating']['ratingSpread']['buy']
#         data.loc[i,'sell'] = stock['rating']['ratingSpread']['sell']
#         data.loc[i,'strongBuy'] = stock['rating']['ratingSpread']['strongBuy']
#         data.loc[i,'hold'] = stock['rating']['ratingSpread']['hold']
#         #TargetPrice
#         data.loc[i,'targetLow'] = stock['targetPrice']['low']
#         data.loc[i,'targetHigh'] = stock['targetPrice']['high']
#         data.loc[i,'current'] = stock['targetPrice']['current']
#         data.loc[i,'mean'] = stock['targetPrice']['mean']
#     except KeyboardInterrupt:
#         break
#     except:
#         pass

#Drop to CSV file
# data.to_csv("wb_analysis_data.csv", index = False)
#-----------------------------------------------------

# Collect Tickers of interest
tickers_test = ['AAPL','AMZN','TSLA','GOOG']
tickers_gt_1500M_mk = gt.get_tickers_filtered(mktcap_min=1500)# millions (numbers are in millions)
sp500_table   = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0] #We want first table from wikipedia
tickers_sp500 = sp500_table['Symbol'].values.tolist()
tickers = tickers_sp500 #rename for rest of code

# Open csv file to store data
dir_path = os.path.dirname(os.path.realpath(__file__))
csv_path = os.path.join(dir_path,'tickerRealTimeData.csv')
df = pd.read_csv(csv_path)

# Collect Data about tickers and write to csv file
# REAL-TIME
MAX_YAHOO_API_CALLS = 1999
MAX_CALLS_PER_TICKER = 3
yahoo_API_calls_counter = 0
ticker_call_counter = 0
i=0 #for index in csv file 
k=0 #for index in tickers list
while k < len(tickers):
    if yahoo_API_calls_counter<MAX_YAHOO_API_CALLS:
        try:
            yahoo_API_calls_counter += 1
            ticker_data=web.get_quote_yahoo(tickers[k])
            df.loc[i,'Symbol']    = tickers[k]
            df.loc[i,'MarketCap'] = ticker_data.loc[tickers[k],'marketCap']
            df.loc[i,'Close']     = ticker_data.loc[tickers[k],'price']
            df.loc[i,'Volume']    = ticker_data.loc[tickers[k],'regularMarketVolume']
            i+=1 #next row
        except:
            print (f"[INFO] Retry: {ticker_call_counter} for symbol: {tickers[k]}")
            ticker_call_counter += 1
            time.sleep(3) # wait
            if ticker_call_counter == MAX_CALLS_PER_TICKER:
                ticker_call_counter=0
                print(f"[INFO] Unable to retrieve : {tickers[k]} continuing with next ticker")
            else: 
                continue
        k+=1 #next ticker
    else:
        # wait an hour and set yahoo_API_calls_counter to zero
        time.sleep(60*60)
        yahoo_API_calls_counter = 0
#df.to_csv('tickerRealTimeData.csv', index=False)

# HISTORY
# ... (TODO: later)

# Retrieve History and Real-Time csv ticker data for Analysis
# (Current strategy keep only top 100 from sp500)
tickers_final = df.sort_values(by=['MarketCap'], ascending=False).filter(items=['Symbol']).squeeze().values.tolist()

# Assign Final Selected List of Stocks as Buy or Sell
final_report ={}
for k in range(len(tickers_final)):
    final_report[tickers_final[k]] = 'buy' if k < 100 else 'sell'
print(final_report)

# Update Portfolio as specified in Final Report


