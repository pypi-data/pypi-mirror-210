import requests
import json


class InstanceAPIClient:
    BASE_PROD_URL = "https://h5y8burhuk.execute-api.ap-south-1.amazonaws.com/prod"

    def __init__(self):
        pass

    def terminate(self, access_token):
        x = requests.post(
            InstanceAPIClient.BASE_PROD_URL + "/terminate",
            data=json.dumps(
                {
                    "access_token": str(access_token)
                }))
        response = json.loads(x.text)

        if response['error'] == True:
            print(response['message'])
            quit()

        return response

    def pull(self, access_token, required_datasets):
        x = requests.post(
            InstanceAPIClient.BASE_PROD_URL + "/pull",
            data=json.dumps(
                {
                    "access_token": str(access_token),
                    "required_datasets" : [required_datasets]
                }))
        response = json.loads(x.text)

        if response['error'] == True:
            print(response['message'])
            quit()

        return response

    def get_instances(self, access_token):
        x = requests.post(
            InstanceAPIClient.BASE_PROD_URL + "/get_instances",
            data=json.dumps(
                {
                    "access_token" : str(access_token)
                }))
        response = json.loads(x.text)

        if response['error'] == True:
            print(response['message'])
            quit()

        return response

    def launch_machine(self, access_token, lease_time, instance_type):
        x = requests.post(
            InstanceAPIClient.BASE_PROD_URL + "/launch_instance",
            data=json.dumps(
                {
                    "access_token" : str(access_token),
                    "lease_time" : str(lease_time),
                    "instance_type" : instance_type
                }))
        response = json.loads(x.text)

        if response['error'] == True:
            print(response['message'])
            quit()

        return response