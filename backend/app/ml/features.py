import pandas as pd
import numpy as np

def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0.0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean()
    
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)

def extract_features(df_prices: pd.DataFrame, include_target: bool = True) -> pd.DataFrame:
    """
    Computes leakage-safe technical features strictly from past and present prices.
    Expects df_prices sorted by trading_date ascending with columns:
    ['trading_date', 'open', 'high', 'low', 'close', 'volume']
    """
    df = df_prices.copy()
    df = df.sort_values("trading_date").reset_index(drop=True)
    
    # 1. Past-only Returns
    df["return_1d"] = df["close"].pct_change(1)
    df["return_2d"] = df["close"].pct_change(2)
    df["return_5d"] = df["close"].pct_change(5)
    
    # 2. Moving Averages & Trend
    df["sma_5"] = df["close"].rolling(window=5).mean()
    df["sma_20"] = df["close"].rolling(window=20).mean()
    df["sma_ratio"] = (df["sma_5"] - df["sma_20"]) / df["sma_20"]
    
    # 3. MACD (12 EMA - 26 EMA) & 9-period Signal Line
    ema_12 = df["close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = (ema_12 - ema_26) / df["close"]
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]
    
    # 4. Bollinger Bands & %B
    rolling_std = df["close"].rolling(window=20).std()
    upper_band = df["sma_20"] + (2 * rolling_std)
    lower_band = df["sma_20"] - (2 * rolling_std)
    band_width = (upper_band - lower_band).replace(0, np.nan)
    df["bollinger_b"] = ((df["close"] - lower_band) / band_width).fillna(0.5)
    
    # 5. Candlestick Anatomy (Intraday Buyer/Seller Pressure)
    hl_range = (df["high"] - df["low"]).replace(0, np.nan)
    df["body_ratio"] = ((df["close"] - df["open"]) / hl_range).fillna(0.0)
    
    # 6. Volatility & Volume Ratios
    df["volatility_5d"] = df["return_1d"].rolling(window=5).std().fillna(0.0)
    vol_sma_5 = df["volume"].rolling(window=5).mean().replace(0, np.nan)
    df["volume_ratio_5d"] = (df["volume"] / vol_sma_5).fillna(1.0)
    
    # 7. Momentum (RSI 14)
    df["rsi_14"] = compute_rsi(df["close"], period=14)
    
    # 8. Calendar Feature
    df["trading_date_dt"] = pd.to_datetime(df["trading_date"])
    df["day_of_week"] = df["trading_date_dt"].dt.dayofweek
    
    # Warm-up check columns
    warmup_cols = ["sma_20", "bollinger_b", "macd_hist"]
    
    if include_target:
        # Target: 1 if NEXT trading day's close > today's close; 0 otherwise (ties labelled 0)
        next_close = df["close"].shift(-1)
        df["target"] = (next_close > df["close"]).astype(int)
        
        # Drop rows where tomorrow's close is not known (the latest row)
        # and drop initial warm-up period
        df_valid = df.dropna(subset=warmup_cols).iloc[:-1].copy()
        return df_valid
    else:
        # For inference: keep the latest row
        df_valid = df.dropna(subset=warmup_cols).copy()
        return df_valid

FEATURE_COLUMNS = [
    "return_1d",
    "return_2d",
    "return_5d",
    "sma_ratio",
    "macd_hist",
    "bollinger_b",
    "body_ratio",
    "volatility_5d",
    "volume_ratio_5d",
    "rsi_14",
    "day_of_week"
]
