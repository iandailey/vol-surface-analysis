import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


df = pd.read_parquet("data/SPY_options.parquet")

T = df['dte'] /365
r = 0.05
df['F'] = df['spot'] * np.exp(r * T)
df['log_moneyness'] = np.log(df['strike'] / df['F'])


def plot_vol_smile(df, expiry):
    slice_df = df[df['expiry'] == expiry]

    calls = slice_df[slice_df['type'] == 'call']
    puts = slice_df[slice_df['type'] == 'put']

    plt.figure(figsize=(10, 6))

    plt.plot(calls['log_moneyness'], calls['computed_iv'], color = 'blue', label = 'calls')

    plt.plot(puts['log_moneyness'], puts['computed_iv'], color = 'red', label = 'puts')

    plt.axvline(x=0, color='black', linestyle='--', label='ATM')

    plt.xlabel('Log Moneyness')
    plt.ylabel('IV')
    plt.title(f'Vol Smile - {expiry}')
    plt.legend()
    plt.savefig(f"notebooks/vol_smile_{expiry}.png")
    plt.close()
    print("Plot saved to notebooks/vol_smile.png")

if __name__ == "__main__":
    # get the first available expiry
    expiries = df['expiry'].unique()[:4]
    for expiry in expiries:
        plot_vol_smile(df, expiry)