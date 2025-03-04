from flask import Flask, render_template, request

app = Flask(__name__)

def price_atr_percent(coin: str):
    coin = coin.upper()
    return f"{coin}...% ATR"


@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    if request.method == 'POST':
        coin = request.form.get('coin', '')
        result = price_atr_percent(coin)
    return render_template('index.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)
