import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

def fetch_options_chain(ticker, min_dte=7, max_dte=365):
    #create yfinance ticker object
    dat = yf.Ticker(ticker)

    #get list of available expiration dates
    expirations = dat.options

    #get todays date
    today = datetime.today().date()

    all_data = []

    for expiry in expirations:
        #convert expiration to date obj
        expiry_date = datetime.strptime(expiry, '%Y-%m-%d').date()

        dte = (expiry_date - today).days

        if min_dte <= dte <= max_dte:
            chain = dat.option_chain(expiry)

            calls = chain.calls
            puts = chain.puts

            calls['type'] = 'call'
            calls['ticker'] = ticker
            calls['dte'] = dte
            calls['expiry'] = expiry

            puts['type'] = 'put'
            puts['ticker'] = ticker
            puts['dte'] = dte
            puts['expiry'] = expiry

            options_data = pd.concat([calls, puts], ignore_index=True)

            all_data.append(options_data)

    return pd.concat(all_data, ignore_index=True)

if __name__ == "__main__":
    df = fetch_options_chain('SPY')
    print(df.shape)
    print(df.head())
