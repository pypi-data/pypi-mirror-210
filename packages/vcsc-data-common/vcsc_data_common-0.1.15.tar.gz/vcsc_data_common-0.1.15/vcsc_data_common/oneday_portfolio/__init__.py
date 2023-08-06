import json

import requests


class OneDayPortfolio:
    def __init__(self, paper_trading_api_end_point: str):
        self.paper_trading_api_end_point = paper_trading_api_end_point
    
    def update_portfolio(self,data):
        url = f"{self.paper_trading_api_end_point}/portfolio/updateOneDayPortfolio"

        payload = json.dumps({
        "data": data
        })
        headers = {
        'Content-Type': 'application/json'
        }

        requests.request("POST", url, headers=headers, data=payload)
