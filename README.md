# 🚀 Market Pulse: Automated Analytics Pipeline

A full-stack financial data platform that automates the collection, processing, and visualization of market trends. 

**Live Demo:** [Insert Your GitHub Pages Link Here]

---

## 🛠️ The Architecture
This project uses a **Hybrid Cloud Architecture** to balance performance and real-time data:

1.  **Data Engine (ETL):** A Python-based engine that fetches market data via `yfinance`.
2.  **Automation (DevOps):** GitHub Actions schedules a daily "cron job" to run the engine and update the dataset.
3.  **Dynamic Dashboard:** A Streamlit application that provides interactive filtering and visualization.
4.  **Static Frontend:** A high-performance landing page hosted on GitHub Pages, embedding the live dashboard.

## 🧰 Tech Stack
- **Language:** Python 3.14
- **Libraries:** Pandas, YFinance, Streamlit, Plotly
- **Automation:** GitHub Actions (CI/CD)
- **Deployment:** GitHub Pages & Streamlit Cloud
- **Styling:** Tailwind CSS

## 📈 Key Features
- **Zero-Manual Maintenance:** The dataset updates every night at 00:00 UTC automatically.
- **Node.js 24 Optimized:** Fully migrated to the latest GitHub Action runners for long-term stability.
- **Interactive Visuals:** Users can filter data by timeframe and asset class in real-time.

---
*Developed by Bhupendra — Focused on Data Engineering & Automation.*
