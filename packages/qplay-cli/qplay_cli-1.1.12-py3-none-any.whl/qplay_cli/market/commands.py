import click
import glob
import pandas as pd
from qplay_cli.utils.file_utils import FileUtils
import gdown
import tarfile
from pathlib import Path
from qplay_cli.api_clients.market_api import MarketAPIClient
from qplay_cli.config.qplay_config import QplayConfig


@click.group()
def market():
    pass

def store_dataset(data_source):
    from quantplay.service import market as market_service

    for dataset_type in data_source:
        if dataset_type == "NSE_EQ":
            output = market_service.nse_equity_path
        elif dataset_type == "NSE_OPT":
            output = market_service.nse_opt_path
        elif dataset_type == "NSE_FUT":
            output = market_service.nse_fut_path
        elif dataset_type == "NSE_MARKET_DATA":
            output = market_service.nse_market_data_path
        elif dataset_type == "MCX":
            output = market_service.mcx_path
        else:
            continue

        for interval in data_source[dataset_type]:
            Path(output).mkdir(parents=True, exist_ok=True)
            file_path = output + "{}.tar.gz".format(interval)

            url = data_source[dataset_type][interval]
            gdown.download(url=url, output=file_path, quiet=False, fuzzy=True)

            file = tarfile.open(file_path)
            file.extractall(output)
            file.close()

@market.command()
def download_sample_data():
    credentials = QplayConfig.get_credentials()
    access_token = credentials['DEFAULT']['access_token']
    data_source = MarketAPIClient().get_data_source(access_token, type="SAMPLE_DATA_SOURCE")

    store_dataset(data_source)


@market.command()
@click.option('--interval', default=None)
@click.option('--dataset', default=None)
def download_data(interval, dataset):
    validate_download_interval(interval)
    validate_datset(dataset)

    credentials = QplayConfig.get_credentials()
    access_token = credentials['DEFAULT']['access_token']
    data_source = MarketAPIClient().get_data_source(access_token, type="DATA_SOURCE", dataset_type=dataset)
    store_dataset({
        dataset : {
            interval : data_source[dataset][interval]
        }
    })

def validate_download_interval(interval):
    if interval == None:
        print("--interval [5minute/minute/day] argument is missing")
        print("For more info re-run the command using --help argument")
        exit(1)

def validate_interval(interval, allowed_intervals):
    if interval == None:
        print(f"--interval {allowed_intervals} argument is missing")
        print("For more info re-run the command using --help argument")
        exit(1)
    if interval not in allowed_intervals:
        print("interval must be in [5minute/15minute/day]")
        exit(1)

def validate_datset(dataset):
    if dataset == None:
        print("--dataset [NSE_EQ/NSE_OPT] argument is missing")
        print("For more info re-run the command using --help argument")
        exit(1)

@market.command()
@click.option('--interval', default=None)
@click.option('--dataset', default=None)
@click.option('--dataset_path', default=None)
@click.option('--contains', default=None)
def create_data(interval, dataset, contains, dataset_path):
    from quantplay.service import market as market_service
    interval_map = {
        "5minute": "5min",
        "3minute": "3min",
        "15minute": "15min",
        "30minute": "30min",
        "day": "1d"
    }

    validate_interval(interval, list(interval_map.keys()))

    if dataset_path is None:
        if dataset == "NSE_EQ":
            dataset_path = market_service.nse_equity_path
        elif dataset == "NSE_OPT":
            dataset_path = market_service.nse_opt_path
        elif dataset == "NSE_FUT":
            dataset_path = market_service.nse_fut_path
        else:
            print("Dataset must be [NSE_EQ/NSE_OPT]")
            exit(1)

    path = "{}minute/".format(dataset_path)

    stocks = [file.replace(path, '').replace('.csv', '') for file in glob.glob("{}*".format(path)) if 'csv' in file]


    FileUtils.create_directory_if_not_exists("{}{}".format(dataset_path, interval))
    for stock in stocks:
        if contains is not None:
            if contains not in stock:
                continue
        print("Processing {}".format(stock))
        df = pd.read_csv("{}{}.csv".format(path, stock))

        df["date"] = pd.to_datetime(df["date"])

        df = df.groupby(pd.Grouper(key='date', freq=interval_map[interval])).agg({
            "symbol": "first",
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum"
        }).reset_index()

        df = df[df.date.dt.time.astype(str) < "15:30:00"]

        if interval == "day":
            df.loc[:, 'date'] = df.date.astype(str) + " 09:15:00"
            df.loc[:, 'date'] = pd.to_datetime(df.date)
        df[df.close>0].to_csv("{}{}/{}.csv".format(dataset_path, interval, stock), index=False)
