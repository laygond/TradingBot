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
from datetime import datetime
import os, sys
import csv
import time

# NOTE:
# - Yfinance API has a 2,000 API calls per hour limit. Otherwise you will be banned
# - For get_all_tickers to work, update get_tickers.py to that of dbondi's fix 
# https://github.com/shilewenuw/get_all_tickers/issues/15
# - To buy fractional shares in robinhhod edit robinhood.py as mentioned by laygond
# https://github.com/robinhood-unofficial/pyrh/issues/200
# quantity should not have more than 6 decimal places. 

# Helper Functions
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

def attempt(func,*args,**kwargs):
    """
    Retries a function call up to three times; otherwise returns None 
    """
    MAX_CALLS_API = 3
    call_counter = 0
    while call_counter < MAX_CALLS_API:
        try:
            return func(*args,**kwargs)
        except:
            print (f"[INFO] Attempt {call_counter} retrying... {func.__name__}{args}")
            call_counter += 1
            time.sleep(3) # wait
            continue
    print(f"[WARNING] Unable to run {func.__name__}{args} continuing with code")
    return None

def cash2shares(cash,symbol):
    """
    Based on stocks current price, transforms cash into the equivalent
    share quantity. Shares are set up to 6 decimal places.
    """
    price  = rh.quote_data(symbol)['last_trade_price']
    shares = cash/float(price)
    return int(shares * 1e6)/1e6

def get_total_shares(symbol):
    """
    Returns quantity shares for a stock owned in robinhood. Otherwise zero. 
    """
    shares = 0
    if symbol in rh_stocks:
        for s in rh.securities_owned()['results']:
            if symbol == rh.get_url(s['instrument'])['symbol']:
                shares = s['quantity']
                break
    return shares

def check_ownership(symbol):
    """
    Verifies in robinhood if you own a stock or not. True: YES & False: NO
    """
    status = False
    for s in rh.securities_owned()['results']:
        if symbol == rh.get_url(s['instrument'])['symbol']:
            status = True
            break
    return status
    

# Login to Robinhood
rh = Robinhood()
rh.login(username=cf.ROBINHOOD_USERNAME, password=cf.ROBINHOOD_PASSWORD, challenge_type='sms')
try: 
    print("[INFO] Welcome to Robinhood Lord "+ rh.user()['first_name'])
except:
    print("[ERROR] login to robinhood failed.")

# Login to Webull
wb = webull()
wb.login(cf.WEBULL_USERNAME, cf.WEBULL_PASSWORD)
try: 
    print("[INFO] Welcome to Webull Secret Agent "+ wb.get_account()['brokerAccountId'])
except:
    print("[ERROR] login to webull failed.")

# Robinhood Current Portfolio Value
print("===Robinhood Portfolio Value===")
print(f"Cash  : ${rh.portfolios()['withdrawable_amount']}") #!!! DOUBLE-CHECK: Seems to update slow
print(f"Stocks: ${rh.portfolios()['market_value']}")
print(f"Total : ${rh.portfolios()['equity']}")
print("")

# Stocks Owned in Robinhood
# TODO: Print in table format instead
print("===My Robinhood Stocks===")
rh_stocks = []
for s in rh.securities_owned()['results']:
    sample_instrument = rh.get_url(s['instrument'])
    print(f"Name  : {sample_instrument['simple_name']}")
    print(f"Symbol: {sample_instrument['symbol']}")
    print(f"Shares: {s['quantity']}")
    #print(f"Average Cost: {s['average_buy_price']}")
    rh_stocks.append(sample_instrument['symbol'])
    print("")

# Webull Current Portfolio Value
print("===Webull Portfolio Value===")
print(f"Cash  : ${wb.get_account()['accountMembers'][1]['value']}")
print(f"Stocks: ${wb.get_account()['accountMembers'][0]['value']}")
print(f"Total : ${wb.get_account()['netLiquidation']}")
print("")

# Stocks Owned in Webull
# TODO: Print in table format instead
print("===My Webull Stocks===")
wb_stocks = []
for s in wb.get_account()['positions']:
    print(f"Name  : {s['ticker']['tinyName']}")
    print(f"Symbol: {s['ticker']['symbol']}")
    print(f"Shares: {s['positionProportion']}") #!!! DOUBLE-CHECK: Might not be number of shares
    wb_stocks.append(s['ticker']['symbol'])
    print("")

# Collect Tickers of interest
#tickers_test = ['AAPL','AMZN','TSLA','GOOG']
# tickers_gt_1500M_mk = gt.get_tickers_filtered(mktcap_min=1500)# millions (numbers are in millions)
sp500_table   = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0] #We want first table from wikipedia
tickers_sp500 = sp500_table['Symbol'].values.tolist()
# tickers_wb = [k['ticker']['symbol'] for k in wb.active_gainer_loser(direction='gainer', rank_type='afterMarket', count=2)['data']]
tickers = tickers_sp500 #rename for rest of code

# Open csv file to store data
dir_path = os.path.dirname(os.path.realpath(__file__))
csv_path = os.path.join(dir_path,'tickerRealTimeData.csv')
df = pd.read_csv(csv_path)

# Collect Data about tickers and write to csv file
# ==== HISTORY ====
# ... (TODO: later) must run once a day after market hours

# ==== REAL-TIME (TODAY'S Market DATA every 10 minutes) =====
i = len(df['Symbol']) # last index in csv file 
for k in range(len(tickers)): 
    wb_ticker_data        = attempt(wb.get_quote, tickers[k])
    wb_ticker_prediction  = attempt(wb.get_analysis, tickers[k])
    rh_ticker_data        = attempt(rh.get_fundamentals, tickers[k])
    rh_ticker_data2       = attempt(rh.quote_data, tickers[k])
    if wb_ticker_data == rh_ticker_data == None: 
    #then skip ticker
        continue 
    df.loc[i,'Symbol']    = tickers[k]
    df.loc[i,'TimeStamp'] = datetime.now()
    if wb_ticker_data:
        df.loc[i,'WB High']      = float(wb_ticker_data['high'])
        df.loc[i,'WB Low']       = float(wb_ticker_data['low'])
        df.loc[i,'WB Open']      = float(wb_ticker_data['open'])
        df.loc[i,'WB Price']     = float(wb_ticker_data['close'])
        df.loc[i,'WB Volume']    = float(wb_ticker_data['volume'])
        df.loc[i,'WB MarketCap'] = float(wb_ticker_data['marketValue'])
    if wb_ticker_prediction:
        df.loc[i,'WB RatingTotal'] = wb_ticker_prediction['rating']['ratingAnalysisTotals']
        df.loc[i,'WB StrongBuy']   = wb_ticker_prediction['rating']['ratingSpread']['strongBuy']
        df.loc[i,'WB Buy']         = wb_ticker_prediction['rating']['ratingSpread']['buy']
        df.loc[i,'WB Hold']        = wb_ticker_prediction['rating']['ratingSpread']['hold']
        df.loc[i,'WB UnderPerform']= wb_ticker_prediction['rating']['ratingSpread']['underPerform']
        df.loc[i,'WB Sell']        = wb_ticker_prediction['rating']['ratingSpread']['sell']
        df.loc[i,'WB TargetLow']   = wb_ticker_prediction['targetPrice']['low']
        df.loc[i,'WB TargetHigh']  = wb_ticker_prediction['targetPrice']['high']
        df.loc[i,'WB TargetMean']  = wb_ticker_prediction['targetPrice']['mean']
    if rh_ticker_data and rh_ticker_data2:
        df.loc[i,'RH High']      = float(rh_ticker_data['high'])
        df.loc[i,'RH Low']       = float(rh_ticker_data['low'])
        df.loc[i,'RH Open']      = float(rh_ticker_data['open'])
        df.loc[i,'RH Price']     = float(rh_ticker_data2['last_trade_price'])
        df.loc[i,'RH Volume']    = float(rh_ticker_data['volume'])
        df.loc[i,'RH MarketCap'] = float(rh_ticker_data['market_cap'])
    i+=1 #next row
#df.to_csv('tickerRealTimeData.csv', index=False)

# Retrieve History and Real-Time csv ticker data for Analysis
# (Current strategy keep only top 100 from sp500)
tickers_final = df.sort_values(by=['WB MarketCap'], ascending=False).filter(items=['Symbol']).squeeze().values.tolist()

# Assign Final Selected List of Stocks as Buy or Sell
final_report ={}
keep_amount = 100 #(Current strategy keep only top keep_amount)
for k in range(len(tickers_final)):
    final_report[tickers_final[k]] = 'buy' if k < keep_amount else 'sell'
print(final_report)

# Update Portfolio as specified in Final Report
# SELL first to increase buying power
for key, value in final_report.items():
    if key in rh_stocks and value == 'sell':
        rh.place_market_sell_order(rh.instrument(key)['url'],
                                   key,
                                   'GFD', #GFD: Good only during the day. GTC: good till cancelled
                                   get_total_shares(key)) 
        time.sleep(3) #wait
        if check_ownership(key):
            print(f"[WARNING] {key} was NOT sold")
        else:
            print(f"[INFO] {key} was sold")
            rh_stocks.remove(key)
# BUY
buying_power = float(rh.portfolios()['withdrawable_amount']) #!!! DOUBLE-CHECK: Seems to update slow
invest= buying_power/(keep_amount - len(rh_stocks)) #(current strategy keep top 100)
for key, value in final_report.items():
    if key not in rh_stocks and value == 'buy':
        rh.place_market_buy_order(rh.instrument(key)['url'],
                                  key,
                                  'GFD', #GFD: Good only during the day. GTC: good till cancelled
                                  cash2shares(invest,key))
        time.sleep(3) #wait 
        if check_ownership(key):
            print(f"[INFO] {key} was bought")
            rh_stocks.append(key)
        else:
            print(f"[WARNING] {key} was NOT bought")