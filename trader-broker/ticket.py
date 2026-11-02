class IndianBrokerClient:
    def __init__(self, api_key: str, access_token: str):
        self.api_key = api_key
        self.access_token = access_token

    def place_fno_order(self, symbol: str, transaction_type: str, quantity: int, product: str = "MIS", price: float = None):
        order_payload = {
            "exchange": "NFO",
            "tradingsymbol": symbol,
            "transaction_type": transaction_type.upper(),
            "quantity": quantity,
            "product": product.upper(),
            "order_type": "MARKET" if price is None else "LIMIT",
            "price": price
        }
        print(f"[Broker API] Executed F&O Order: {order_payload}")
        return {"status": "SUCCESS", "order_id": "IN_ORD_987654321", "payload": order_payload}

if __name__ == "__main__":
    client = IndianBrokerClient("demo_key", "demo_token")
    print(client.place_fno_order("NIFTY26NOVFUT", "BUY", 25, product="NRML"))
