# from pyrh import Robinhood
# import config

# rh = Robinhood()
# rh.login(username=config.rh_user, password=config.rh_passwd)
# rh.print_quote("AAPL")

#Import all packages needed
import pandas as pd
import numpy as np
from config import WEBULL_USERNAME, WEBULL_PASSWORD
from progressbar import progressbar
from webull import webull # for paper trading, import 'paper_webull'

#login to webull/authenticate with API
wb = webull()
wb.login(WEBULL_USERNAME, WEBULL_PASSWORD)
# wb.login("WEBULL_USERNAME", "WEBULL_PASSWORD")
try: 
    print(wb.get_account_id())
except Exception as e:
    print(e)
    print("login failed.")

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