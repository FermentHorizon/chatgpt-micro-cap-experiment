
"""Plot ChatGPT portfolio performance against a benchmark index.

The script loads logged portfolio equity, fetches comparison index data,
and renders a chart. Core behaviour remains unchanged; the code is simply
reorganised and commented for clarity.
"""

import argparse
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from typing import cast

DATA_DIR = "Start Your Own"
PORTFOLIO_CSV = f"{DATA_DIR}/chatgpt_portfolio_update.csv"


def load_portfolio_details(
    baseline_equity: float, baseline_date: pd.Timestamp | None
) -> pd.DataFrame:
    """Load portfolio equity history and prepend a baseline row.

    Parameters
    ----------
    baseline_equity:
        Dollar value used for the synthetic starting equity.
    baseline_date:
        Date assigned to the baseline equity. If ``None`` the earliest
        portfolio date is used. When the CSV has no data the baseline date is
        set to ``pd.Timestamp.today()``.
    """

    chatgpt_df = pd.read_csv(PORTFOLIO_CSV)
    chatgpt_totals = chatgpt_df[chatgpt_df["Ticker"] == "TOTAL"].copy()
    chatgpt_totals["Date"] = pd.to_datetime(chatgpt_totals["Date"])

    if baseline_date is None:
        if not chatgpt_totals.empty:
            baseline_date = chatgpt_totals["Date"].min()
        else:
            baseline_date = pd.Timestamp.today()

    baseline_row = pd.DataFrame({"Date": [baseline_date], "Total Equity": [baseline_equity]})
    return pd.concat([baseline_row, chatgpt_totals], ignore_index=True).sort_values("Date")


def download_index(
    ticker: str, start_date: pd.Timestamp, end_date: pd.Timestamp
) -> pd.DataFrame:
    """Download index prices and normalise to a $100 baseline."""
    idx = yf.download(
        ticker, start=start_date, end=end_date + pd.Timedelta(days=1), progress=False
    )
    idx = cast(pd.DataFrame, idx)
    idx = idx.reset_index()
    if isinstance(idx.columns, pd.MultiIndex):
        idx.columns = idx.columns.get_level_values(0)
    initial_price = idx["Close"].iloc[0]
    scaling_factor = 100 / initial_price
    idx[f"{ticker} Value ($100 Invested)"] = idx["Close"] * scaling_factor
    return idx


def main(
    baseline_equity: float,
    start_date: pd.Timestamp | None,
    end_date: pd.Timestamp | None,
    benchmark_index: str,
) -> None:
    """Generate and display the comparison graph."""
    chatgpt_totals = load_portfolio_details(baseline_equity, start_date)

    if start_date is None:
        start_date = chatgpt_totals["Date"].min()
    if end_date is None:
        end_date = chatgpt_totals["Date"].max()

    benchmark_df = download_index(benchmark_index, start_date, end_date)

    plt.figure(figsize=(10, 6))
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.plot(
        chatgpt_totals["Date"],
        chatgpt_totals["Total Equity"],
        label="ChatGPT ($100 Invested)",
        marker="o",
        color="blue",
        linewidth=2,
    )
    plt.plot(
        benchmark_df["Date"],
        benchmark_df[f"{benchmark_index} Value ($100 Invested)"],
        label=f"{benchmark_index} ($100 Invested)",
        marker="o",
        color="orange",
        linestyle="--",
        linewidth=2,
    )

    final_date = chatgpt_totals["Date"].iloc[-1]
    final_chatgpt = float(chatgpt_totals["Total Equity"].iloc[-1])
    final_spx = benchmark_df[f"{benchmark_index} Value ($100 Invested)"].iloc[-1]

    plt.text(
        final_date, final_chatgpt + 0.3, f"+{final_chatgpt - baseline_equity:.1f}%", color="blue", fontsize=9
    )
    plt.text(
        final_date, final_spx + 0.9, f"+{final_spx - 100:.1f}%", color="orange", fontsize=9
    )
    plt.title(f"ChatGPT's Micro Cap Portfolio vs. {benchmark_index}")
    plt.xlabel("Date")
    plt.ylabel("Value of $100 Investment")
    plt.xticks(rotation=15)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot portfolio performance")
    parser.add_argument(
        "--baseline-equity",
        type=float,
        default=100.0,
        help="Starting equity value used for normalisation",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        help="Start date for the chart (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        help="End date for the chart (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--benchmark-index",
        type=str,
        default="^SPX",
        help="Ticker for comparison index (e.g. ^AXJO)",
    )
    args = parser.parse_args()

    start = pd.to_datetime(args.start_date) if args.start_date else None
    end = pd.to_datetime(args.end_date) if args.end_date else None

    main(args.baseline_equity, start, end, args.benchmark_index)

