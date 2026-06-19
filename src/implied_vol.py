import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq

def bsm_prices(S, K, T, r, sigma, option_type):
    d1 = (np.log(S/K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    call = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    put = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    if option_type == 'call':
        return call
    elif option_type == 'put':
        return put
    else:
        raise ValueError(f"option_type much be 'call' or 'put', got {option_type}")

def compute_implied_vol(market_price, S, K, T, r, option_type):

    def objective(sigma):
        return bsm_prices(S, K, T, r, sigma, option_type) - market_price

    

    try:
        sigma = brentq(objective, 1e-6, 5.0)
        return sigma
    except:
        return np.nan



if __name__ == "__main__":
    price = bsm_prices(S=100, K=100, T=0.5, r=0.05, sigma=0.2, option_type='call')
    print(f"Call price: {price:.2f}")
