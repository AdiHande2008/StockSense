# StockSense AI — Day 1 Project Charter

**Status:** Confirmed starter scope  
**Purpose:** A simple, educational stock-direction prediction project for learning—not financial advice.

## The project in one sentence

StockSense AI will let a user select a supported Indian NSE/BSE stock and see an educational prediction of whether its closing price may finish **UP** or **DOWN** in the next trading session.

## What the prediction means

- **UP:** the next completed trading session's closing price is higher than today's completed-session closing price.
- **DOWN:** the next completed trading session's closing price is the same or lower.
- The result is a model estimate based on historical daily data. It is not a buy, sell, or profit recommendation.
- The app will always show the last date for which data is available, because markets are closed on weekends and holidays.

## Starter stock universe

The first version will begin with these 10 well-known, liquid Indian shares. This is intentionally a small list so the project remains achievable and easy to test.

| # | Company | Proposed NSE symbol | Sector |
|---:|---|---|---|
| 1 | Reliance Industries | `RELIANCE` | Energy / conglomerate |
| 2 | Tata Consultancy Services | `TCS` | Information technology |
| 3 | Infosys | `INFY` | Information technology |
| 4 | HDFC Bank | `HDFCBANK` | Banking |
| 5 | ICICI Bank | `ICICIBANK` | Banking |
| 6 | State Bank of India | `SBIN` | Banking |
| 7 | Bharti Airtel | `BHARTIARTL` | Telecommunications |
| 8 | ITC | `ITC` | Consumer goods |
| 9 | Larsen & Toubro | `LT` | Engineering / infrastructure |
| 10 | Tata Motors | `TATAMOTORS` | Automotive |

The exact provider-specific symbol spelling and exchange coverage will be verified before downloading data. A symbol can be replaced if the selected data provider cannot reliably supply its daily history.

## What we will build in the first version

- A clean website showing daily price charts for the supported stocks.
- A next-session **UP/DOWN** prediction, clearly marked as educational.
- A simple comparison between the AI model and a basic “always guess the most common result” benchmark.
- A transparent page explaining how the result was tested and its limitations.
- An optional private watchlist for signed-in users.

## What we will not build

- Live intraday prices, automatic trading, broker accounts, or payment features.
- “Buy”/“sell” advice, target prices, profit claims, or guarantees.
- Every Indian stock, cryptocurrency, options, mutual funds, news sentiment, or a chatbot.

## Success for this student project

Success means the website works reliably, the model is evaluated fairly using only past information, and the result is explained honestly—even if the simple benchmark performs as well as or better than the AI model.

## Next milestone

**Day 2:** choose one legitimate daily-price data source and confirm that it can provide usable historical data for this starter list.
