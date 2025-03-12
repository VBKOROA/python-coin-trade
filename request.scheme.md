# Trading Decision Request

**Objective:**  Determine the optimal trading action (Buy or Wait) for the given cryptocurrency based on recent candlestick data, and define key price levels if a Buy action is recommended. Minimize risk and account for transaction fees.

## Input Data

*   **Candlestick Data (Multiple Timeframes):**
    *   **15-Minute Candles:**
        ```json
        $15m_candle_data
        ```
    *   **5-Minute Candles:**
        ```json
        $5m_candle_data
        ```
        *   *Data Fields (for each candle):*
            *   `time`:  Candle open time (KST).
            *   `open`:  Opening price.
            *   `close`: Closing price.
            *   `high`:  Highest price reached during the candle's period.
            *   `low`:  Lowest price reached during the candle's period.
            *   `volume`:  Trading volume for the candle's period.

*   **Current Market Conditions:**
    *   `current_time`:  $current_time 
    *   `current_price`:  $current_price

* **Fees:**
    * **Transaction Fee:** 0.05% of the transaction amount (Number of Shares * Transaction Price).

## Output (Decision & Rationale)

The response should strictly adhere to the following structure:

1.  **Optimal Action:**  A single word: `Buy` or `Wait`.

2.  **If Buy (and *only* if Buy is the Optimal Action):**
    *   **Target Price:**  A specific numerical price at which to sell for a profit.  Must be higher than the `current_price` + fees.
    *   **Stop-Loss Price:** A specific numerical price at which to sell to limit potential losses. Must be lower than the `current_price`.

3.  **Think:** A concise, step-by-step explanation of the decision-making process.  Each step should be extremely brief (maximum 5 words per step) and focus on the *most critical* observations and logical deductions.  This section *must* demonstrate the reasoning, even if the action is `Wait`. Show your work.