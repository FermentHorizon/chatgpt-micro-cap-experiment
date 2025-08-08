# Scripts

**Note: NONE OF THE PROMPTS ARE AUTOMATED, MANUAL UPDATES AND DEEP RESEARCH IS REQUIRED**
## Generate_Graph.py

Pretty simple — it grabs the daily logs from `'chatgpt_portfolio_update.csv'` and then plots the results alongside a benchmark index (default S&P 500, ticker `^SPX`).
To run, just make sure there's data in `'chatgpt_portfolio_update.csv'`, then run the script to generate the plot. Use `--benchmark-index` to compare against another market such as the S&P/ASX 200 (`^AXJO`).

---

## Trading_Script.py

The trading script tracks positions, logs trades, and prints daily results.

Set `DEFAULT_SUFFIX` in the script to automatically append an exchange suffix to tickers. For example, `DEFAULT_SUFFIX = ".AX"` lets you enter `BHP` and have it logged as `BHP.AX` for the Australian Securities Exchange.

### 1. Daily Results

Gets trading data for the day (as long as the trading day has closed).
If it's not a trading day, it will use data from the previous day.
It will also print the updated portfolio and cash. **If any manual trades were made, be sure to copy both and update the code.**
By default the function also reports the Russell 2000 (`^RUT`), IWO, and XBI for comparison.

You can override these benchmarks, the comparison index, and the risk-free rate:

```python
daily_results(
    chatgpt_portfolio,
    cash,
    benchmarks=["^AXJO"],
    comparison_index="^AXJO",
    rf_annual=0.04,
)
```
### Process Portfolio
Handles stop-losses, updates `'chatgpt_portfolio_update.csv'`, and now prompts for manual trades before processing.

When prompted you can enter:

- `b` to log a manual buy (ticker, shares, buy price, and stop loss)
- `s` to log a manual sell (ticker, shares, and sell price)
- press **Enter** to skip

Any manual trades are saved to `chatgpt_trade_log.csv`.

### Putting It Together
At the bottom of your script, call:

```python
chatgpt_portfolio = process_portfolio(chatgpt_portfolio, cash)
daily_results(chatgpt_portfolio, cash)
```

`process_portfolio` will ask about manual trades and update the CSV files automatically before `daily_results` prints the day's metrics.
