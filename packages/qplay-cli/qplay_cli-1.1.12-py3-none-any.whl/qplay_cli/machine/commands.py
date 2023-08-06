from qplay_cli.api_clients.instance_api import InstanceAPIClient
from qplay_cli.config.qplay_config import QplayConfig
from qplay_cli.api_clients.user_api import UserAPIClient
import click
import subprocess
import os
from tabulate import tabulate
import pandas as pd

@click.group()
def machine():
    pass

@machine.command()
def launch():
    credentials = QplayConfig.get_credentials()
    access_token = credentials['DEFAULT']['access_token']

    print("Enter lease time in hours")
    lease_time = input()


    instance_data = InstanceAPIClient().get_instances(access_token)['data']
    user_info = UserAPIClient().get_info(access_token)

    df = pd.DataFrame(instance_data)
    print(tabulate(df, headers='keys', tablefmt='psql'))
    print("Available funds {}".format(user_info['funds']))

    print("Pick an instance type {}".format(df['instance type'].unique()))
    instance_type = input()

    response = InstanceAPIClient().launch_machine(access_token, lease_time, instance_type)
    print(response['message'])
    print("Wait for 2-3 minutes, while we process your request")

@machine.command()
def ssh():
    credentials = QplayConfig.get_credentials()
    access_token = credentials['DEFAULT']['access_token']

    info = UserAPIClient().get_info(access_token)

    if 'machine_ip' in info and info['machine_ip'] != False:
        bshCmd = 'ssh -i "{}/user-machine.pem" ubuntu@{}'.format(QplayConfig.config_path, info['machine_ip'])
        os.system(bshCmd)
    else:
        print("No live machine found, please rent a machine")

@machine.command()
def terminate():
    credentials = QplayConfig.get_credentials()
    access_token = credentials['DEFAULT']['access_token']

    response = InstanceAPIClient().terminate(access_token)
    print(response['message'])

@machine.command()
@click.option('--dataset_name', default=None)
def pull(dataset_name):
    if dataset_name == None:
        print("--dataset_name [NSE_EQ/NSE_OPT/NSE_FUT/NSE_MARKET_DATA] argument is missing")
        return

    credentials = QplayConfig.get_credentials()
    access_token = credentials['DEFAULT']['access_token']

    response = InstanceAPIClient().pull(access_token, dataset_name)
    print(response['message'])