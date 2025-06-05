# eurusd-strategy-bot/bot.py

import requests
import pandas as pd
import smtplib
from email.mime.text import MIMEText

API_KEY = "XZMRAARZ7QX8XVU1"
EMAIL_TO = "v.samimi@yahoo.com"
EMAIL_FROM = "your@gmail.com"
EMAIL_PASSWORD = "your_app_password"  # رمز اپلیکیشن Gmail

def get_data():
    url = f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=EUR&to_symbol=USD&interval=60min&apikey={API_KEY}&outputsize=compact"
    r = requests.get(url)
    data = r.json()["Time Series FX (60min)"]
    df = pd.DataFrame(data).T.astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.resample("4H").agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    return df.tail(100)

def check_strategy(df):
    df["ema50"] = df["close"].ewm(span=50).mean()
    df["ema100"] = df["close"].ewm(span=100).mean()
    is_bullish = df["ema50"].iloc[-1] > df["ema100"].iloc[-1]
    is_bearish = df["ema50"].iloc[-1] < df["ema100"].iloc[-1]

    candles = [1 if df["close"].iloc[-i] > df["open"].iloc[-i] else -1 for i in [4, 3, 2, 1]]
    length3 = abs(df["close"].iloc[-2] - df["open"].iloc[-2])
    length4 = abs(df["close"].iloc[-1] - df["open"].iloc[-1])
    same_color = candles[0] == candles[1] == candles[2]

    buy = is_bullish and same_color and candles[0] == -1 and candles[3] == 1 and length4 > 1.3 * length3
    sell = is_bearish and same_color and candles[0] == 1 and candles[3] == -1 and length4 > 1.3 * length3

    return buy, sell

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)

def main():
    df = get_data()
    buy, sell = check_strategy(df)
    if buy:
        send_email("EUR/USD Buy Signal", "Buy signal detected on EUR/USD!")
    elif sell:
        send_email("EUR/USD Sell Signal", "Sell signal detected on EUR/USD!")

if __name__ == "__main__":
    main()
