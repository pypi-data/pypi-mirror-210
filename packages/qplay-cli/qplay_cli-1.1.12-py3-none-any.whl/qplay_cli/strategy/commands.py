from qplay_cli.api_clients.instance_api import InstanceAPIClient
from qplay_cli.config.qplay_config import QplayConfig
from qplay_cli.api_clients.strategy_service import StrategyService
import click
import subprocess
import os




@click.group()
def strategy():
    pass

@strategy.command()
def list():
    StrategyService().describe()


@strategy.command()
def subscribe():
    credentials = QplayConfig.get_credentials()
    access_token = credentials['DEFAULT']['access_token']

    StrategyService().describe()

    print("Enter strategy name")
    strategy_name = input()

    StrategyService().subscribe(access_token, strategy_name)