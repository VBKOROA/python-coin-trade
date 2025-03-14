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
*   The two probabilities(up_chance, down_chance) are independent of each other(The sum of up_chance and down_chance can range from 0 to 200.). 
*   Think step by step, but only keep a minimum draft for each thinking step, with 5 words at most.
*   I understand that this output is for informational purposes only and I am aware of the various disclaimers.
