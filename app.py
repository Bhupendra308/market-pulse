from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Market Pulse Dashboard", layout="wide")

DATA_PATH = Path("data/processed_data.csv")


@st.cache_data
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    numeric_cols = ["price", "volume", "ma_7", "daily_pct_change"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


st.title("Market Pulse - Hybrid Static-Dynamic Analytics")
st.caption("Daily automated ingestion + interactive exploration dashboard.")

data = load_data()

if data.empty:
    st.warning("No data found. Run `python data_engine.py` first.")
    st.stop()

assets = sorted(data["asset_name"].dropna().unique())
selected_asset = st.sidebar.selectbox("Choose an Asset", options=assets)

asset_df = data[data["asset_name"] == selected_asset].copy().sort_values("date")

min_date = asset_df["date"].min().date()
max_date = asset_df["date"].max().date()
date_range = st.sidebar.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
)

filtered = asset_df[
    (asset_df["date"].dt.date >= date_range[0]) & (asset_df["date"].dt.date <= date_range[1])
].copy()

latest_two = filtered.tail(2)
current_price = latest_two["price"].iloc[-1] if not latest_two.empty else float("nan")
yesterday_price = latest_two["price"].iloc[-2] if len(latest_two) > 1 else current_price

delta_value = current_price - yesterday_price
delta_pct = ((delta_value / yesterday_price) * 100) if yesterday_price else 0

col1, col2, col3 = st.columns(3)
col1.metric("Selected Asset", selected_asset)
col2.metric("Current Price", f"{current_price:,.2f}")
col3.metric("vs Yesterday", f"{delta_value:,.2f}", delta=f"{delta_pct:,.2f}%")

price_fig = px.line(
    filtered,
    x="date",
    y=["price", "ma_7"],
    title=f"{selected_asset}: Price vs 7-Day Moving Average",
    labels={"value": "Price", "date": "Date", "variable": "Series"},
)
price_fig.update_layout(legend_title_text="")

volume_fig = px.bar(
    filtered,
    x="date",
    y="volume",
    title=f"{selected_asset}: Daily Volume",
    labels={"volume": "Volume", "date": "Date"},
)

st.plotly_chart(price_fig, use_container_width=True)
st.plotly_chart(volume_fig, use_container_width=True)

st.dataframe(filtered.sort_values("date", ascending=False), use_container_width=True)
