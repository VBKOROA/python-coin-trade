# Chart Analysis Request

**Request:** Analyze the recent candlestick data to predict whether the overall future trend will be upward or downward.

## Input

**Recent Candlestick Data**
```json
$5m_candle_data
```

## Output
```json
{
    "up_chance": "Probability of future upward trend. Expressed as an integer from 0 to 100.",
    "down_chance": "Probability of future downward trend. Expressed as an integer from 0 to 100.",
    "details": "Briefly describe the analysis and reasoning process."
}
```

## Important Note:
*   **Step-by-step reasoning:** Concisely document each analysis step (maximum 5 words per step).
*   **Precise probabilities:** Calculate all probabilities as whole numbers (e.g., 65%, not 65.3%).
*   **Data limitation:** Base analysis *solely* on the provided data. No external data is permitted.
*   **Disclaimer:** The output is for informational purposes *only* and is not financial advice. I understand the inherent risks of market prediction and acknowledge that this analysis is not a guarantee of future performance.
