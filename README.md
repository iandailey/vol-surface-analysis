# Volatility Surface Construction & Analysis
Python toolkit to construct and analyze the implied volatility (IV) surfaces from live options data.

---

## Motivation
The IV surface is one of the most info rich objects in options markets. The surface demostrates how the market prices uncertainty across all expirations and strikes simulatenously, showing the market's risk netural distrubtion of future returns.

The IV surface is foundational in pricing and market making for options, along with systematic strategies. It quantifies and visualizes the market's demand for downside protection along with opinions on future events. 

This project seeks to build the surface from scratch, starting with the options chain data, filtering liquidity, BSM IV computation, and visualization to better understand its operation. This is meant as an intro project into modern options concepts along with setting foundational qunatitative skills. 

---

## Methodology

### 1. Data Pipeline
Live options chain data is pulled from Yahoo Finance via yfinance for a set of tickers (defaults to SPY, QQQ, AAPL). Options are fetched across a changable DTE window (defaults to 7-365 days).

### 2. Liquidity filtering
Raw options data often contains many illiquid contracts with prcicing that isn't super reliable. Four filters are applied ith per-filter logging:
- Zero bid/ask - contracts with no active market makers are dropped
- Open interest < 100 - contracts with insufficient outstanding positions are dropped
- Volume < 10 - conrtacts need a solid amount of daily trading otherwise dropped
- Bid-Ask spread > 10% of mid - contracts with wide spreads are dropped
- Moneyness bounds - strikes outside `0.7 < K/S < 1.3` are dropped. This was suggested to me since deep OTM contracts tend to have IV that is not very reliable

As an example, for SPY's options chain, the filters removed ~70% of raw contracts leaving only contracts that are actively traded with more reliable pricing.

### 3. Implied Volatility Computation
The Black-Scholes-Merton pricing formula is implemented from scratch using `scipy.stats.norm.cdf` for the cumulative normal distribution. IV is computed by inverting the BSM formula numerically using Brent's method (there will be different methods attempted in the future), which guarantees convergence on a bounded interval `[1e-6, 5.0]`.

Mid pirce ((bid + ask) / 2) is used as the market price input. Felt this was simplest and easiest. There is an expected discrepancy vs. Yahoo Finance's built in `impliedVolatility` field. After much investigating it appears to be from dividend omission in standard BSM, differing rate assumptions (I am sing 5% as the rfr right now), and also timestamp mischatches between option last trade time and the current spot price. (More accurate current data is $$$)

### 4. Surface Construction
Strikes are converted to log-moneyness k = log(K/F) where F = S * exp(rT) is the forward price. This is standard practice as it centers the surface at 0 for ATM options and scaling naturally with the BSM formula.

Scattered data points are interpolated onto a uniform 50x30 grid using scipy with cubic interpolation. Points outside the conves hull of the data are masked.

### 5. Visualization
Two interactive visualizations are produces via plotly:
- 3D surface plot - rotatable, colored by IV level using diverging colorscale
- 2d heatmap - IV as a function of log moneyness (x) and DTE (y) often easier for identifying structural patterns

---

## Results
The surface exhibits the classic equity skew; IV is higher for OTM puts (negative log moneyness) than for OTM calls (positive log moneyness), reflecting the persistent demand for downside protection. The skew is consistent across all expiries.

The 3D surface and heatmap reveal localized artifacts from residual illiquid contracts. This is why no arbitrage checks are implemented next.


## Project structure
(shout out Claude for helping me make the diagram below)
```
vol-surface-analysis/
├── data/                   # Parquet files (options chain + computed IVs)
├── notebooks/              # Interactive HTML visualizations + static plots
├── src/
│   ├── data_pipeline.py    # Fetch, filter, compute IV, save to parquet
│   ├── implied_vol.py      # BSM pricer + Brent's method IV solver
│   └── surface.py          # Log-moneyness transformation, interpolation, visualization
├── tests/                  # Unit tests (BSM pricer, IV solver)
└── requirements.txt
```

---

## Current State

- [x] End-to-end data pipeline (fetch → filter → IV computation → parquet storage)
- [x] BSM pricer implemented from scratch
- [x] Implied vol solver via Brent's method
- [x] Log-moneyness transformation and per-expiry smile plots
- [x] 3D interactive vol surface
- [x] 2D interactive heatmap
- [ ] No-arbitrage checks (calendar spread + butterfly)
- [ ] SVI parameterization
- [ ] Local volatility surface (Dupire)
- [ ] Greeks: vanna, volga
- [ ] Volatility regime classification

---

## Dependencies

```
yfinance
pandas
numpy
scipy
matplotlib
plotly
pyarrow
```

---

## Limitations and Next Steps
- Dividend Yield: as mentioned before, BSM omits dividends, causing systematic IV underestimation for dividend paying underlying securities. Adding the Merton continuous dividend yield model would help with this.
- Rate assumptions: risk free rate (rfr) is hardcoded at 5% as mentioned above. Using a live treasury yield would improve the accuracy.
- Interpolation artifacts: cibic interpolation can produce unrealistic values in sparse regions. SVI parameterization (coming soon) will replace raw interpolation with financially motivated parametric fit.
- Single snapshot: the pipeline reflects a point in time snapshot. A time series of surfaces would enable regime analysis and historical vol comparisons. 