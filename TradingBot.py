# Import all packages needed
import pandas as pd
import numpy as np
import config as cf
from progressbar import progressbar
from webull import webull # for paper trading, import 'paper_webull'
from pyrh import Robinhood
import json

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

# Robinhood Portfolio Value
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
    print("Quote")
    print(rh.quote_data(sample_instrument['symbol']))
    print("Fundamentals")
    print(rh.get_fundamentals(sample_instrument['symbol']))
    print("")


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