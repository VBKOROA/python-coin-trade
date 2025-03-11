# Trading Decision Request

**Objective:**  Determine the optimal trading action (Buy or Wait) for the given cryptocurrency based on recent candlestick data, and define key price levels if a Buy action is recommended.  Minimize risk and account for transaction fees.

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
            *   `time`:  Candle open time (KST).  *Crucially, this allows for time-based analysis and pattern recognition.*
            *   `open`:  Opening price.
            *   `close`: Closing price.
            *   `high`:  Highest price reached during the candle's period.
            *   `low`:  Lowest price reached during the candle's period.
            *   `volume`:  Trading volume for the candle's period.  *Higher volume often indicates stronger conviction behind a price movement.*

*   **Current Market Conditions:**
    *   `current_time`:  Current time (KST). *Used to relate the candlestick data to the present moment.*
    *   `current_price`:  Current market price of the asset.

* **Fees:**
    * **Transaction Fee:** 0.05% of the transaction amount (Number of Shares * Transaction Price).

## Output (Decision & Rationale)

The response should strictly adhere to the following structure:

1.  **Optimal Action:**  A single word: `Buy` or `Wait`.

2.  **If Buy (and *only* if Buy is the Optimal Action):**
    *   **Target Price:**  A specific numerical price at which to sell for a profit.  Must be higher than the `current_price` + fees.
    *   **Stop-Loss Price:** A specific numerical price at which to sell to limit potential losses. Must be lower than the `current_price`.

3.  **Think:** A concise, step-by-step explanation of the decision-making process.  Each step should be extremely brief (maximum 5 words per step) and focus on the *most critical* observations and logical deductions.  This section *must* demonstrate the reasoning, even if the action is `Wait`. Show your work.

## Analytical Methodology (Behind the Scenes - What the AI Should Do):

The AI should perform the following analysis, but only the final decision and the concise "Think" steps should be outputted:

1.  **Trend Identification:**
    *   Examine both 15-minute and 5-minute charts.
    *   Identify the *predominant* short-term trend (uptrend, downtrend, or sideways/ranging).  Look for higher highs and higher lows (uptrend), lower highs and lower lows (downtrend), or horizontal price movement (ranging).
    *   Consider the *relationship* between the 5-minute and 15-minute trends. Are they in agreement, or is there divergence?

2.  **Candlestick Pattern Recognition:**
    *   Identify any recognizable candlestick patterns (e.g., bullish engulfing, bearish engulfing, doji, hammer, shooting star, etc.) on *both* timeframes.
    *   Pay particular attention to patterns that occur near potential support or resistance levels.

3.  **Volume Analysis:**
    *   Assess the volume associated with recent price movements.
    *   Increasing volume on upward moves in an uptrend, or increasing volume on downward moves in a downtrend, *confirms* the trend.
    *   Low volume suggests a lack of conviction and potential for a reversal.
    *   Volume spikes can indicate potential turning points.

4.  **Support and Resistance:**
    *   Identify potential support levels (previous lows) and resistance levels (previous highs) on both charts.  These levels often act as price barriers.

5.  **Risk/Reward Assessment (If Considering a Buy):**
    *   **Target Price:**  Set a realistic target price based on identified resistance levels or projected price movements (e.g., extending the current trend).  *Must* account for fees to ensure actual profit.  The target should offer a reasonable reward relative to the risk.
    *   **Stop-Loss Price:**  Set a stop-loss price below a recent swing low or a key support level.  This is to limit losses if the trade goes against the prediction.
    *   **Calculate the potential profit (Target Price - Current Price - Fees) and potential loss (Current Price - Stop-Loss Price - Fees).**  The potential profit should ideally be significantly larger than the potential loss (e.g., a 2:1 or 3:1 risk/reward ratio is often a minimum guideline).

6.  **Decision Making:**
    *   **Buy:**  Only if a clear uptrend is identified, bullish candlestick patterns are present, volume confirms the upward movement, and a favorable risk/reward ratio can be established.
    *   **Wait:**  If the trend is unclear, bearish signals are present, volume is low, or a favorable risk/reward ratio cannot be achieved.  Waiting is a valid trading decision, especially in uncertain conditions.
