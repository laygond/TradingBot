from pyrh import Robinhood
import config

rh = Robinhood()
rh.login(username=config.rh_user, password=config.rh_passwd)
rh.print_quote("AAPL")