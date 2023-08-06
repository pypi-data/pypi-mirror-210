import requests
import json
import pandas as pd
from tabulate import tabulate

class StrategyService:

    BASE_PROD_URL = 'https://a8tdizgtbk.execute-api.ap-south-1.amazonaws.com/prod'

    def __init__(self):
        pass

    def subscribe(self, access_token, strategy_name):
        x = requests.post(StrategyService.BASE_PROD_URL + "/subscribe",
                          data=json.dumps({
                              'strategy_name': strategy_name,
                              'access_token': access_token}))

        response = json.loads(x.text)
        print(response['message'])

    def list(self):
        x = requests.post(StrategyService.BASE_PROD_URL + "/list")

        return json.loads(x.text)

    def describe(self):
        strategies = self.list()
        data = []
        for s in strategies:
            entry = {
                "strategy_name": s
            }
            for more_details in strategies[s]:
                entry[more_details] = strategies[s][more_details]
            data.append(entry)

        data = pd.DataFrame(data)
        print(tabulate(data, headers='keys', tablefmt='psql'))



