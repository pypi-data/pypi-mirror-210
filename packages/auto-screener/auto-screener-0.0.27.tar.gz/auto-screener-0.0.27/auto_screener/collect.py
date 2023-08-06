# collect.py

import threading
from typing import (
    Optional, Dict, Iterable, List, Callable, Union
)

from cryptofeed.feed import Feed
from cryptofeed.exchanges import EXCHANGE_MAP

from auto_screener.tickers import ticker_to_parts, Separator
from auto_screener.tickers import parts_to_ticker

__all__ = [
    "collect_assets",
    "collect_tickers",
    "collect_mutual_assets",
    "collect_mutual_tickers",
    "is_valid_ticker",
    "validate_ticker",
    "collect_exchanges",
    "is_valid_source",
    "find_exchange"
]

def _collect_exchange_assets(
        data: Dict[str, List[str]],
        source: str,
        exchange: Feed,
        quotes: Optional[Iterable[str]] = None,
        excluded: Optional[Iterable[str]] = None
) -> None:
    """
    Collects the tickers from the exchanges.

    :param source: The name of the exchange.
    :param exchange: The exchange object.
    :param data: The data to collect the assets.
    :param quotes: The quotes of the asset pairs.
    :param excluded: The excluded tickers.

    :return: The data of the exchanges.
    """

    quotes = quotes or []
    excluded = excluded or []
    assets = []

    # noinspection PyBroadException
    try:
        for ticker in exchange.symbols():
            ticker: str

            base, quote = ticker_to_parts(ticker, separator='-')

            if (
                quotes and
                (quote not in quotes) or
                (quote in excluded) or
                (base in excluded)
            ):
                continue
            # end if

            assets.append(base)
        # end for

        data[source] = list(set(assets))

    except Exception:
        data[source] = []
    # end try
# end _collect_exchange_assets

def _collect_exchange_tickers(
        data: Dict[str, List[str]],
        source: str,
        exchange: Feed,
        quotes: Optional[Iterable[str]] = None,
        separator: Optional[str] = Separator.value,
        excluded: Optional[Iterable[str]] = None
) -> None:
    """
    Collects the tickers from the exchanges.

    :param source: The name of the exchange.
    :param exchange: The exchange object.
    :param data: The data to collect the assets.
    :param quotes: The quotes of the asset pairs.
    :param separator: The separator of the assets.
    :param excluded: The excluded tickers.

    :return: The data of the exchanges.
    """

    quotes = quotes or []
    excluded = excluded or []
    tickers = []

    # noinspection PyBroadException
    try:
        for ticker in exchange.symbols():
            ticker: str

            base, quote = ticker_to_parts(ticker, separator='-')

            if (
                quotes and
                (quote not in quotes) or
                (tickers in excluded) or
                (ticker.replace('-', separator) in excluded)
            ):
                continue
            # end if

            tickers.append(ticker.replace('-', separator))
        # end for

        data[source] = list(set(tickers))

    except Exception:
        data[source] = []
    # end try
# end _collect_exchange_tickers

Collector = Callable[
    [Dict[str, List[str]], str, Feed, Optional[Iterable[str]]], None
]

def find_exchange(name: str, exchanges: Iterable[str]) -> str:
    """
    Finds the exchange in the exchanges.

    :param name: The name of the exchange.
    :param exchanges: The exchanges to search in.

    :return: The valid exchange name.
    """

    for exchange in exchanges:
        if exchange.lower() == name.lower():
            return exchange
        # end if
    # end for

    return name
# end find_exchange

def _collect_data(
        collector: Collector,
        exchanges: Optional[Iterable[str]] = None,
        quotes: Optional[Iterable[str]] = None,
        excluded: Optional[Union[Dict[str, Iterable[str]], Iterable[str]]] = None
) -> Dict[str, List[str]]:
    """
    Collects the tickers from the exchanges.

    :param exchanges: The exchanges.
    :param quotes: The quotes of the asset pairs.
    :param excluded: The excluded tickers.

    :return: The data of the exchanges.
    """

    excluded_tickers = []

    excluded = excluded or {}

    if not excluded:
        excluded_tickers = excluded
    # end if

    if (
        excluded and
        all(isinstance(value, str) for value in excluded) and
        not isinstance(excluded, dict)
    ):
        excluded = {exchange: excluded_tickers for exchange in exchanges}
    # end if

    quotes = quotes or []

    data = {}
    markets = {}

    for source in (exchanges or EXCHANGE_MAP.keys()):
        if source.upper() not in EXCHANGE_MAP.keys():
            continue
        # end if

        exchange = EXCHANGE_MAP[source.upper()]

        markets[source] = exchange
    # end for

    for source, exchange in markets.items():
        excluded_source = find_exchange(name=source, exchanges=excluded)

        threading.Thread(
            target=collector,
            kwargs=dict(
                source=source, exchange=exchange,
                data=data, quotes=quotes, excluded=(
                    excluded[excluded_source]
                    if excluded_source in excluded else None
                )
            )
        ).start()
    # end for

    while len(markets) > len(data):
        pass
    # end while

    return {key: value for key, value in data.items() if value}
# end collect_tickers

def collect_assets(
        exchanges: Optional[Iterable[str]] = None,
        quotes: Optional[Iterable[str]] = None,
        excluded: Optional[Union[Dict[str, Iterable[str]], Iterable[str]]] = None
) -> Dict[str, List[str]]:
    """
    Collects the tickers from the exchanges.

    :param exchanges: The exchanges.
    :param quotes: The quotes of the asset pairs.
    :param excluded: The excluded tickers.

    :return: The data of the exchanges.
    """

    return _collect_data(
        collector=_collect_exchange_assets,
        exchanges=exchanges, quotes=quotes, excluded=excluded
    )
# end collect_tickers

def _collect_mutual_data(
        data: Dict[str, Iterable[str]],
) -> Dict[str, List[str]]:
    """
    Collects the tickers from the exchanges.

    :param data: The exchanges' data.

    :return: The data of the exchanges.
    """

    values = {}

    for source in data:
        for asset in data[source]:
            values[asset] = values.setdefault(asset, 0) + 1
        # end for
    # end for

    return {
        source: [
            asset for asset in data[source]
            if values.get(asset, 0) > 1
        ]
        for source in data
    }
# end collect_mutual_assets

def collect_mutual_assets(
        exchanges: Optional[Iterable[str]] = None,
        quotes: Optional[Iterable[str]] = None,
        excluded: Optional[Union[Dict[str, Iterable[str]], Iterable[str]]] = None
) -> Dict[str, List[str]]:
    """
    Collects the tickers from the exchanges.

    :param exchanges: The exchanges.
    :param quotes: The quotes of the asset pairs.
    :param excluded: The excluded tickers.

    :return: The data of the exchanges.
    """

    return _collect_mutual_data(
        data=collect_assets(
            exchanges=exchanges, quotes=quotes, excluded=excluded
        )
    )
# end collect_mutual_assets

def collect_tickers(
        exchanges: Optional[Iterable[str]] = None,
        quotes: Optional[Iterable[str]] = None,
        excluded: Optional[Union[Dict[str, Iterable[str]], Iterable[str]]] = None
) -> Dict[str, List[str]]:
    """
    Collects the tickers from the exchanges.

    :param exchanges: The exchanges.
    :param quotes: The quotes of the asset pairs.
    :param excluded: The excluded tickers.

    :return: The data of the exchanges.
    """

    return _collect_data(
        collector=_collect_exchange_tickers,
        exchanges=exchanges, quotes=quotes, excluded=excluded
    )
# end collect_tickers

def collect_mutual_tickers(
        exchanges: Optional[Iterable[str]] = None,
        quotes: Optional[Iterable[str]] = None,
        excluded: Optional[Union[Dict[str, Iterable[str]], Iterable[str]]] = None
) -> Dict[str, List[str]]:
    """
    Collects the tickers from the exchanges.

    :param exchanges: The exchanges.
    :param quotes: The quotes of the asset pairs.
    :param excluded: The excluded tickers.

    :return: The data of the exchanges.
    """

    return _collect_mutual_data(
        data=collect_tickers(
            exchanges=exchanges, quotes=quotes, excluded=excluded
        )
    )
# end collect_mutual_tickers

def is_valid_ticker(source: str, ticker: str) -> bool:
    """
    Returns a value for the ticker being valid for the source exchange.

    :param source: The name of the exchange platform.
    :param ticker: The ticker of the assets.

    :return: The validation-value.
    """

    if not is_valid_source(source):
        return False
    # end if

    return (
        ticker.replace(Separator.value, '-') in
        EXCHANGE_MAP[source.upper()].symbols()
    )
# end is_valid_ticker

def validate_ticker(source: str, ticker: str) -> str:
    """
    Validates the ticker value.

    :param source: The name of the exchange platform.
    :param ticker: The name of the ticker.

    :return: The validates ticker.
    """

    validate_source(source)

    if not is_valid_ticker(source, ticker):
        raise ValueError(
            f"ticker {ticker} is not a valid "
            f"ticker for the {source} exchange."
        )
    # end if

    return ticker
# end validate_ticker

def is_valid_source(source: str) -> bool:
    """
    checks of the source os a valid exchange name.

    :param source: The source name to validate.

    :return: The validation value.
    """

    return source.upper() in EXCHANGE_MAP
# end is_valid_source

def validate_source(source: str) -> str:
    """
    Validates the source value.

    :param source: The name of the exchange platform.

    :return: The validates ticker.
    """

    if not is_valid_source(source):
        raise ValueError(
            f"source {source} is not a valid exchange."
        )
    # end if

    return source
# end validate_source

def collect_exchanges(
        currencies: Dict[str, List[str]],
        pairs: Dict[str, List[str]],
        excluded: Optional[Dict[str, Iterable[str]]] = None,
) -> Dict[str, List[str]]:
    """
    Collects the exchanges.

    :param pairs: The data of currencies and their traded quote assets.
    :param currencies: The data of exchanges and their traded currencies.
    :param excluded: The data of excluded pairs for each exchange.

    :return: The data of exchanges and their tickers.
    """

    exchanges: Dict[str, List[str]] = {}

    for platform, currencies in currencies.items():
        exchanges[platform] = []

        for currency in currencies:
            for asset in pairs[currency]:
                if (
                    parts_to_ticker(asset, currency) in
                    excluded.get(platform, [])
                ):
                    continue
                # end if

                exchanges[platform].append(
                    parts_to_ticker(asset, currency)
                )
            # end for
        # end for
    # end for

    return exchanges
# end collect_exchanges