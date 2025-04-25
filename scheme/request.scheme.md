Analyze the provided 5-minute candlestick data and decide the next trading action.

**Current Time:**
```
$current_time
```

**Candlestick Data (5m):**
```json
$5m_candle_data
```

**Output Format:**
Return a JSON object with the following structure:
```json
{
  "action": "'buy', 'sell', or 'wait'",
  "reason": "Brief explanation for the action."
}
```

**IMPORTANT:**
Comprehensively consider the meaning of individual candlesticks, patterns formed by multiple candles, the current market trend, support/resistance levels, and trading volume.