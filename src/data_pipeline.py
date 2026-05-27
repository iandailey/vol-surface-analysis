import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

def fetch_options_chain(ticker, min_dte=7, max_dte=365):
    #create yfinance ticker object
    dat = yf.Ticker(ticker)

    #get list of available expiration dates
    expirations = dat.options

    #get todays dateS
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

def filter_illiquid(df):

    before = len(df)
    df = df[(df['bid'] > 0) & (df['ask'] > 0)]
    print(f"Removed {before - len(df)} options with zero bid or ask")

    before = len(df)
    df = df[(df['openInterest'] >= 100) & (df['volume'] >= 10)]
    print(f"Removed {before - len(df)} options small open interest and volume")

    before = len(df)
    df = df[(df['ask'] - df['bid']) <= 0.10 * (df['ask'] + df['bid']) / 2]
    print(f"Removed {before - len(df)} options with wide bid-ask spreads")

    before = len(df)
    ticker = df['ticker'].iloc[0]
    spot = yf.Ticker(ticker).info['regularMarketPrice']

    df = df[(df['strike'] > 0.7 * spot) & (df['strike'] < 1.3 * spot)]
    print(f"Removed {before - len(df)} options with strikes too far from spot")

    return df

if __name__ == "__main__":
    df = fetch_options_chain("SPY")
    print(f"Raw data shape: {df.shape}")
    df = filter_illiquid(df)
    print(f"Filtered data shape: {df.shape}")
