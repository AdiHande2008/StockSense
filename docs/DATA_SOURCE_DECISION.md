# StockSense AI — Day 2 Data-Source Decision

**Decision date:** 23 October 2026  
**Status:** Approved for private/local student development only  
**Chosen source:** EODHD End-of-Day Historical Data API (free personal tier)

## Plain-English decision

We will use EODHD's daily historical-price API while learning and building the first private version of StockSense AI. It is a practical choice because it supplies daily open, high, low, close, adjusted close, and volume data; the free tier permits up to 20 API calls per day and one year of price history. One year is enough for the project's first fair train/validation/test experiment.

This choice **does not authorize a public website to show its price charts or price data**. EODHD's terms limit the free/personal tier to private, non-commercial use and prohibit displaying or redistributing the information. The project may be demonstrated locally to the student/evaluator while in this private-learning phase. A publicly accessible deployment must wait for a data licence/plan that explicitly permits that display, or use separately licensed/publicly shareable data.

## Why this is the best beginner-friendly starting point

| Need | EODHD free personal tier | Result |
|---|---|---|
| Daily OHLCV data | Provides end-of-day open, high, low, close, adjusted close, and volume. | Meets the model's data needs. |
| Historical depth | Past year of history is available on the free plan. | Enough for a small, honest initial evaluation; not enough to claim decades of robustness. |
| Small starter universe | 20 requests/day; one request retrieves one stock's time series. | The 10-stock starter list can be refreshed once per day within the limit. |
| Indian market aim | EODHD identifies both National Stock Exchange of India and BSE India in its market coverage. | Individual ticker availability still needs verification before the universe is final. |
| Cost | No credit card required for the free learning tier. | Suitable while learning. |
| Public deployment | Personal-use terms prohibit public display/redistribution. | **Not approved** without a suitable commercial/data-display licence. |

## How we will use it

1. The user creates a free EODHD account later, using their own email, and keeps the API key private.
2. The backend—not the browser—uses the key to download one completed daily record series for each supported stock.
3. The project stores only the data needed for the local/private student demonstration and labels the source/date clearly.
4. The project updates after the market day has finished; it does not claim live or real-time pricing.
5. Before any public deployment, we stop and review the intended audience, data-display rights, attribution, retention, and exchange-specific terms.

## Verification required before implementation

- Confirm each proposed NSE/BSE stock has a valid provider-specific ticker and at least one year of usable daily history.
- Confirm the provider's raw/adjusted-price behavior for the selected tickers; do not mix them unknowingly.
- Confirm there are no material date gaps, duplicate trading dates, impossible OHLC values, or unexplained volume fields.
- Keep a record of the retrieval date, source URL, source terms, and the data's latest available session.

If fewer than six of the starter symbols validate cleanly, we will reduce the scope to the symbols that do or change provider before building the prediction model.

## Options considered and rejected for the MVP

| Option | What was attractive | Why it is not the selected free private-development source |
|---|---|---|
| Yahoo Finance through `yfinance` | Common in tutorials; convenient historical data. | Its documentation says the Yahoo Finance API is intended for personal use only. It is not an appropriate basis for a public project, and we will not rely on an unofficial wrapper as the source-of-truth integration. |
| Alpha Vantage | Official daily-series API documentation includes a BSE example (`RELIANCE.BSE`) and an education-project request path. | Free daily output is limited to the latest 100 points; full history and adjusted daily data are premium features. Its terms also require a rights review for the intended use. It remains a fallback only if written educational access/support makes it suitable. |
| Twelve Data | Officially lists NSE instruments and supports a time-series endpoint. | Its free/individual plans are for internal, non-commercial use, and its terms prohibit external display/redistribution unless expressly authorized. India EOD data is not a free-tier public-display solution. |
| EODHD paid/commercial plan | Broader history and potentially suitable service level. | Costs money and still requires explicit confirmation that the selected plan and exchange rights allow public display. Not justified before a working private MVP exists. |

## Source links reviewed

- [EODHD end-of-day historical data documentation](https://eodhd.com/financial-apis/api-for-historical-data-and-volumes) — fields, free-tier one-year history, one-symbol requests, and daily call limit context.
- [EODHD pricing](https://eodhd.com/pricing) — free tier and student-discount information.
- [EODHD terms and conditions](https://eodhd.com/financial-apis/terms-conditions) — personal-use restrictions and prohibition on displaying/redistributing information.
- [EODHD market-status coverage](https://eodhd.com/marketplace/tradinghours/markets-g20/) — identifies BSE India and the National Stock Exchange of India in its listed market coverage.
- [Alpha Vantage daily-series documentation](https://www.alphavantage.co/documentation/) and [support page](https://www.alphavantage.co/support/api-key/) — BSE example, 100-point/free versus full-history/premium distinction, and educational-project route.
- [Twelve Data NSE exchange page](https://twelvedata.com/exchanges/xnse?group=analysis), [pricing](https://twelvedata.com/pricing), and [terms](https://twelvedata.com/terms) — availability and display/redistribution constraints.
- [yfinance legal disclaimer](https://ranaroussi.github.io/yfinance/) — personal-use limitation reminder.

## Rule for the rest of the project

We will never describe the source as exchange-official, real time, fully adjusted, complete, or licensed for public display unless the provider's written terms and our actual plan explicitly support that claim. The website will say **“Data source: EODHD; end-of-day; private student demonstration”** until its data rights change.
