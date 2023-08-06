import requests
import json


class MarketAPIClient:
    BASE_PROD_URL = "https://7tpcay1yyk.execute-api.ap-south-1.amazonaws.com/prod"

    def __init__(self):
        pass

    def get_data_source(self, access_token, dataset_type=None, type=None):
        input = {
            "access_token" : str(access_token)
        }
        if dataset_type != None:
            input['dataset_type'] = dataset_type
        input['type'] = type
        x = requests.post(
            MarketAPIClient.BASE_PROD_URL + "/get_data_source",
            data=json.dumps(input))
        response = json.loads(x.text)

        if response['error'] == True:
            print(response['message'])
            quit()

        return response['data']
