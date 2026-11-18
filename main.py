from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from math import isfinite

app = FastAPI(title="1-Minute Binary Market Analysis Bot", version="1.0.0")

class Candle(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

class AnalyzeRequest(BaseModel):
    symbol: str = Field(default="UNKNOWN")
    timeframe: str = Field(default="1m")
    candles: List[Candle]

def ema(values, period):
    if len(values) < period:
        return None
    alpha = 2 / (period + 1)
    value = sum(values[:period]) / period
    for x in values[period:]:
        value = alpha * x + (1 - alpha) * value
    return value

def rsi(values, period=14):
    if len(values) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(values)):
        change = values[i] - values[i-1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

@app.get("/")
def home():
    return {"status": "online", "service": "Binary Cortex Bot", "timeframe": "1m"}

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    if req.timeframe.lower() not in ("1m", "1min", "1-minute", "1 minute"):
        raise HTTPException(status_code=400, detail="This bot is configured for 1-minute candles.")
    if len(req.candles) < 30:
        raise HTTPException(status_code=400, detail="Send at least 30 recent 1-minute candles.")
    closes = [c.close for c in req.candles]
    for c in req.candles:
        if not all(isfinite(v) for v in (c.open, c.high, c.low, c.close)):
            raise HTTPException(status_code=400, detail="Candle values must be finite numbers.")
        if c.high < max(c.open, c.close, c.low) or c.low > min(c.open, c.close, c.high):
            raise HTTPException(status_code=400, detail="Invalid OHLC candle values.")

    e9, e21 = ema(closes, 9), ema(closes, 21)
    current_rsi = rsi(closes)
    if e9 is None or e21 is None or current_rsi is None:
        raise HTTPException(status_code=400, detail="Not enough candle data.")

    bullish = e9 > e21 and closes[-1] > e9 and 50 < current_rsi < 70
    bearish = e9 < e21 and closes[-1] < e9 and 30 < current_rsi < 50

    if bullish:
        signal, bias = "CALL", "BULLISH"
        reason = "EMA 9 is above EMA 21, price is above EMA 9, and RSI supports upward momentum."
    elif bearish:
        signal, bias = "PUT", "BEARISH"
        reason = "EMA 9 is below EMA 21, price is below EMA 9, and RSI supports downward momentum."
    else:
        signal, bias = "WAIT", "UNCLEAR"
        reason = "The indicators do not agree strongly. Avoid forcing a trade."

    return {
        "symbol": req.symbol,
        "timeframe": "1m",
        "signal": signal,
        "market_bias": bias,
        "indicators": {
            "ema_9": round(e9, 6),
            "ema_21": round(e21, 6),
            "rsi_14": round(current_rsi, 2),
            "last_close": closes[-1]
        },
        "reason": reason,
        "risk_note": "Educational technical analysis only. Signals are not guaranteed; confirm with your own analysis and test on a demo account."
    }
