# screener.py

import datetime as dt
import time
from abc import ABCMeta
import threading
from typing import (
    Optional, Union, Dict, Iterable,
    Any, Protocol, List
)

import pandas as pd

from represent import BaseModel, Modifiers

from auto_screener.dataset import (
    BIDS, ASKS, DATE_TIME, save_dataset, load_dataset
)
from auto_screener.hints import Number
from auto_screener.base import terminate_thread
from auto_screener.collect import validate_ticker

__all__ = [
    "BaseScreener",
    "wait_for_update",
    "wait_for_initialization",
    "WaitingState",
    "SingleAutoDataCollector",
    "AutoDataCollector",
    "collect_screeners",
    "wait_for_dynamic_update",
    "wait_for_dynamic_initialization",
    "BaseMultiScreener",
    "live_screeners"
]

class WaitingState(BaseModel):
    """A class to represent the waiting state of screener objects."""

    modifiers = Modifiers(excluded=["create_screeners"])

    def __init__(
            self, screeners: Iterable,
            delay: Number,
            count: int,
            canceled: bool,
            cancel: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
    ) -> None:
        """
        Defines the class attributes.

        :param screeners: The screener objects.
        :param delay: The waiting delay.
        :param count: The iterations count.
        :param canceled: The value for the waiting being canceled.
        :param cancel: The time to cancel the waiting.
        """

        self.screeners: Iterable[SingleAutoDataCollector] = screeners

        self.delay = delay
        self.cancel = cancel
        self.count = count

        self.canceled = canceled

        self.time = dt.timedelta(seconds=self.delay * self.count)
    # end __init__
# end WaitingState

class AutoDataCollector(Protocol, metaclass=ABCMeta):
    """A class to represent an abstract parent class of data collectors."""

    LOCATION = "datasets"

    block: bool
    running: bool
    saving: bool

    delay: Optional[Union[Number, dt.timedelta]]
    cancel: Union[Number, dt.timedelta, dt.datetime]

    screening_process: Optional[threading.Thread]
    timeout_process: Optional[threading.Thread]
    saving_process: Optional[threading.Thread]

    def blocking(self) -> bool:
        """
        returns the value of the process being blocked.

        :return: The value.
        """

        return self.block
    # end blocking

    def run_loop(self) -> None:
        """Runs the process of the price screening."""
    # end run_loop

    def saving_loop(self) -> None:
        """Runs the process of the price screening."""
    # end saving_loop

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
    # end wait_for_update

    def run(
            self,
            save: Optional[bool] = True,
            block: Optional[bool] = False,
            wait: Optional[Union[bool, Number, dt.timedelta, dt.datetime]] = False,
            timeout: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
    ) -> threading.Thread:
        """
        Runs the process of the price screening.

        :param save: The value to save the data.
        :param wait: The value to wait after starting to run the process.
        :param block: The value to block the execution.
        :param timeout: The valur to add a timeout to the process.
        """

        self.running = True

        self.screening_process = threading.Thread(target=self.run_loop)

        self.screening_process.start()

        if save:
            self.saving = True

            self.saving_process = threading.Thread(
                target=self.saving_loop
            )

            self.saving_process.start()
        # end if

        if timeout:
            self.timeout(timeout)
        # end if

        if block:
            self.block = block

            while self.blocking():
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

        return self.screening_process
    # end run

    def timeout(
            self, duration: Union[Number, dt.timedelta, dt.datetime]
    ) -> threading.Thread:
        """
        Runs a timeout for the process.

        :param duration: The duration of the timeout.

        :return: The timeout process.
        """

        if isinstance(duration, dt.datetime):
            duration = duration - dt.datetime.now()
        # end if

        if isinstance(duration, dt.timedelta):
            duration = duration.total_seconds()
        # end if

        self.timeout_process = threading.Thread(
            target=lambda: (time.sleep(duration), self.terminate())
        )

        self.timeout_process.start()

        return self.timeout_process
    # end timeout

    def terminate(self) -> None:
        """Stops the trading process."""

        self.stop()
    # end terminate

    def stop(self) -> None:
        """Stops the screening process."""

        self.running = False
        self.saving = False

        if isinstance(self.screening_process, threading.Thread):
            terminate_thread(self.screening_process)
        # end if

        if isinstance(self.timeout_process, threading.Thread):
            terminate_thread(self.timeout_process)
        # end if

        if isinstance(self.saving_process, threading.Thread):
            terminate_thread(self.saving_process)
        # end if
    # end stop
# end AutoDataCollector

class SingleAutoDataCollector(AutoDataCollector, metaclass=ABCMeta):
    """A class to represent an abstract parent class of data collectors."""

    market: pd.DataFrame

    ticker: str
    source: str
    location: str

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

        return wait_for_initialization(
            self, delay=delay, once=once,
            stop=stop, cancel=cancel or self.cancel
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

        return wait_for_update(
            self, delay=delay, once=once,
            stop=stop, cancel=cancel or self.cancel
        )
    # end wait_for_update

    def dataset_path(
            self, location: Optional[str] = None
    ) -> str:
        """
        Creates the path to the saving file for the screener object.

        :param location: The saving location of the dataset.

        :return: The saving path for the dataset.
        """

        return (location + "/" if isinstance(location, str) else "") + (
            f"{self.source.lower()}/{self.ticker.replace('/', '-')}.csv"
        )
    # end dataset_path

    def save_dataset(self, location: Optional[str] = None) -> None:
        """Saves the data of the screener."""

        if len(self.market) == 0:
            return
        # end if

        location = location or self.location

        save_dataset(
            dataset=self.market,
            path=self.dataset_path(location=location)
        )
    # end save_dataset

    def load_dataset(self, location: Optional[str] = None) -> None:
        """Saves the data of the screener."""

        location = location or self.location

        data = load_dataset(
            path=self.dataset_path(location=location)
        )

        for index, data in zip(data.index[:], data.loc[:]):
            self.market.loc[index] = data
        # end for
    # end load_dataset

    def validate_ticker(self, ticker: Any) -> str:
        """
        Validates the ticker value.

        :param ticker: The name of the ticker.

        :return: The validates ticker.
        """

        if not hasattr(self, "source"):
            raise AttributeError(
                f"Source attribute must be defined before "
                f"attempting to validate the ticker attribute."
            )
        # end if

        return validate_ticker(self.source, ticker)
    # end validate_ticker

    def saving_loop(self) -> None:
        """Runs the process of the price screening."""

        self.saving = True

        delay = self.delay

        if isinstance(self.delay, dt.timedelta):
            delay = delay.total_seconds()
        # end if

        while self.saving:
            start = time.time()

            self.save_dataset()

            end = time.time()

            time.sleep(max(delay - (end - start), 0) or 1)
        # end while
    # end run_loop
# end SingleAutoDataCollector

class BaseScreener(BaseModel, SingleAutoDataCollector):
    """
    A class to represent an asset price screener.

    Using this class, you can create a screener object to
    screen the market ask and bid data for a specific asset in
    a specific exchange at real time.

    Parameters:

    - ticker:
        The ticker symbol of an asset to screen.

    - source:
        The name of the exchange platform to screen data from.

    - location:
        The saving location for the saved data of the screener.

    - cancel:
        The time to cancel screening process after no new data is fetched.

    - delay:
        The delay to wait between each data fetching.
    """

    modifiers = Modifiers(
        excluded=[
            "market", 'screening_process',
            'timeout_process', 'saving_process'
        ]
    )

    ASKS = ASKS
    BIDS = BIDS

    DELAY = 0.0
    CANCEL = 0

    COLUMNS = (BIDS, ASKS)

    def __init__(
            self,
            ticker: str,
            source: str,
            location: Optional[str] = None,
            cancel: Optional[Union[Number, dt.timedelta]] = None,
            delay: Optional[Union[Number, dt.timedelta]] = None
    ) -> None:
        """
        Defines the class attributes.

        :param ticker: The ticker of the asset.
        :param source: The exchange to get source data from.
        :param location: The saving location for the data.
        :param delay: The delay for the process.
        :param cancel: The cancel time for the loops.
        """

        self.cancel = cancel or self.CANCEL
        self.delay = delay or self.DELAY

        self.source = source
        self.location = location or self.LOCATION

        self.ticker = self.validate_ticker(ticker=ticker)

        self.running = False
        self.block = False
        self.saving = False

        self.screening_process = None
        self.timeout_process = None
        self.saving_process = None

        self.market = pd.DataFrame(
            {column: [] for column in self.COLUMNS}, index=[]
        )

        self.market.index.name = DATE_TIME
    # end __init__

    def __getstate__(self) -> Dict[str, Any]:
        """
        Returns the data of the object.

        :return: The state of the object.
        """

        data = self.__dict__.copy()

        data["screening_process"] = None
        data["timeout_process"] = None

        return data
    # end __getstate__

    def stop(self) -> None:
        """Stops the screening process."""

        super().stop()

        if isinstance(self.screening_process, threading.Thread):
            terminate_thread(self.screening_process)
        # end if

        if isinstance(self.timeout_process, threading.Thread):
            terminate_thread(self.timeout_process)
        # end if
    # end stop

    def terminate(self) -> None:
        """Stops the trading process."""

        super().terminate()
    # end terminate
# end BaseScreener

class BaseMultiScreener(BaseModel, AutoDataCollector):
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
    """

    modifiers = Modifiers(
        excluded=[
            "market", 'screening_process',
            'timeout_process', 'saving_process'
        ]
    )

    DELAY = 0.0
    CANCEL = 0

    screeners: Iterable[SingleAutoDataCollector]

    def __init__(
            self,
            location: Optional[str] = None,
            cancel: Optional[Union[Number, dt.timedelta]] = None,
            delay: Optional[Union[Number, dt.timedelta]] = None
    ) -> None:
        """
        Defines the class attributes.

        :param location: The saving location for the data.
        :param delay: The delay for the process.
        :param cancel: The cancel time for the loops.
        """

        self.cancel = cancel or self.CANCEL
        self.delay = delay or self.DELAY

        self.location = location or self.LOCATION

        self.running = False
        self.block = False
        self.saving = False

        self.screening_process = None
        self.timeout_process = None
    # end __init__

    def __getstate__(self) -> Dict[str, Any]:
        """
        Returns the data of the object.

        :return: The state of the object.
        """

        data = self.__dict__.copy()

        data["screening_process"] = None
        data["timeout_process"] = None

        return data
    # end __getstate__

    def terminate(self) -> None:
        """Stops the trading process."""

        super().terminate()
    # end terminate
# end BaseScreener

def collect_screeners(
        ticker: str, source: str, screeners: Iterable[SingleAutoDataCollector]
) -> List[SingleAutoDataCollector]:
    """
    Finds the create_screeners with the given source exchange and ticker.

    :param ticker: The ticker of the screener.
    :param source: The exchange name of the screener.
    :param screeners: The create_screeners to search in.

    :return: A list of the matching create_screeners.
    """

    found = []

    for screener in screeners:
        if (screener.source == source) and (screener.ticker == ticker):
            found.append(screener)
        # end if
    # end for

    return found
# end collect_screeners

def wait_for_dynamic_initialization(
        screeners: Iterable[SingleAutoDataCollector],
        delay: Optional[Union[Number, dt.timedelta]] = None,
        once: Optional[bool] = False,
        stop: Optional[Union[bool, int]] = False,
        cancel: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
) -> WaitingState:
    """
    Waits for all the create_screeners to update.

    :param screeners: The create_screeners to wait for them to update.
    :param delay: The delay for the waiting.
    :param once: The value to get data only once.
    :param stop: The value to stop the screener objects.
    :param cancel: The time to cancel the waiting.

    :returns: The total delay.
    """

    if cancel == 0:
        cancel = None
    # end if

    if isinstance(cancel, (int, float)):
        cancel = dt.timedelta(seconds=cancel)
    # end if

    current_time = dt.datetime.now()

    if isinstance(cancel, dt.timedelta):
        cancel = current_time + cancel
    # end if

    if isinstance(delay, dt.timedelta):
        delay = delay.total_seconds()
    # end if

    delay = delay or 0
    count = 0

    while True:
        if (
            (not any(len(screener.market) == 0 for screener in screeners)) or
            ((cancel is not None) and ((current_time := dt.datetime.now()) > cancel))
        ):
            break
        # end if

        count += 1

        if isinstance(delay, (int, float)) and (count > 0):
            time.sleep(delay)
        # end if
    # end while

    if stop and ((stop == count) or once):
        for screener in screeners:
            screener.stop()
        # end for
    # end if

    return WaitingState(
        screeners=screeners, delay=delay, count=count,
        cancel=cancel, canceled=(cancel is None) or (current_time > cancel)
    )
# end wait_for_dynamic_initialization

def wait_for_initialization(
        *screeners: SingleAutoDataCollector,
        delay: Optional[Union[Number, dt.timedelta]] = None,
        once: Optional[bool] = False,
        stop: Optional[Union[bool, int]] = False,
        cancel: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
) -> WaitingState:
    """
    Waits for all the create_screeners to update.

    :param screeners: The create_screeners to wait for them to update.
    :param delay: The delay for the waiting.
    :param once: The value to get data only once.
    :param stop: The value to stop the screener objects.
    :param cancel: The time to cancel the waiting.

    :returns: The total delay.
    """

    return wait_for_dynamic_initialization(
        screeners, delay=delay, once=once,
        stop=stop, cancel=cancel
    )
# end wait_for_initialization

def wait_for_dynamic_update(
        screeners: Iterable[SingleAutoDataCollector],
        delay: Optional[Union[Number, dt.timedelta]] = None,
        once: Optional[bool] = False,
        stop: Optional[Union[bool, int]] = False,
        cancel: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
) -> WaitingState:
    """
    Waits for all the create_screeners to update.

    :param screeners: The create_screeners to wait for them to update.
    :param delay: The delay for the waiting.
    :param once: The value to get data only once.
    :param stop: The value to stop the screener objects.
    :param cancel: The time to cancel the waiting.

    :returns: The total delay.
    """

    if cancel == 0:
        cancel = None
    # end if

    if isinstance(cancel, (int, float)):
        cancel = dt.timedelta(seconds=cancel)
    # end if

    current_time = dt.datetime.now()

    if isinstance(cancel, dt.timedelta):
        cancel = current_time + cancel
    # end if

    if isinstance(delay, dt.timedelta):
        delay = delay.total_seconds()
    # end if

    delay = delay or 0
    count = 0

    if screeners:
        wait_for_dynamic_initialization(
            screeners, delay=delay, once=once
        )

        indexes = [
            screener.market.index[-1]
            for screener in screeners
        ]

        new_indexes = indexes

        length = len(tuple(screeners))

        while True:
            if (
                all(
                    indexes[i] != new_indexes[i]
                    for i in range(length)
                ) or
                (
                    (cancel is not None) and
                    ((current_time := dt.datetime.now()) > cancel)
                )
            ):
                break
            # end if

            count += 1

            new_indexes = [
                screener.market.index[-1]
                for screener in screeners
            ]

            if isinstance(delay, (int, float)) and (count > 0):
                time.sleep(delay)
            # end if
        # end while

        if stop and ((stop == count) or once):
            for screener in screeners:
                screener.stop()
            # end for
        # end if
    # end if

    return WaitingState(
        screeners=screeners, delay=delay, count=count, cancel=cancel,
        canceled=(cancel is None) or (current_time > cancel)
    )
# end wait_for_dynamic_update

def wait_for_update(
        *screeners: SingleAutoDataCollector,
        delay: Optional[Union[Number, dt.timedelta]] = None,
        once: Optional[bool] = False,
        stop: Optional[Union[bool, int]] = False,
        cancel: Optional[Union[Number, dt.timedelta, dt.datetime]] = None
) -> WaitingState:
    """
    Waits for all the create_screeners to update.

    :param screeners: The create_screeners to wait for them to update.
    :param delay: The delay for the waiting.
    :param once: The value to get data only once.
    :param stop: The value to stop the screener objects.
    :param cancel: The time to cancel the waiting.

    :returns: The total delay.
    """

    return wait_for_dynamic_update(
        screeners, delay=delay, once=once,
        stop=stop, cancel=cancel
    )
# end wait_for_update

def live_screeners(
        screeners: Iterable[Union[BaseScreener, BaseMultiScreener]]
) -> List[Union[BaseScreener, BaseMultiScreener]]:
    """
    Returns a list of all the live create_screeners.

    :param screeners: The create_screeners to search from.

    :return: A list the live create_screeners.
    """

    return [
        screener for screener in screeners
        if (
            screener.running and (
                isinstance(screener, BaseMultiScreener) or
                len(screener.market) > 0
            )
        )
    ]
# end live_screeners