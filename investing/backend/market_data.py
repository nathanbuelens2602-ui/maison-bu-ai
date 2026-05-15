import yfinance as yf
import time

_price_cache: dict = {}  # ticker -> (price, timestamp)
CACHE_TTL = 300  # 5 minutes


def get_current_price(ticker: str) -> float | None:
    now = time.time()
    if ticker in _price_cache:
        price, ts = _price_cache[ticker]
        if now - ts < CACHE_TTL:
            return price
    try:
        data = yf.Ticker(ticker)
        info = data.fast_info
        price = float(info.last_price)
        _price_cache[ticker] = (price, now)
        return price
    except Exception:
        return None


def get_prices_bulk(tickers: list[str]) -> dict[str, float | None]:
    result = {}
    now = time.time()
    to_fetch = []
    for t in tickers:
        if t in _price_cache:
            price, ts = _price_cache[t]
            if now - ts < CACHE_TTL:
                result[t] = price
                continue
        to_fetch.append(t)
    if to_fetch:
        try:
            data = yf.download(to_fetch, period="1d", progress=False, auto_adjust=True)
            if len(to_fetch) == 1:
                close = data["Close"]
                if not close.empty:
                    price = float(close.iloc[-1])
                    _price_cache[to_fetch[0]] = (price, now)
                    result[to_fetch[0]] = price
                else:
                    result[to_fetch[0]] = None
            else:
                for t in to_fetch:
                    try:
                        price = float(data["Close"][t].dropna().iloc[-1])
                        _price_cache[t] = (price, now)
                        result[t] = price
                    except Exception:
                        result[t] = None
        except Exception:
            for t in to_fetch:
                result[t] = None
    return result


def clear_cache():
    _price_cache.clear()
