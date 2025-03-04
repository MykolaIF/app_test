import pandas as pd
from binance.client import Client
from flask import Flask, render_template, request

app = Flask(__name__)
client = Client("", "")
LENGTH = 14
TIME_FRAME = Client.KLINE_INTERVAL_1HOUR
TIME_START = f"{LENGTH * 60} minutes ago UTC"


def rma(s: pd.Series, period: int) -> pd.Series:
    return s.ewm(alpha=1 / period).mean()


def atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    high, low, prev_close = df['high'], df['low'], df['close'].shift()
    tr_all = [high - low, high - prev_close, low - prev_close]
    tr_all = [tr.abs() for tr in tr_all]
    tr = pd.concat(tr_all, axis=1).max(axis=1)
    atr_ = rma(tr, length)
    return atr_


def price_atr_percent(coin: str):
    coin = coin.upper()
    try:
        klines = client.get_historical_klines(
            f"{coin}USDT",
            TIME_FRAME,
            TIME_START
        )
    except:
        return f"Монети {coin} немає"

    data = pd.DataFrame(klines, columns=["timestamp", "open", "high", "low", "close", "volume",
                                         "close_time", "quote_asset_volume", "number_of_trades",
                                         "taker_buy_base", "taker_buy_quote", "ignore"])
    data = data[["high", "low", "close"]].astype(float)
    if len(data) > 0:
        atr_values = atr(data, length=LENGTH)

        current_price = data["close"].iloc[-1]
        current_atr = atr_values.iloc[-1]
        return f"{coin} {round(current_atr / current_price * 100, 2)}% ATR"
    else:
        return f"Немає руху ціни {coin} для обрахунку ATR"


@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    if request.method == 'POST':
        coin = request.form.get('coin', '')
        result = price_atr_percent(coin)
    return render_template('index.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)
