# test.py

from auto_screener.progress import Spinner
from auto_screener.screening import MultiScreener
from auto_screener.collect import collect_mutual_tickers

MATCHES = [["USD", "USDT"]]
QUOTES = ["USD", "USDT"]
EXCHANGES = ["kraken", "kucoin"]

LENGTH = 0
DELAY = 0

PRO = True

INTERVAL = None

LOCATION = "datasets"

def main() -> None:
    """Runs the program to test the module."""

    exchanges = collect_mutual_tickers(
        exchanges=EXCHANGES, quotes=QUOTES
    )

    screener = MultiScreener(
        data=exchanges, length=LENGTH,
        delay=DELAY, location=LOCATION,
        pro=PRO, interval=INTERVAL
    )

    with Spinner(message='Initializing Screeners'):
        screener.prepare_screeners()
    # end Spinner

    screener.run(block=True, wait=True)
# end main

if __name__ == "__main__":
    main()
# end if