# feed.py

import threading
import datetime as dt
from typing import (
    Dict, Optional, Iterable, Any,
    Union, Callable, List
)

import pandas as pd

from cryptofeed import FeedHandler
from cryptofeed.types import OrderBook
from cryptofeed.exchanges import EXCHANGE_MAP
from cryptofeed.defines import L2_BOOK

from auto_screener.dataset import BIDS, ASKS
from auto_screener.tickers import Separator
from auto_screener.screener import BaseScreener, BaseMultiScreener
from auto_screener.hints import Number

__all__ = [
    "MarketRecorder",
    "MarketHandler",
    "MarketScreener",
    "add_feeds",
    "create_market",
    "market_screener",
    "market_recorder"
]

Market = Dict[str, Dict[str, pd.DataFrame]]
RecorderParameters = Dict[str, Union[Iterable[str], Dict[str, Callable]]]

def create_market(data: Dict[str, Iterable[str]]) -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    Creates the dataframes of the market data.

    :param data: The market data.

    :return: The dataframes of the market data.
    """

    return {
        source: {
            ticker: pd.DataFrame({BIDS: [], ASKS: []}, index=[])
            for ticker in data[source]
        } for source in data
    }
# end create_market

class MarketRecorder:
    """A class to represent a crypto data feed recorder."""

    def __init__(self, market: Optional[Market] = None) -> None:
        """
        Defines the class attributes.

        :param market: The object to fill with the crypto feed record.
        """

        self.market: Market = market or {}
    # end __init__

    def parameters(self) -> RecorderParameters:
        """
        Returns the order book parameters.

        :return: The order book parameters.
        """

        return dict(
            channels=[L2_BOOK],
            callbacks={L2_BOOK: self.record}
        )
    # end parameters

    async def record(self, data: OrderBook, timestamp: float) -> None:
        """
        Records the data from the crypto feed into the dataset.

        :param data: The data from the exchange.
        :param timestamp: The time of the request.
        """

        dataset = (
            self.market.
            setdefault(data.exchange, {}).
            setdefault(
                data.symbol.replace('-', Separator.value),
                pd.DataFrame({BIDS: [], ASKS: []}, index=[])
            )
        )

        try:
            dataset.loc[dt.datetime.fromtimestamp(timestamp)] = {
                BIDS: data.book.bids.index(0)[0],
                ASKS: data.book.asks.index(0)[0]
            }

        except IndexError:
            pass
        # end try
    # end record

    def screener(
            self,
            ticker: str,
            source: str,
            location: Optional[str] = None,
            cancel: Optional[Union[Number, dt.timedelta]] = None,
            delay: Optional[Union[Number, dt.timedelta]] = None
    ) -> BaseScreener:
        """
        Defines the class attributes.

        :param ticker: The ticker of the asset.
        :param source: The exchange to get source data from.
        :param location: The saving location for the data.
        :param cancel: The time to cancel the waiting.
        :param delay: The delay for the process.
        """

        if source not in self.market:
            raise ValueError(
                f"source {source} is not a valid exchange in {self}."
            )
        # end if

        if ticker not in self.market[source]:
            raise ValueError(
                f"ticker {ticker} of exchange {source} "
                f"is not a valid ticker in {self}."
            )
        # end if

        screener = BaseScreener(
            ticker=ticker, source=source, delay=delay,
            location=location, cancel=cancel
        )

        screener.market = self.market[source][ticker]

        return screener
    # end screener

    def screeners(
            self,
            location: Optional[str] = None,
            cancel: Optional[Union[Number, dt.timedelta]] = None,
            delay: Optional[Union[Number, dt.timedelta]] = None
    ) -> List[BaseScreener]:
        """
        Defines the class attributes.

        :param location: The saving location for the data.
        :param cancel: The time to cancel the waiting.
        :param delay: The delay for the process.
        """

        base_screeners = []

        for source in self.market:
            for ticker in self.market[source]:
                base_screeners.append(
                    self.screener(
                        ticker=ticker, source=source, delay=delay,
                        location=location, cancel=cancel
                    )
                )
            # end for
        # end for

        return base_screeners
    # end screeners
# end MarketRecorder

def add_feeds(
        handler: FeedHandler,
        data: Dict[str, Iterable[str]],
        fixed: Optional[bool] = False,
        separator: Optional[str] = Separator.value,
        parameters: Optional[Dict[str, Dict[str, Any]]] = None
) -> None:
    """
    Adds the tickers to the handler for each exchange.

    :param handler: The handler object.
    :param data: The data of the exchanges and tickers to add.
    :param parameters: The parameters for the exchanges.
    :param fixed: The value for fixed parameters to all exchanges.
    :param separator: The separator of the assets.
    """

    base_parameters = None

    if not fixed:
        parameters = parameters or {}

    else:
        base_parameters = parameters or {}
        parameters = {}
    # end if

    for exchange, tickers in data.items():
        exchange = exchange.upper()

        tickers = [
            ticker.replace(separator, '-')
            for ticker in tickers
        ]

        if fixed:
            parameters.setdefault(exchange, base_parameters)
        # end if

        handler.add_feed(
            EXCHANGE_MAP[exchange](
                symbols=tickers,
                **(
                    parameters[exchange]
                    if (
                        (exchange in parameters) and
                        isinstance(parameters[exchange], dict) and
                        all(isinstance(key, str) for key in parameters)

                    ) else {}
                )
            )
        )
    # end for
# end add_feeds

class MarketHandler(FeedHandler):
    """A class to handle the market data feed."""

    def __init__(self) -> None:
        """Defines the class attributes."""

        super().__init__(
            config={'uvloop': True, 'log': {'disabled': True}}
        )
    # end __init__
# end MarketHandler

class MarketScreener(BaseMultiScreener):
    """
    A class to represent an asset price screener.

    Using this class, you can create a screener object to
    screen the market ask and bid data for a specific asset in
    a specific exchange at real time.

    Parameters:

    - location:
        The saving location for the saved data of the screener.

    - cancel:
        The time to cancel screening process after no new data is fetched.

    - delay:
        The delay to wait between each data fetching.

    - handler:
        The handler object to handle the data feed.

    - recorder:
        The recorder object to record the data of the market from the feed.

    >>> from auto_screener.feed import MarketScreener
    >>>
    >>> screener = MarketScreener()
    >>> screener.add_feeds({'binance': 'BTC/USDT', 'bittrex': 'ETH/USDT'})
    >>> screener.saving_loop()
    >>> screener.run_loop()
    """

    DELAY = 10

    def __init__(
            self,
            location: Optional[str] = None,
            cancel: Optional[Union[Number, dt.timedelta]] = None,
            delay: Optional[Union[Number, dt.timedelta]] = None,
            handler: Optional[FeedHandler] = None,
            recorder: Optional[MarketRecorder] = None
    ) -> None:
        """
        Creates the class attributes.

        :param location: The saving location for the data.
        :param delay: The delay for the process.
        :param cancel: The cancel time for the loops.
        :param handler: The handler object for the market data.
        :param recorder: The recorder object for recording the data.
        """

        super().__init__(
            location=location, cancel=cancel, delay=delay
        )

        self.handler = handler or MarketHandler()
        self.recorder = recorder or MarketRecorder()
    # end __init__

    def screener(
            self,
            ticker: str,
            source: str,
            location: Optional[str] = None,
            cancel: Optional[Union[Number, dt.timedelta]] = None,
            delay: Optional[Union[Number, dt.timedelta]] = None
    ) -> BaseScreener:
        """
        Defines the class attributes.

        :param ticker: The ticker of the asset.
        :param source: The exchange to get source data from.
        :param location: The saving location for the data.
        :param cancel: The time to cancel the waiting.
        :param delay: The delay for the process.
        """

        return self.recorder.screener(
            ticker=ticker, source=source, location=location or self.location,
            cancel=cancel or self.cancel, delay=delay or self.delay
        )
    # end screener

    def screeners(
            self,
            location: Optional[str] = None,
            cancel: Optional[Union[Number, dt.timedelta]] = None,
            delay: Optional[Union[Number, dt.timedelta]] = None
    ) -> List[BaseScreener]:
        """
        Defines the class attributes.

        :param location: The saving location for the data.
        :param cancel: The time to cancel the waiting.
        :param delay: The delay for the process.
        """

        return self.recorder.screeners(
            location=location or self.location,
            cancel=cancel or self.cancel, delay=delay or self.delay
        )
    # end screeners

    def add_feeds(
            self,
            data: Dict[str, Iterable[str]],
            fixed: Optional[bool] = True,
            separator: Optional[str] = Separator.value,
            parameters: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> None:
        """
        Adds the tickers to the handler for each exchange.

        :param data: The data of the exchanges and tickers to add.
        :param parameters: The parameters for the exchanges.
        :param fixed: The value for fixed parameters to all exchanges.
        :param separator: The separator of the assets.
        """

        add_feeds(
            self.handler, data=data, fixed=fixed, separator=separator,
            parameters=parameters or self.recorder.parameters()
        )
    # end add_feeds

    def run_loop(self) -> None:
        """Runs the process of the price screening."""

        self.handler.run()
    # end run_loop

    def saving_loop(self) -> None:
        """Runs the process of the price screening."""

        self.save()
    # end saving_loop

    def save(self, screeners: Optional[Iterable[BaseScreener]] = None) -> None:
        """
        Runs the data handling loop.

        :param screeners: The screeners.
        """

        for screener in screeners or self.screeners():
            threading.Thread(target=screener.saving_loop).start()
        # end for
    # end run

    def close(self) -> None:
        """Closes the data handling loop."""

        self.handler.close()
    # end close

    def stop(self) -> None:
        """Stops the data handling loop."""

        self.handler.stop()
    # end stop
# end MarketScreener

def market_recorder(
        data: Dict[str, Iterable[str]]
) -> MarketRecorder:
    """
    Creates the market recorder object for the data.

    :param data: The market data.

    :return: The market recorder object.
    """

    return MarketRecorder(market=create_market(data=data))
# end market_recorder

def market_screener(
        data: Dict[str, Iterable[str]],
        handler: Optional[FeedHandler] = None,
) -> MarketScreener:
    """
    Creates the market screener object for the data.

    :param data: The market data.
    :param handler: The handler object for the market data.

    :return: The market screener object.
    """

    screener = MarketScreener(
        recorder=MarketRecorder(market=create_market(data=data)),
        handler=handler
    )

    screener.add_feeds(data=data)

    return screener
# end market_recorder