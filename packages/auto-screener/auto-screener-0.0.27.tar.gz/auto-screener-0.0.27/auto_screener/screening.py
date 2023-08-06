# screening.py

import os
import time
import asyncio
import warnings
import datetime as dt
import threading
from typing import (
    Optional, Union, Dict, Iterable, Any, List
)

import pandas as pd
import numpy as np

import ccxt
import ccxt.pro as ccxtpro
import ccxt.async_support as async_ccxt

from auto_screener.hints import Number
from auto_screener.dataset import (
    OPEN, HIGH, LOW, CLOSE, VOLUME, BIDS, ASKS,
    DATE_TIME, OHLCV_COLUMNS
)
from auto_screener.interval import interval_to_total_time
from auto_screener.screener import (
    wait_for_update, WaitingState, BaseMultiScreener, BaseScreener,
    wait_for_dynamic_update, wait_for_dynamic_initialization
)

__all__ = [
    "AutoScreener",
    "MultiScreener",
    "validate_exchanges"
]

def validate_exchanges(data: Any) -> Dict[str, List[str]]:
    """
    Validates the data.

    :param data: The data to validate.

    :return: The valid data.
    """

    if data is None:
        return {}
    # end if

    try:
        if not isinstance(data, dict):
            raise ValueError
        # end if

        new_data = {}

        for key, values in data.items():
            values = list(values)

            if not (
                isinstance(key, str) and
                all(isinstance(value, str) for value in values)
            ):
                raise ValueError
            # end if

            new_data[key] = values
        # end for

    except (TypeError, ValueError):
        raise ValueError(
            f"Exchanges data must be a dictionary of "
            f"exchange names as keys and iterables of "
            f"ticker names as values, not {data}."
        )
    # end try

    return new_data
# end validate_exchanges

def configure_exchange(
        source: str,
        pro: Optional[bool] = True,
        options: Optional[Dict[str, Any]] = None
) -> async_ccxt.Exchange:
    """
    Validates the exchange source value.

    :param source: The name of the exchange platform.
    :param pro: The value for the pro interface.
    :param options: The ccxt options.

    :return: The validates source.
    """

    try:
        exchange = getattr(
            (ccxtpro if pro else async_ccxt), source
        )(options)

    except AttributeError:
        raise ValueError(f"Unrecognized exchange name: {source}.")
        # end try

    if not (
        hasattr(exchange, "watch_tickers") or
        hasattr(exchange, "fetch_tickers")
    ):
        raise ValueError(
            f"Exchange {exchange} must have at least one of the "
            f"methods 'fetch_tickers', or 'watch_tickers'."
        )
        # end if
    # end if

    return exchange
# end configure_exchange

def ohlcv_to_dataset(data: Iterable[Iterable]) -> pd.DataFrame:
    """
    Adjusts the dataset to an asset Open, High, Low, Close, Bids, Asks, Volume dataset.

    :param data: The data to adjust.

    :return: The asset dataset.
    """

    data = pd.DataFrame(data)

    index_column_name = list(data.columns)[0]

    data.index = pd.to_datetime(data[index_column_name], unit="ms")
    del data[index_column_name]
    data.index.name = DATE_TIME
    data.columns = list(OHLCV_COLUMNS)

    return data
# end ohlcv_to_dataset

class AutoScreener(BaseScreener):
    """
    A class to represent a live asset data builder.

    Using this class, you can create a screener object to
    screen the market ask and bid data for a specific asset in
    a specific exchange at real time.

    You can also use it to build real time datasets of Open
    High Low Close Volume, with Bids and Asks.

    Parameters:

    - ticker:
        The ticker symbol of an asset to screen.

    - source:
        The name of the exchange platform to screen data from.

    - locaion:
        The saving location for the saved data of the screener.

    - interval:
        The interval for the time between data points in the dataset.

    - delay:
        The delay to wait between each data fetching.

    - screener:
        The screener object to connect to for creating the dataset.

    - length:
        An initial dataset length to start with.

    - pro:
        The value to use the pro interface.

    - options:
        The ccxt options for the backend screening process.

    - cencel:
        The time to cancel screening process after no new data is fetched.

    >>> from auto_screener.screening import AutoScreener
    >>> from auto_screener.screener import wait_for_initialization
    >>> from auto_screener.interval import interval_to_total_time
    >>>
    >>> interval = "1m"
    >>>
    >>> dataset = AutoScreener(
    >>>     ticker="BTC/USD", source="binance", interval=interval
    >>> )
    >>>
    >>> dataset.run(wait=True)
    >>>
    >>> print(dataset.market.iloc[-1].splitlines()[0])
    >>>
    >>> while True:
    >>>     print(dataset.market.iloc[-1].splitlines()[-1])
    >>>
    >>>     wait_for_update(dataset, delay=interval_to_total_time(interval))
    """

    modifiers = BaseScreener.modifiers
    modifiers.excluded.append('task')

    INTERVAL = "1m"

    PRO = False

    OPTIONS = {}

    CANCEL = 0
    LENGTH = 0

    BIDS = BIDS
    ASKS = ASKS

    COLUMNS = (
        OPEN, HIGH, LOW, CLOSE,
        ASKS, BIDS, VOLUME
    )

    def __init__(
            self,
            ticker: str,
            source: str,
            interval: Optional[str] = None,
            pro: Optional[bool] = True,
            data: Optional[pd.DataFrame] = None,
            length: Optional[Union[bool, int]] = None,
            delay: Optional[Union[Number, dt.timedelta]] = None,
            location: Optional[str] = None,
            options: Optional[Dict[str, Any]] = None,
            cancel: Optional[Union[Number, dt.timedelta]] = None
    ) -> None:
        """
        Defines the class attributes.

        :param ticker: The ticker of the asset.
        :param source: The exchange to get source data from.
        :param interval: The interval for the data.
        :param data: The base dataset of the asset to add to.
        :param length: The length of the base dataset.
        :param location: The saving location for the data.
        :param delay: The delay for the process.
        :param pro: The value for the pro interface.
        :param options: The ccxt options.
        :param cancel: The time to cancel the waiting.
        """

        super().__init__(
            ticker=ticker, source=source, delay=delay,
            location=location, cancel=cancel
        )

        self.interval = interval or self.INTERVAL

        self.options = options or {}

        self.pro = pro

        self.task = None

        self.market = self.validate_data(data, length=length)
    # end __init__

    def validate_data(self, data: Any, length: Optional[int]) -> pd.DataFrame:
        """
        Validates the asset data value.

        :param data: The asset data.
        :param length: The length of the data to add.

        :return: The validates source.
        """

        if not all(
            hasattr(self, name) for name in ["source", "interval"]
        ):
            raise AttributeError(
                "Source and interval attributes must be defined "
                "before attempting to validate the data parameter data."
            )
        # end if

        if (
            (data is None) and
            (
                (length is None) or
                (length == 0) or
                (length is False) or
                (
                    isinstance(length, int) and
                    not (0 < length <= 500)
                )
            )
        ):
            data = pd.DataFrame(
                {column: [] for column in self.COLUMNS},
                index=[]
            )

        elif (data is None) and (isinstance(length, int)):
            if 0 < length <= 500:
                try:
                    exchange = getattr(ccxt, self.source)(self.options)

                    data = self.data_to_dataset(
                        exchange.fetch_ohlcv(
                            symbol=self.ticker,
                            timeframe=self.interval,
                            limit=length
                        )
                    )

                except Exception as e:
                    warnings.warn(str(e))

                    data = pd.DataFrame(
                        {column: [] for column in self.COLUMNS},
                        index=[]
                    )
                # end try

            else:
                raise ValueError(
                    f"Length must be a positive int between "
                    f"1 and 500 when data is not defined, "
                    f"not: {length}."
                )
            # end if
        # end if

        return data
    # end validate_data

    def data_to_dataset(self, data: Iterable[Iterable]) -> pd.DataFrame:
        """
        Adjusts the dataset to an asset Open, High, Low, Close, Bids, Asks, Volume dataset.

        :param data: The data to adjust.

        :return: The asset dataset.
        """

        data = ohlcv_to_dataset(data=data)

        if len(self.market) == 0:
            asks = [np.nan] * len(data)
            bids = [np.nan] * len(data)

        else:
            asks = (
                self.market[self.ASKS].iloc
                [-len(data):].values[:]
            )
            bids = (
                self.market[self.BIDS].iloc
                [-len(data):].values[:]
            )
        # end if

        data[self.ASKS].values[:] = asks
        data[self.BIDS].values[:] = bids

        return data[list(self.COLUMNS)]
    # end data_to_dataset

    def dataset_path(
            self, location: Optional[str] = None
    ) -> str:
        """
        Creates the path to the saving file for the screener object.

        :param location: The saving location of the dataset.

        :return: The saving path for the dataset.
        """

        return super().dataset_path(location=location).replace(
            '.csv', f'_{self.interval}.csv'
        )
    # end dataset_path

    def __getstate__(self) -> Dict[str, Any]:
        """
        Returns the data of the object.

        :return: The state of the object.
        """

        data = self.__dict__.copy()

        data["screening_process"] = None
        data["timeout_process"] = None
        data["task"] = None

        return data
    # end __getstate__

    async def async_get_market(self) -> Dict[str, Number]:
        """
        Gets the market data.

        :return: The bids and asks.
        """

        exchange = configure_exchange(
            source=self.source.lower(), pro=self.pro,
            options=self.options
        )

        method = None

        if hasattr(exchange, "fetch_tickers"):
            method = exchange.fetch_tickers

        elif hasattr(exchange, "watch_tickers"):
            method = exchange.watch_tickers
        # end if

        data = await method(symbols=[self.ticker])

        ticker = list(data.keys())[0]

        data[ticker][VOLUME.lower()] = data[ticker]["quoteVolume"]
        data[ticker][self.ASKS.lower()] = data[ticker]["ask"]
        data[ticker][self.BIDS.lower()] = data[ticker]["bid"]

        data = {
            key: data[ticker][key.lower()] for key in
            self.COLUMNS
        }

        if any(np.isnan(value) for value in data.values()):
            ohlcv = await exchange.fetch_ohlcv(
                self.ticker, timeframe='1m', limit=1
            )

            ohlcv = {
                column: value for column, value in zip(
                    [OPEN, HIGH, LOW, CLOSE, VOLUME], ohlcv
                ) if np.isnan(data[column])
            }

            data.update(ohlcv)
        # end if

        await exchange.close()

        return data
    # end async_get_market

    async def async_update_market(self) -> None:
        """Updates the market data."""

        data = await self.async_get_market()

        self.market.loc[dt.datetime.now()] = data
    # end async_update_market

    def update_market(self) -> None:
        """Updates the market data."""

        asyncio.run(self.async_update_market())
    # end update_market

    def get_market(self) -> Dict[str, Number]:
        """Gets the market data."""

        return asyncio.run(self.async_get_market())
    # end get_market

    async def async_run_loop(self) -> None:
        """Runs the processes of price screening."""

        self.running = True

        delay = interval_to_total_time(self.interval).seconds

        while self.running:
            start = time.time()

            try:
                await self.async_update_market()

            except Exception as e:
                self.terminate()

                raise RuntimeError(
                    f"Could not complete task. {str(e)}"
                ) from e
            # end try

            end = time.time()

            if delay:
                time.sleep(max([delay - (end - start), 0]))
            # end if
        # end while
    # end async_run

    def run_loop(self) -> None:
        """Runs the process of the price screening."""

        task = self.async_run_loop()

        try:
            loop = asyncio.new_event_loop()

            self.task = loop.create_task(task)

            if not loop.is_running():
                loop.run_forever()
            # end if

        except RuntimeError:
            asyncio.run(task)
        # end try
    # end run_loop

    def run_new_loop(self) -> None:
        """Runs the process of the price screening."""

        task = self.async_run_loop()

        try:
            loop = asyncio.new_event_loop()

            self.task = loop.create_task(task)

            if not loop.is_running():
                loop.run_forever()
            # end if

        except RuntimeError:
            asyncio.run(task)
        # end try
    # end run_loop

    def stop(self) -> None:
        """Stops the screening process."""

        super().stop()

        if self.task is not None:
            self.task.cancel()
        # end if
    # end stop

    def terminate(self) -> None:
        """Stops the trading process."""

        super().terminate()
    # end terminate
# end LiveAssetData

class MultiScreener(BaseMultiScreener):
    """
    A class to represent an asset price screener.

    Using this class, you can create a screener object to
    screen the market ask and bid data for a specific asset in
    a specific exchange at real time.

    Parameters:

    - exchanges:
        The data of exchanges and their tickers to screen.

    - interval:
        The interval for the time between data points in the dataset.

    - delay:
        The delay to wait between each data fetching.

    - length:
        An initial dataset length to start with.

    - locaion:
        The saving location for the saved data of the screener.

    - pro:
        The value to use the pro interface.

    - options:
        The ccxt options for the backend screening process.

    - cencel:
        The time to cancel screening process after no new data is fetched.

    >>> from auto_screener.screening import MultiScreener
    >>> from auto_screener.screener import wait_for_initialization
    >>>
    >>> screener = MultiScreener(
    >>>     data={
    >>>         "binance": ["BTC/USDT", "AAVE/EUR"],
    >>>         "bittrex": ["GRT/USD", "BTC/USD"]
    >>>     }
    >>> )
    >>>
    >>> screener.run(wait=True)
    >>>
    >>> while True:
    >>>     screener.wait_for_update(delay=1)
    """

    INTERVAL = AutoScreener.INTERVAL

    PRO = AutoScreener.PRO

    OPTIONS = AutoScreener.OPTIONS

    ASKS = AutoScreener.ASKS
    BIDS = AutoScreener.BIDS

    LENGTH = AutoScreener.LENGTH
    CANCEL = AutoScreener.CANCEL

    COLUMNS = AutoScreener.COLUMNS

    screeners: List[AutoScreener]

    def __init__(
            self,
            data: Dict[str, Iterable[str]],
            interval: Optional[str] = None,
            delay: Optional[Union[Number, dt.timedelta]] = None,
            length: Optional[Union[int, bool]] = None,
            location: Optional[str] = None,
            pro: Optional[bool] = None,
            options: Optional[Dict[str, Any]] = None,
            cancel: Optional[Union[Number, dt.timedelta]] = None,
            screeners: Optional[Iterable[AutoScreener]] = None
    ) -> None:
        """
        Defines the class attributes.

        :param interval: The interval of the data to load.
        :param data: The data of exchanges and their tickers.
        :param pro: The value to use the pro interface.
        :param location: The saving location for the data.
        :param delay: The delay between each data fetching request.
        :param length: The length of the data to get in each request.
        :param options: The ccxt options.
        :param cancel: The time it takes to cancel a non-updating screener.
        :param screeners: The create_screeners for the multi-screener object.
        """

        super().__init__(
            delay=delay, cancel=cancel, location=location
        )

        self.options = options or self.OPTIONS
        self.interval = interval or self.INTERVAL
        self.length = length or self.LENGTH
        self.pro = pro or self.PRO

        self.exchanges = self.validate_exchanges(data)

        self.market: Dict[str, Dict[str, Optional[AutoScreener]]] = {}

        self.screeners: List[AutoScreener] = list(screeners or [])
    # end Screener

    @staticmethod
    def validate_exchanges(data: Any) -> Dict[str, List[str]]:
        """
        Validates the data.

        :param data: The data to validate.

        :return: The valid data.
        """

        return validate_exchanges(data=data)
    # end validate_data

    def create_screener(
            self,
            ticker: str,
            source: str,
            container: Optional[Dict[str, Optional[AutoScreener]]] = None
    ) -> Dict[str, Optional[AutoScreener]]:
        """
        Creates the screener and inserts it into the container.

        :param container: The container to contain the new screener.
        :param ticker: The ticker of the screener.
        :param source: The source of the data.
        """

        if container is None:
            container = {}
        # end if

        try:
            container[ticker] = AutoScreener(
                ticker=ticker, source=source, options=self.options,
                interval=self.interval, pro=self.pro,
                delay=self.delay, length=self.length
            )

        except ValueError as e:
            warnings.warn(str(e))

            container[ticker] = None
        # end try

        return container
    # end create_screener

    def create_screeners(
            self,
            tickers: Iterable[str],
            source: str,
            container: Optional[Dict[str, Optional[AutoScreener]]] = None,
    ) -> Dict[str, Optional[AutoScreener]]:
        """
        Creates the screener and inserts it into the container.

        :param container: The container to contain the new screener.
        :param tickers: The ticker of the screener.
        :param source: The source of the data.
        """

        if container is None:
            container = {}
        # end if

        for ticker in tickers:
            threading.Thread(
                target=self.create_screener,
                kwargs=dict(
                    container=container,
                    ticker=ticker, source=source
                )
            ).start()
        # end for

        return container
    # end create_screeners

    def load_datasets(self, location: Optional[str] = None) -> None:
        """
        Loads the datasets of the create_screeners.

        :param location: The saving or loading path for the dataset.
        """

        for screener in self.screeners:
            if os.path.exists(screener.dataset_path() or location):
                try:
                    screener.load_dataset(
                        location=location or screener.location
                    )

                except Exception as e:
                    warnings.warn(str(e))
                # end try
            # end if
        # end for
    # end load_datasets

    def save_datasets(self, location: Optional[str] = None) -> None:
        """
        Saves the datasets of the create_screeners.

        :param location: The saving or loading path for the dataset.
        """

        for screener in self.screeners:
            try:
                screener.save_dataset(
                    location=location or screener.location
                )

            except Exception as e:
                warnings.warn(str(e))
            # end try
        # end for
    # end load_datasets

    def wait_for_initialization(
            self,
            delay: Optional[Union[Number, dt.timedelta]] = None,
            once: Optional[bool] = False,
            stop: Optional[Union[bool, int]] = False,
            cancel: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
    ) -> WaitingState:
        """
        Waits for all the create_screeners to update.

        :param delay: The delay for the waiting.
        :param once: The value to get data only once.
        :param stop: The value to stop the screener objects.
        :param cancel: The time to cancel the waiting.

        :returns: The total delay.
        """

        return wait_for_dynamic_initialization(
            self.screeners, delay=delay, once=once,
            stop=stop, cancel=cancel
        )
    # end wait_for_initialization

    def wait_for_update(
            self,
            delay: Optional[Union[Number, dt.timedelta]] = None,
            once: Optional[bool] = False,
            stop: Optional[Union[bool, int]] = False,
            cancel: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
    ) -> WaitingState:
        """
        Waits for all the create_screeners to update.

        :param delay: The delay for the waiting.
        :param once: The value to get data only once.
        :param stop: The value to stop the screener objects.
        :param cancel: The time to cancel the waiting.

        :returns: The total delay.
        """

        return wait_for_dynamic_update(
            self.screeners, delay=delay, once=once,
            stop=stop, cancel=cancel
        )
    # end wait_for_update

    def initialize_screeners(self) -> None:
        """Initializes the create_screeners."""

        self.market.clear()

        for exchange, tickers in self.exchanges.items():
            self.market[exchange] = {}

            threading.Thread(
                target=self.create_screeners,
                kwargs=dict(
                    container=self.market[exchange],
                    tickers=tickers, source=exchange
                )
            ).start()
        # end for

        while (
            sum(len(screeners) for screeners in self.market.values()) <
            sum(len(tickers) for tickers in self.exchanges.values())
        ):
            time.sleep(1)
        # end while

        self.screeners.clear()

        for exchange in self.market.values():
            for ticker, screener in exchange.copy().items():
                if isinstance(screener, AutoScreener):
                    self.screeners.append(screener)

                else:
                    exchange.pop(ticker)
                # end if
            # end for
        # end for
    # end initialize_screeners

    async def async_get_market(self) -> Dict[str, Dict[str, Dict[str, Number]]]:
        """Gets the market data."""

        market = {exchange: {} for exchange in self.exchanges}

        for screener in self.screeners:
            market[screener.source][screener.ticker] = (
                await screener.async_get_market()
            )
        # end for

        return market
    # end async_get_market

    async def async_update_market(self) -> None:
        """Updates the market data."""

        for screener in self.screeners:
            await screener.async_update_market()
        # end for
    # end async_update_market

    def update_market(self) -> None:
        """Updates the market data."""

        asyncio.run(self.async_update_market())
    # end update_market

    def get_market(self) -> Dict[str, Dict[str, Dict[str, Number]]]:
        """Gets the market data."""

        return asyncio.run(self.async_get_market())
    # end get_market

    def terminate(self) -> None:
        """Stops the screening process."""

        super().terminate()

        for screener in self.screeners:
            screener.terminate()
        # end for
    # end terminate

    def blocking(self) -> bool:
        """
        returns the value of the process being blocked.

        :return: The value.
        """

        return self.block
    # end blocking

    def run(
            self,
            save: Optional[bool] = True,
            block: Optional[bool] = False,
            wait: Optional[Union[bool, Number, dt.timedelta, dt.datetime]] = False,
            timeout: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
    ) -> None:
        """
        Runs the process of the price screening.

        :param save: The value to save the data.
        :param block: The value to block the execution.
        :param timeout: The valur to add a timeout to the process.
        :param wait: The value to wait after starting to run the process.
        """

        for screener in self.screeners:
            screener.run(
                timeout=timeout, wait=False,
                block=False, save=save
            )
        # end for

        if block:
            self.block = True

            while self.block:
                pass
            # end while
        # end if

        if isinstance(wait, dt.datetime):
            wait = wait - dt.datetime.now()
        # end if

        if isinstance(wait, dt.timedelta):
            wait = wait.total_seconds()
        # end if

        if isinstance(wait, bool) and wait:
            self.wait_for_initialization()

        elif isinstance(wait, (int, float)):
            time.sleep(wait)
        # end if
    # end run
# end Screener