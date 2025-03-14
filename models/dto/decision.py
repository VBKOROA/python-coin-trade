class Decision:
    def __init__(self, decision: dict):
        self.up_chance = decision["up_chance"]
        self.down_chance = decision["down_chance"]
        self.details = decision["details"]
        
    def set_current_price(self, current_price: int):
        self.current_price = current_price
        
    def set_market(self, market: str):
        self.market = market
        
    def __str__(self):
        return f"Decision(up_chance={self.up_chance}, down_chance={self.down_chance}, details={self.details})"