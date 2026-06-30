import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

from implied_vol import compute_implied_vol

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


def compute_row_iv(row, spot):
    market_price = (row['bid'] + row['ask']) / 2
    K = row['strike']
    T = row['dte']/365
    r = 0.05
    option_type = row['type']

    return compute_implied_vol(market_price, spot, K, T, r, option_type)

def save_data(df, ticker):

    filepath = f"data/{ticker}_options.parquet"
    df.to_parquet(filepath)

def run_pipeline(tickers=['SPY', 'QQQ', 'AAPL']):
    if len(tickers) == 0:
        return 

    for ticker in tickers:
        df = fetch_options_chain(ticker)
        df = filter_illiquid(df)
        spot = yf.Ticker(ticker).info['regularMarketPrice']
        df['computed_iv'] = df.apply(lambda row: compute_row_iv(row, spot), axis=1)
        df['spot'] = spot
        save_data(df, ticker)
    
    return "Saved all file successfully"

if __name__ == "__main__":
    run_pipeline()