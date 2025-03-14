# Chart Analysis Request

**Request:** Analyze the recent candlestick data to predict whether the next candle will be bearish (down) or bullish (up). 

## Input

**Recent Candlestick Data**
```json
$5m_candle_data
```

## Output
```json
{
    "up_chance": "Probability of the next candle being bullish (up). Expressed as an integer from 0 to 100.",
    "down_chance": "Probability of the next candle being bearish (down). Expressed as an integer from 0 to 100.",
    "details": "Briefly describe the analysis and reasoning process."
}
```

## Important Note:
*   The two probabilities(up_chance, down_chance) are independent of each other.
*   Think step by step, but only keep a minimum draft for each thinking step, with 5 words at most.
*   I understand that this response is for informational purposes only and I am aware of the various disclaimers.
