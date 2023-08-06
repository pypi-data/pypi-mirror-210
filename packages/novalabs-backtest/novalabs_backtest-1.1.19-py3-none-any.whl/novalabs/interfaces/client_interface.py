import abc
import asyncio
from typing import Any, List, Union

import aiohttp
import pandas as pd

from novalabs.utils.helpers import get_time_chunks


class ClientInterface(abc.ABC):
    @abc.abstractmethod
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        passphrase: str,
        limit: int,
        batch: int,
        sleep_time: int,
    ) -> None:
        """
        Initialize the exchange API client with the specified credentials and parameters.

        Args:
            key: A string representing the API key for the exchange.
            secret: A string representing the secret key for the exchange.
            passphrase: A string representing the passphrase for the exchange.
            limit: number of candle that can be query at once

        Returns:
            None.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.limit = limit
        self.batch = batch
        self.sleep_time = sleep_time

    @abc.abstractmethod
    def _send_request(
        self, end_point: str, request_type: str, params: dict, signed: bool
    ) -> Union[dict, list]:
        """
        Send a request to the specified exchange API endpoint with the given parameters.

        Args:
            end_point: A string representing the API endpoint to send the request to.
            request_type: A string representing the type of HTTP request to send, e.g. 'GET' or 'POST'.
            params: A dictionary of parameters to include in the request.
            signed: A boolean flag indicating whether to include authentication information in the request.

        Returns:
            A dictionary containing the response data from the API endpoint.

        Raises:
            APIClientError: If there is an error with the API client, such as an invalid API key or missing required parameters.
            APIConnectionError: If there is an error connecting to the API endpoint, such as a network issue or a timeout.
            APIResponseError: If the API endpoint returns an error response, such as a 400 or 500 status code.
        """
        pass

    @abc.abstractmethod
    def get_server_time(self) -> int:
        """
        Retrieve the current server time from the exchange API server.

        Returns:
            An integer value representing the current server time in milliseconds.
        """
        pass

    @abc.abstractmethod
    def get_pairs_info(self, quote_asset: str) -> dict:
        """
        Retrieve information about available trading pairs on the exchange.

        Args:
            quote_asset: A string representing the quote asset to filter the trading pairs by, e.g. 'USDT'.

        Returns:
            A dictionary or list containing information about available trading pairs on the exchange. If there is no
            trading pair matching the quote asset, an empty dictionary or list will be returned.

            The dictionary has the following structure:
            {
                "pair_symbol": {
                    "quote_asset": str,
                    "tick_size": float,
                    "step_size": float,
                    "maxLimitQuantity": float,
                    "maxMarketQuantity": float,
                    "minQuantity": float
                },
                ...
            }
        """

    pass

    @abc.abstractmethod
    def _get_candles(
        self, pair: str, interval: str, start_time: int, end_time: int
    ) -> list:
        """
        Retrieve a batch of historical candlestick data for a specified trading pair, interval, and time range.

        Args:
            pair: A string representing the trading pair to retrieve data for, e.g. 'BTC-USD'.
            interval: A string representing the time interval of the candlesticks to retrieve, e.g. '1h' for 1 hour intervals.
            start_time: An integer representing the start time for the candlestick data in milliseconds since the Unix epoch.
            end_time: An integer representing the end time for the candlestick data in milliseconds since the Unix epoch.

        Returns:
            A dictionary containing the candlestick data for the specified trading pair, interval, and time range, with a
            maximum limit

        """
        pass

    @abc.abstractmethod
    def _get_earliest_timestamp(self, pair: str, interval: str) -> int:
        """
        Retrieve the earliest available timestamp for candlestick data for the specified trading pair and time interval.

        Args:
            pair: A string representing the trading pair to retrieve data for, e.g. 'BTC-USD'.
            interval: A string representing the time interval of the candlesticks to retrieve, e.g. '1h' for 1 hour intervals.

        Returns:
            An integer representing the earliest available timestamp for candlestick data in milliseconds since the Unix epoch.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def _format_data(all_data: list) -> pd.DataFrame:
        """
        Format the raw candlestick data into a standardized pandas dataframe for further analysis.

        Args:
            all_data: A list or dict containing the raw candlestick data from the exchange API endpoint.

        Returns:
            A pandas dataframe containing the formatted candlestick data, including the following columns:
                - open_time: The opening time of the candlestick in milliseconds since the Unix epoch.
                - open: The opening price of the trading pair during the candlestick interval.
                - high: The highest price of the trading pair during the candlestick interval.
                - low: The lowest price of the trading pair during the candlestick interval.
                - close: The closing price of the trading pair during the candlestick interval.
                - volume: The trading volume during the candlestick interval.
                - close_time: The closing time of the candlestick in milliseconds since the Unix epoch.

            The dataframe may also contain additional columns specific to the exchange, such as the number of trades.
        """
        pass

    @abc.abstractmethod
    def get_historical_data(
        self, pair: str, interval: str, start_ts: int, end_ts: int
    ) -> pd.DataFrame:
        """
        Retrieve full historical candlestick data for a specified trading pair and time range, and return it as a
        standardized pandas dataframe.

        Args:
            pair: A string representing the trading pair for which to retrieve data, in the format "BTC/USD".
            interval: A string representing the granularity of the candlesticks to retrieve, in units of time (e.g. '1m' for
                1 minute intervals, '1h' for 1 hour intervals, etc.).
            start_ts: An integer representing the starting timestamp in milliseconds for the data to retrieve.
            end_ts: An integer representing the ending timestamp in milliseconds for the data to retrieve.

        Returns:
            A pandas dataframe containing the full historical candlestick data for the specified trading pair and time range,
            formatted as follows:
                - open_time: The opening time of the candlestick in milliseconds since the Unix epoch.
                - open: The opening price of the trading pair during the candlestick interval.
                - high: The highest price of the trading pair during the candlestick interval.
                - low: The lowest price of the trading pair during the candlestick interval.
                - close: The closing price of the trading pair during the candlestick interval.
                - volume: The trading volume during the candlestick interval.
            The dataframe will also contain any additional market data that is available, such as the number of trades.
        """
        pass

    @abc.abstractmethod
    def get_extra_market_data(self, pair: str, interval: str) -> pd.DataFrame:
        """
        Retrieve extra market data for a specified trading pair and time interval, and return it as a Pandas DataFrame.
        It's important to know that those datapoints may not be supported on production

        Args:
            pair: A string representing the trading pair for which to retrieve market data.
            interval: A string representing the time interval for which to retrieve market data.

        Returns:
            A Pandas DataFrame containing extra market data for the specified trading pair and time interval, including
            global and top long/short account and position ratios, taker long/short ratios, and open interest.
        """
        pass

    def get_most_traded_pairs(self, quote_asset: str, top_n: int = 20) -> list:
        """
        Returns the top 'n' most traded pairs for a given quote asset.

        This function uses the `get_pairs_info` method to retrieve all trading pairs
        for the provided quote asset. It then sorts these pairs based on their 24-hour
        trading volume in descending order, and returns the top 'n' pairs.

        Args:
            quote_asset (str): The quote asset to consider for trading pairs.
            top_n (int, optional): The number of top-most traded pairs to return. Defaults to 20.

        Returns:
            list: A list of the top 'n' most traded pairs as strings.
        """
        all_pairs = self.get_pairs_info(quote_asset=quote_asset)
        df = pd.DataFrame(all_pairs).T
        df = df.sort_values(by="24h_volume", ascending=False)
        return list(df.head(top_n).index)

    @abc.abstractmethod
    async def _get_async_candles(
        self,
        session: aiohttp.ClientSession,
        pair: str,
        interval: str,
        start_time: int,
        end_time: int,
        proxy: str = "",
    ) -> pd.DataFrame:
        """Retrieves OHLCV (Open, High, Low, Close, Volume) data asynchronously from Binance.

        This method makes a GET request to the Exchange API to download candlestick data for a given
        cryptocurrency pair and time interval. It returns a pandas DataFrame formatted by the _format_data method.

        Args:
            session (aiohttp.ClientSession): An aiohttp client session for making the API request.
            pair (str): The symbol of the cryptocurrency pair to retrieve data for, e.g. "BTCUSDT".
            interval (str): The time interval for the data, e.g. "1m", "1h", "1d".
            start_time (int): The start time of the data range in milliseconds since Unix Epoch.
            end_time (int): The end time of the data range in milliseconds since Unix Epoch.
            proxy (str): proxy to be used if any.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the formatted candlestick data.

        """
        pass

    async def download_fast_data(
        self,
        pair: str,
        interval: str,
        start_ts: int,
        end_ts: int,
        list_proxies: List[Any] = [],
    ) -> pd.DataFrame:
        """Asynchronously downloads candlestick data from Binance for a given cryptocurrency pair and time interval.

        This method uses aiohttp to asynchronously send GET requests to the Exchange API. It controls the rate of requests
        to comply with the API's rate limit. The downloaded data is then concatenated into a single pandas DataFrame.

        Args:
            pair (str): The symbol of the cryptocurrency pair to retrieve data for, e.g. "BTCUSDT".
            interval (str): The time interval for the data, e.g. "1m", "1h", "1d".
            start_ts (int): The start time of the data range in milliseconds since Unix Epoch.
            end_ts (int): The end time of the data range in milliseconds since Unix Epoch.
            batch (int): The number of requests to send before pausing.
            sleep_time (int): The time to pause (in seconds) after each batch of requests.
            list_proxies (list): List the proxies to be used in the request

        Returns:
            pd.DataFrame: A pandas DataFrame containing the downloaded and formatted candlestick data, sorted by "open_time"
                        and with duplicate "open_time" entries removed.

        """
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            tasks = []

            times = get_time_chunks(
                start_ts=start_ts, end_ts=end_ts, interval=interval, limit=self.limit
            )

            proxy_index = 0
            if list_proxies:
                proxy_url = list_proxies[proxy_index]
            else:
                proxy_url = ""

            request_count = 0
            for _time_ in times:
                task = asyncio.ensure_future(
                    self._get_async_candles(
                        session=session,
                        pair=pair,
                        interval=interval,
                        start_time=_time_[0],
                        end_time=_time_[1],
                        proxy=proxy_url,
                    )
                )
                tasks.append(task)

                request_count += 1
                if request_count % self.batch == 0:
                    await asyncio.sleep(self.sleep_time)
                    if list_proxies:
                        proxy_index = (proxy_index + 1) % len(list_proxies)
                        proxy_url = list_proxies[proxy_index]
                        print(f"Rotating Proxy -- {proxy_url}")

            all_info = await asyncio.gather(*tasks)

            final_df = pd.DataFrame()
            for df in all_info:
                final_df = pd.concat([final_df, df])

            final_df = final_df.sort_values(by="open_time").reset_index(drop=True)
            return final_df.drop_duplicates("open_time").reset_index(drop=True)
