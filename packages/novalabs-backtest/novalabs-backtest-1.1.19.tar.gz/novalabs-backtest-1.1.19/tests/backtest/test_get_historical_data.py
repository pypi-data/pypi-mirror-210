import time
from datetime import datetime, timedelta

from novalabs.strategies.macd_strategy import StratBacktest


def asserts_get_historical_data(test: dict) -> None:
    strategy = StratBacktest(
        exchange=test["exchange"],
        list_pairs=test["list_pairs"],
        start=datetime(2023, 1, 1),
        end=datetime(2023, 4, 1),
        candle=test["candle"],
        max_holding=timedelta(minutes=720),
        tp_sl_delta=0.01,
        api_key=test["api_key"],
        api_secret=test["api_secret"],
        passphrase=test["passphrase"],
    )

    start_time = time.time()
    strategy.get_historical_data(pair=test["pair"])
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")

    print(f"Test get_historical_data for {test['exchange'].upper()} SUCCESSFUL")


def test_get_historical_data() -> None:
    all_test = [
        {
            "exchange": "binance",
            "list_pairs": ["BTCUSDT", "ETHUSDT", "XRPUSDT"],
            "pair": "BTCUSDT",
            "candle": "1m",
            "api_key": "",
            "api_secret": "",
            "passphrase": "",
        },
        {
            "exchange": "bybit",
            "list_pairs": ["BTCUSDT", "ETHUSDT", "XRPUSDT"],
            "api_key": "",
            "api_secret": "",
            "passphrase": "",
            "pair": "BTCUSDT",
            "candle": "1m",
        },
        {
            "exchange": "okx",
            "list_pairs": ["BTC-USDT-SWAP", "ETH-USDT-SWAP", "XRP-USDT-SWAP"],
            "pair": "BTC-USDT-SWAP",
            "candle": "1m",
            "api_key": "",
            "api_secret": "",
            "passphrase": "",
        },
        {
            "exchange": "kucoin",
            "list_pairs": ["XBTUSDTM", "ETHUSDTM", "XRPUSDTM"],
            "pair": "XBTUSDT",
            "candle": "1m",
            "api_key": "",
            "api_secret": "",
            "passphrase": "",
        },
        {
            "exchange": "oanda",
            "list_pairs": ["GBP_SGD", "GBP_AUD", "NZD_SGD"],
            "pair": "GBP_SGD",
            "candle": "1m",
            "api_key": "",
            "api_secret": "",
            "passphrase": "",
        },
    ]
    for test in all_test:
        asserts_get_historical_data(test)


test_get_historical_data()
