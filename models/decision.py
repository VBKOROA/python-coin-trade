class Decision:
    def __init__(self, decision: dict):
        self.action = decision["action"]
        self.target_price = 0
        self.stop_loss_price = 0
        
        if self.action == "buy":
            self.target_price = int(decision["target_price"])
            self.stop_loss_price = int(decision["stop_loss_price"])
            
        self.think = decision["think"]
        
    def set_current_price(self, current_price: int):
        self.current_price = current_price
        
    def set_market(self, market: str):
        self.market = market
        
    def __str__(self):
        return f"Action: {self.action}, Target Price: {self.target_price}, Stop Loss Price: {self.stop_loss_price}, Think: {self.think}"