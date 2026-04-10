from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf


ASSETS = {
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "GC=F": "Gold Futures",
    "^GSPC": "S&P 500",
    "AAPL": "Apple",
}

OUTPUT_PATH = Path("processed_data.csv")


def fetch_history(symbol: str, lookback_days: int = 30) -> pd.DataFrame:
    """Fetch daily OHLCV data for a symbol and normalize columns."""
    end_date = datetime.now(tz=timezone.utc).date() + timedelta(days=1)
    start_date = end_date - timedelta(days=lookback_days + 7)  # +7 for moving average warm-up

    df = yf.download(
        tickers=symbol,
        start=start_date.isoformat(),
        end=end_date.isoformat(),
        interval="1d",
        auto_adjust=False,
        progress=False,
    )

    if df.empty:
        return pd.DataFrame()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    df = df.reset_index()
    if "Date" not in df.columns:
        df = df.rename(columns={df.columns[0]: "Date"})

    keep_cols = ["Date", "Close", "Volume"]
    available = [c for c in keep_cols if c in df.columns]
    df = df[available].copy()

    df = df.rename(columns={"Close": "price", "Volume": "volume", "Date": "date"})
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["symbol"] = symbol
    df["asset_name"] = ASSETS[symbol]

    return df


def build_dataset() -> pd.DataFrame:
    """Collect all assets and compute analytics columns."""
    frames = []
    for symbol in ASSETS:
        history = fetch_history(symbol=symbol, lookback_days=30)
        if not history.empty:
            frames.append(history)

    if not frames:
        raise RuntimeError("No data returned from upstream provider.")

    data = pd.concat(frames, ignore_index=True)
    data = data.sort_values(["symbol", "date"]).reset_index(drop=True)

    data["ma_7"] = data.groupby("symbol")["price"].transform(lambda s: s.rolling(7).mean())
    data["daily_pct_change"] = data.groupby("symbol")["price"].pct_change() * 100
    data = data.groupby("symbol", group_keys=False).tail(30).reset_index(drop=True)

    output = data[
        ["date", "symbol", "asset_name", "price", "volume", "ma_7", "daily_pct_change"]
    ].copy()
    output["date"] = pd.to_datetime(output["date"])

    for col in ["price", "ma_7", "daily_pct_change"]:
        output[col] = output[col].astype(float).round(4)

    output["volume"] = output["volume"].fillna(0).astype("int64")
    return output


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    dataset = build_dataset()
    dataset.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(dataset)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
