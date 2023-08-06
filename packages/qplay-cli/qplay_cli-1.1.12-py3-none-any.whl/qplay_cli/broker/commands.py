import click
from quantplay.config.qplay_config import QplayConfig
from qplay_cli.api_clients.user_api import UserAPIClient
import codecs
import pickle

@click.group()
def broker():
    pass

@broker.command()
@click.option('--broker_name', default=None)
def generate_token(broker_name):
    from quantplay.broker.zerodha import Zerodha
    from quantplay.broker.angelone import AngelOne

    if broker_name == None:
        print("--broker_name [Zerodha/AngelOne] argument is missing")
        exit(1)
    if broker_name not in ["Zerodha", "AngelOne"]:
        print("broker_name must be in [Zerodha/AngelOne]")
        exit(1)

    credentials = QplayConfig.get_credentials()
    access_token = credentials['DEFAULT']['access_token']

    if broker_name == "Zerodha":
        Zerodha(user_id=QplayConfig.get_value("zerodha_username"),
                api_key=QplayConfig.get_value("zerodha_api_key"),
                api_secret=QplayConfig.get_value("zerodha_api_secret"),
                totp=QplayConfig.get_value("zerodha_totp_unique_id"),
                password=QplayConfig.get_value("zerodha_password"))
        zerodha_wrapper = QplayConfig.get_value(Zerodha.zerodha_wrapper)
        UserAPIClient().update_info(access_token,
                                    {
                                        'zerodha_wrapper': zerodha_wrapper,
                                        'preferred_broker': "Zerodha"
                                    })
    elif broker_name == "AngelOne":
        AngelOne()
        angelone_wrapper = QplayConfig.get_value(AngelOne.angelone_wrapper)
        UserAPIClient().update_info(access_token, {
            'angel_one_wrapper' : angelone_wrapper,
            'angelone_wrapper': angelone_wrapper,
            'preferred_broker' : "AngelOne"
        })
    QplayConfig.save_config('preferred_broker', broker_name)
    print("Token generated Successfully")



    