import yfinance as yf


def retrieve_ticker_names():
    with open("ticker_list", "r") as f:
        return f.read()


if __name__ == '__main__':
    ticker_list = retrieve_ticker_names()
    tickers = yf.Tickers(ticker_list)
    result = {}
    for ticker in tickers.tickers:
        info = ticker.info
        result[info['longName']] = info['previousClose']

    print(result)
