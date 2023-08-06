# exchanges.py

from cryptofeed import exchanges
from cryptofeed.feed import Feed

__all__ = [
    "EXCHANGES"
]

EXCHANGES = {
    exchange.id: exchange
    for exchange in exchanges.__dict__
    if isinstance(exchange, Feed)
}