from datetime import datetime, timedelta

from novalabs.strategies.macd_strategy import StratBacktest


def asserts_run_backtest(test: dict) -> None:
    strategy = StratBacktest(
        exchange=test["exchange"],
        list_pairs=test["list_pairs"],
        start=datetime(2023, 1, 1),
        end=datetime(2023, 4, 1),
        candle="15m",
        max_holding=timedelta(minutes=720),
        tp_sl_delta=0.01,
        api_key=test["api_key"],
        api_secret=test["api_secret"],
        passphrase=test["passphrase"],
    )

    df_all_pos, all_stats = strategy.run_backtest(save=True)

    assert len(df_all_pos) > 0

    print(f"Test run_backtest for {test['exchange'].upper()} SUCCESSFUL")


def test_run_backtest() -> None:
    all_test = [
        {
            "exchange": "binance",
            "list_pairs": ["BTCUSDT", "ETHUSDT", "XRPUSDT"],
            "api_key": "",
            "api_secret": "",
            "passphrase": "",
        },
        # {"exchange": "okx", "list_pairs": ["BTC-USDT-SWAP", "ETH-USDT-SWAP", "XRP-USDT-SWAP"],
        #     "api_key": "",
        #     "api_secret": "",
        #     "passphrase": "",},
        # {"exchange": "bybit", "list_pairs": ["BTCUSDT", "ETHUSDT", "XRPUSDT"],
        #     "api_key": "",
        #     "api_secret": "",
        #     "passphrase": "",},
        # {"exchange": "kucoin", "list_pairs": ["XBTUSDTM", "ETHUSDTM", "XRPUSDTM"],
        #     "api_key": "",
        #     "api_secret": "",
        #     "passphrase": "",},
        # {"exchange": "oanda", "list_pairs": ["GBP_SGD", "GBP_AUD", "NZD_SGD"],
        #     "api_key": "",
        #     "api_secret": "",
        #     "passphrase": ""},
    ]
    for test in all_test:
        asserts_run_backtest(test)


test_run_backtest()
