import time
from datetime import datetime, timedelta

from novalabs.strategies.macd_strategy import StratBacktest


def asserts_fast_download_history(test: dict) -> None:
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
    strategy.fast_download_history(pair=test["pair"], list_proxies=test["list_proxies"])
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")

    print(f"Test fast_download_history for {test['exchange'].upper()} SUCCESSFUL")


def test_fast_download_history() -> None:
    all_test = [
        {
            "exchange": "binance",
            "list_pairs": ["BTCUSDT", "ETHUSDT", "XRPUSDT"],
            "pair": "BTCUSDT",
            "candle": "1m",
            "api_key": "",
            "api_secret": "",
            "passphrase": "",
            "list_proxies": [],
        },
        {
            "exchange": "bybit",
            "list_pairs": ["BTCUSDT", "ETHUSDT", "XRPUSDT"],
            "api_key": "",
            "api_secret": "",
            "passphrase": "",
            "pair": "SOLUSDT",
            "candle": "5m",
            "list_proxies": [],
        },
        {
            "exchange": "okx",
            "list_pairs": ["BTC-USDT-SWAP", "ETH-USDT-SWAP", "XRP-USDT-SWAP"],
            "pair": "SOL-USDT-SWAP",
            "candle": "5m",
            "api_key": "",
            "api_secret": "",
            "passphrase": "",
            "list_proxies": [],
        },
        {
            "exchange": "kucoin",
            "list_pairs": ["XBTUSDTM", "ETHUSDTM", "XRPUSDTM"],
            "api_key": "",
            "pair": "XBTUSDTM",
            "candle": "1m",
            "api_secret": "",
            "passphrase": "",
            "list_proxies": [],
        },
        {
            "exchange": "oanda",
            "list_pairs": ["GBP_SGD", "GBP_AUD", "NZD_SGD"],
            "pair": "GBP_SGD",
            "candle": "15m",
            "api_key": "",
            "api_secret": "",
            "passphrase": "",
            "list_proxies": [],
        },
    ]
    for test in all_test:
        asserts_fast_download_history(test)


test_fast_download_history()
