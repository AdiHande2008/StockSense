# 📈 StockSense AI

### Transparent, Educational Next-Session Stock Direction Predictor for Indian Equities (NSE/BSE)

> **"Truth before novelty."** StockSense AI predicts whether a liquid Indian stock's next trading session will close **UP** or **DOWN** using strict chronological machine learning, transparently evaluated against a Majority-Class Baseline.

---

## 🌟 Executive Summary

Predicting short-term stock movements is notoriously difficult. Many online tools fake accuracy by leaking future information into training or inventing arbitrary price targets. 

**StockSense AI** is built on scientific honesty and engineering rigor:
- **Binary Direction Target:** Predicts whether $\text{Close}_{t+1} > \text{Close}_t$ (**UP**) or $\le \text{Close}_t$ (**DOWN**).
- **Leakage-Safe Features:** All technical indicators (RSI-14, SMA 5/20, Volatility, Lagged Returns) are computed strictly from completed past sessions.
- **Strict Chronological Splits:** The past 80% of historical dates train the model; the subsequent 20% untouched holdout evaluates it. Zero random shuffling.
- **Majority-Class Baseline Benchmark:** The AI model is directly compared with a naive baseline (always guessing the most frequent class). If the model doesn't beat the baseline, it is transparently reported.
- **10 Liquid Starter Stocks:** Curated Indian large-caps across banking, IT, energy, consumer, and auto sectors.

---

## 🏛️ Supported Starter Universe (NSE)

| # | Symbol | Company | Sector |
|---|---|---|---|
| 1 | **RELIANCE** | Reliance Industries Ltd. | Energy / Conglomerate |
| 2 | **TCS** | Tata Consultancy Services Ltd. | Information Technology |
| 3 | **INFY** | Infosys Ltd. | Information Technology |
| 4 | **HDFCBANK** | HDFC Bank Ltd. | Banking & Financial Services |
| 5 | **ICICIBANK** | ICICI Bank Ltd. | Banking & Financial Services |
| 6 | **SBIN** | State Bank of India | Banking & Public Sector |
| 7 | **BHARTIARTL** | Bharti Airtel Ltd. | Telecommunications |
| 8 | **ITC** | ITC Ltd. | Consumer Goods & FMCG |
| 9 | **LT** | Larsen & Toubro Ltd. | Engineering & Infrastructure |
| 10 | **TATAMOTORS**| Tata Motors Ltd. | Automotive |

---

## 🏗️ Architecture & Folder Structure

```text
StockSense/
├── docs/                        # Complete project specifications & design
│   ├── STOCKSENSE_AI_DESIGN.md  # 30-Day Master Design & Architecture Blueprint
│   ├── PROJECT_CHARTER.md       # Day 1 Scope & Guardrails
│   └── DATA_SOURCE_DECISION.md  # Day 2 Market Data Source Evaluation
│
├── backend/                     # Python + FastAPI + Scikit-Learn Engine
│   ├── app/
│   │   ├── api/v1/              # REST Endpoints (Health, Instruments, Predictions, Methodology, Watchlist)
│   │   ├── core/                # Configuration & Settings
│   │   ├── db/                  # SQLite / PostgreSQL Database Engine
│   │   ├── models/              # SQLAlchemy Database Entities
│   │   ├── schemas/             # Pydantic API Data Contracts
│   │   ├── ml/                  # Feature Extraction & Model Pipelines
│   │   └── jobs/                # Data Ingestion & Seeding Automation
│   ├── artifacts/               # Serialized Scikit-Learn Model Files (.joblib)
│   ├── stocksense.db            # SQLite Database (Auto-created on first run)
│   ├── requirements.txt         # Python Dependencies
│   └── run_backend.py           # One-Click Backend Launcher
│
├── frontend/                    # Next.js 16 + React 19 + Tailwind CSS + TypeScript
│   ├── src/app/
│   │   ├── page.tsx             # Interactive Dashboard & Analytics Suite
│   │   ├── layout.tsx           # Base HTML shell & theme
│   │   └── globals.css          # Tailwind CSS styling
│   └── package.json             # Frontend Dependencies
│
├── .gitignore                   # Excludes binaries, .env, and build artifacts
├── .env.example                 # Configuration Template
└── README.md                    # Project Documentation & Implementation Guide
```

---

## 🚀 Beginner-Friendly Implementation Guide

You do **not** need advanced programming knowledge to run StockSense AI. Follow these two simple steps:

### Prerequisites
- **Python 3.10+** (Already installed on your system)
- **Node.js 18+** (Already installed on your system)

---

### Step 1: Launch the Backend (FastAPI & ML Engine)

1. Open PowerShell or Terminal and navigate to the backend folder:
   ```powershell
   cd C:\Users\ADITYA\StockSense\backend
   ```
2. Install dependencies (if not already installed):
   ```powershell
   pip install -r requirements.txt
   ```
3. Run the one-click server script:
   ```powershell
   python run_backend.py
   ```

✨ **What happens automatically:**
- The database schema is initialized (`stocksense.db`).
- 1 full year of historical daily prices (2,450 sessions) for all 10 Indian equities is populated.
- Scikit-learn pipelines extract past-only features, perform strict chronological splits, and train the models.
- All 10 models are saved to `backend/artifacts/`.
- The FastAPI server starts at **`http://127.0.0.1:8000`**.
- Interactive Swagger documentation opens at **`http://127.0.0.1:8000/docs`**.

---

### Step 2: Launch the Frontend (Next.js Dashboard)

1. Open a **second** PowerShell or Terminal window:
   ```powershell
   cd C:\Users\ADITYA\StockSense\frontend
   ```
2. Start the development server:
   ```powershell
   npm run dev
   ```
3. Open your browser and visit:
   ```text
   http://localhost:3000
   ```

🎉 **You're all set!** The dashboard will automatically detect the backend on port 8000, displaying real-time predictions, interactive price curves, technical indicators, and baseline comparisons.

---

## 🧠 Machine Learning Methodology

### 1. Label Formulation
For each trading date $t$, the prediction target is binary:
$$y_t = \begin{cases} 1 \ (\text{UP}) & \text{if } \text{Close}_{t+1} > \text{Close}_t \\ 0 \ (\text{DOWN}) & \text{if } \text{Close}_{t+1} \le \text{Close}_t \end{cases}$$
*(Price ties are classified as DOWN to prevent optimistic bias).*

### 2. Leakage-Safe Feature Contract
All features are calculated solely using data available up to day $t$:
- **Lagged Returns:** 1-day, 2-day, and 5-day percentage price change.
- **Trend Moving Averages:** Simple Moving Average ratio: $\frac{\text{SMA}_5 - \text{SMA}_{20}}{\text{SMA}_{20}}$.
- **Rolling Volatility:** 5-day standard deviation of daily returns.
- **Volume Ratio:** $\frac{\text{Volume}_t}{\text{SMA}_5(\text{Volume})}$.
- **Momentum (RSI-14):** 14-period Relative Strength Index.
- **Calendar Day:** Day of the week (Monday = 0 to Friday = 4).

### 3. Chronological Evaluation Gate
- **Train Split (80%):** Earliest dates in the historical time series.
- **Holdout Test Split (20%):** Strictly future trading dates never exposed during model training or feature normalization.
- **Comparison Benchmark:** Evaluated against the **Majority-Class Baseline** using **Balanced Accuracy**, Precision, Recall, and Confusion Matrices.

---

## 📡 REST API Reference

The backend exposes a fully typed, documented OpenAPI interface:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | System health, database state, and model count |
| `GET` | `/api/v1/instruments` | List of all 10 supported Indian stocks with latest prices |
| `GET` | `/api/v1/instruments/NSE/{symbol}` | Profile and latest quote for a single instrument |
| `GET` | `/api/v1/instruments/NSE/{symbol}/prices?range=1mo` | Historical OHLCV series for interactive charts |
| `GET` | `/api/v1/instruments/NSE/{symbol}/prediction/latest` | Latest UP/DOWN forecast, probability, and holdout metrics |
| `GET` | `/api/v1/methodology` | Public disclosure of features, split rules, and baseline definitions |
| `GET` | `/api/v1/watchlist` | Retrieve saved user watchlist |
| `POST` | `/api/v1/watchlist` | Add or toggle an instrument in the watchlist |

Interactive API documentation with live testing is available at **`http://127.0.0.1:8000/docs`**.

---

## 🔒 Security & Data Licensing Transparency

- **Data Source:** EODHD End-of-Day Daily Historical Series.
- **Licensing Constraint:** EODHD's personal/free tier is authorized for **private, local learning and educational demonstrations only**. It is not licensed for public redistribution or commercial trading services.
- **Educational Guardrail:** StockSense AI is strictly an academic project. It does **not** give buy/sell signals, target price forecasts, or profit claims.

---

## 👥 Authors & Credits

Built as part of the **StockSense AI 30-Day Student Project**.
- **Frontend:** Next.js 16, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Python, SQLAlchemy, Uvicorn
- **Machine Learning:** Scikit-Learn, Pandas, NumPy, Joblib
