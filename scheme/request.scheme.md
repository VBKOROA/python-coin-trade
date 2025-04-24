# Chart Analysis Request

**Request:** Analyze the candlestick data and provide a direct trading action recommendation (buy, sell, or wait).

## Input

**Candlestick Data**
```json
$5m_candle_data
```

## Output
```json
{
    "action": "Recommend one of the following: 'buy', 'sell', or 'wait'",
    "reason": "Briefly explain the rationale behind your recommended action"
}
```

## Important Note:
*   **Data limitation:** Base analysis *solely* on the provided data. No external data is permitted.
*   **Disclaimer:** The output is for informational purposes *only* and is not financial advice. I understand the inherent risks of market prediction and acknowledge that this analysis is not a guarantee of future performance.
