# from novalabs.clients.clients import clients


# def asserts_get_pairs_info(test: dict) -> None:
#     client = clients(
#         exchange=test["exchange"],
#         api_key=test["api_key"],
#         api_secret=test["api_secret"],
#         passphrase=test["passphrase"],
#     )

#     info = client.get_most_traded_pairs(test["quote_asset"], top_n=10)

#     assert type(info) == list
#     assert len(info) == 10

#     print(f"Test get_most_traded_pairs for {test['exchange'].upper()} SUCCESSFUL")


# def test_get_pairs_info() -> None:
#     all_test = [
#         {
#             "exchange": "binance",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "quote_asset": "USDT",
#             "to_test_USDT": True,
#         },
#         {
#             "exchange": "okx",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "quote_asset": "USDT",
#             "to_test_USDT": True,
#         },
#         {
#             "exchange": "bybit",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "quote_asset": "USDT",
#             "to_test_USDT": True,
#         },
#         {
#             "exchange": "kucoin",
#             "api_key": "",
#             "api_secret": "",
#             "passphrase": "",
#             "quote_asset": "USDT",
#             "to_test_USDT": True,
#         },
#         {
#             "exchange": "oanda",
#             "api_key": "101-002-23843409-001",
#             "api_secret": "abbd7fb0eb44869a4a36d0741259b4d7-a20d993e204d17b94294f9f9afbd4b58",
#             "passphrase": "",
#             "quote_asset": "USD",
#             "to_test_USDT": False,
#         },
#     ]
#     for test in all_test:
#         asserts_get_pairs_info(test)


# test_get_pairs_info()
