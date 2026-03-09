import yfinance as yf
import pandas as pd
import requests


# ================= ANALYZE STOCK (ACCURATE & STABLE) =================
def analyze_stock(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="5y", interval="1d", auto_adjust=False)
    except Exception:
        return None

    if data.empty or "Close" not in data:
        return None

    # Use Close prices only
    close = data["Close"].dropna()

    if len(close) < 200:
        return None

    # ✅ Accurate prices
    latest_price = float(close.iloc[-1])
    first_price = float(close.iloc[0])

    # ✅ Returns
    total_return = ((latest_price - first_price) / first_price) * 100

    # ✅ CAGR using trading years
    years = len(close) / 252  # approx trading days per year
    cagr = ((latest_price / first_price) ** (1 / years) - 1) * 100

    # ✅ Moving averages
    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()

    latest_ma50 = float(ma50.iloc[-1])
    latest_ma200 = float(ma200.iloc[-1])

    # ✅ RSI (14)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = float(rsi.iloc[-1])

    # ✅ Recommendation logic
    if latest_rsi < 30:
        recommendation = "BUY (Oversold)"
    elif latest_rsi > 70:
        recommendation = "SELL (Overbought)"
    elif latest_ma50 > latest_ma200:
        recommendation = "BUY (Uptrend)"
    else:
        recommendation = "HOLD"

    return {
        "symbol": symbol.upper(),
        "current_price": round(latest_price, 2),
        "total_return": round(total_return, 2),
        "cagr": round(cagr, 2),
        "rsi": round(latest_rsi, 2),
        "recommendation": recommendation
    }


# ================= SEARCH STOCK (EQUITY ONLY) =================
def search_stock(query):
    url = "https://query2.finance.yahoo.com/v1/finance/search"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    params = {
        "q": query,
        "quotesCount": 10,
        "newsCount": 0
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        data = response.json()
    except Exception:
        return []

    results = []

    for item in data.get("quotes", []):
        # ✅ Only real stocks (no options, no crypto)
        if item.get("quoteType") != "EQUITY":
            continue

        symbol = item.get("symbol")
        name = item.get("shortname") or item.get("longname")

        if symbol and name:
            results.append({
                "symbol": symbol,
                "name": name
            })

    return results[:5]
