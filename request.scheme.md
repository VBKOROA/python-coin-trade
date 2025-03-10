# Trading Decision Request

**Request:** Analyze the provided recent candlestick data to develop the following trading strategy:

1.  **Optimal Action:** (Buy / Wait)
2.  **If Buy:**
    *   **Target Price:** A price at sell to take a profit.
    *   **Stop-Loss Price:** A price at sell to limit potential losses.
3.  **Reason:** Clear and concise justification for the above decisions (minimize sentence as possible)

## Recent Candlestick Data
- `time`: begin time of candle (KST)
- `open`: opening price
- `close`: closing price
- `high`: high price
- `low`: low price
- `volume`: accumulated trading volume

### 15 Minute Candles
```yaml
$15m_candle_data
```

### 1 Hour Candles
```yaml
$1h_candle_data
```

### Current price
$current_price

## Additional Considerations
*   Please make a decision based on the current data, as no further data will be provided.
*   Please consider fees.
    *   **Fee** = `Transaction Amount (Number of Shares x Transaction Price) x 0.05%`
*   Think step by step by step by step by step.