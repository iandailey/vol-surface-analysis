import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import plotly.graph_objects as go


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

def build_surface(df):
    k = df['log_moneyness']
    t = df['dte']
    iv = df['computed_iv']

    k_grid = np.linspace(-0.3, 0.3, 50)
    t_grid = np.linspace(7, 365, 30)

    K, T = np.meshgrid(k_grid, t_grid)

    grid = griddata((k, t), iv, (K, T), method='cubic')

    #masking out NaN values
    grid = np.ma.masked_invalid(grid)

    return K, T, grid

def plot_surface_3d(K, T, grid):
    fig = go.Figure(data=[go.Surface(
        x=K,
        y=T,
        z=grid,
        colorscale='RdBu'
    )])

    fig.update_layout(
        title='SPY Implied Volatility Surface',
        scene=dict(
            xaxis_title='Log-Moneyness',
            yaxis_title='DTE',
            zaxis_title='Implied Volatility'
        )
    )
    
    fig.write_html("notebooks/vol_surface_3d.html")
    print("Saved to notebooks/vol_surface_3d.html")

if __name__ == "__main__":
    K, T, grid = build_surface(df)
    plot_surface_3d(K, T, grid)