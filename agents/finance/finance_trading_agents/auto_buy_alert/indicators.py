"""Technical indicators for auto-buy-alert. Pure functions over pandas Series."""
import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    """Simple moving average."""
    return series.rolling(window=window, min_periods=window).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Wilder's RSI."""
    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss
    out = 100.0 - (100.0 / (1.0 + rs))
    # When there are no losses over the window, RSI is defined as 100.
    out = out.where(avg_loss != 0, 100.0)
    return out


def sma_value_and_slope(close: pd.Series, window: int):
    """Return (latest SMA value, is_rising) or (None, None) if not enough data.

    is_rising compares the latest SMA to its value 5 bars earlier.
    """
    if len(close) < window:
        return None, None
    s = sma(close, window)
    cur = s.iloc[-1]
    if cur != cur:  # NaN
        return None, None
    if len(s) >= 6 and s.iloc[-6] == s.iloc[-6]:
        rising = bool(cur > s.iloc[-6])
    else:
        rising = None
    return float(cur), rising
