class Decision:
    def __init__(self, decision: dict):
        self.action = decision["action"]
        self.reason = decision["reason"]
        self.current_price: int = None
        self.market: str = None
        
    def set_current_price(self, current_price: int):
        self.current_price = current_price
        
    def set_market(self, market: str):
        self.market = market
        
    def __str__(self):
        return f"Decision(action={self.action}, reason={self.reason}, price={self.current_price}, market={self.market})"