import requests
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import os

API_KEY = "313c54ea08cf4aedabff6cb615c6c6b4"
EMAILS_TO = ["v.samimi@yahoo.com", "apminaei@gmail.com"]
EMAIL_FROM = os.environ.get("EMAIL_FROM")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

def get_data(symbol: str):
    print(f"📥 Fetching data for {symbol} from Twelve Data...")
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=4h&outputsize=100&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        print("❌ Error: Could not parse API response.")
        print(data)
        return None

    df = pd.DataFrame(data["values"])
    df = df.rename(columns={
        "datetime": "date",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close"
    })
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    df = df.astype(float)
    df = df.sort_index()  # Ascending order
    print("✅ Data fetched successfully.")
    return df

def check_strategy(df):
    print("🔍 Checking strategy conditions...")
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

    print(f"📊 Trend: {'Bullish' if is_bullish else 'Bearish' if is_bearish else 'Neutral'}")
    print(f"📈 Buy signal: {buy}")
    print(f"📉 Sell signal: {sell}")
    return buy, sell

def send_email(subject, body):
    print(f"📨 Sending email: {subject}")
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        for email in EMAILS_TO:
            msg["To"] = email
            server.send_message(msg)
    print("✅ Email sent successfully.")

def process_symbol(symbol: str):
    df = get_data(symbol)
    if df is None:
        print(f"⛔️ Stopping processing of {symbol} due to data fetch failure.")
        return
    buy, sell = check_strategy(df)
    if buy:
        send_email(f"{symbol} Buy Signal", f"Buy signal detected on {symbol}!")
    elif sell:
        send_email(f"{symbol} Sell Signal", f"Sell signal detected on {symbol}!")
    else:
        print(f"ℹ️ No signal detected for {symbol}.")


def main():
    for symbol in ["EUR/USD", "XAU/USD", "AMZN", "NFLX"]:
        process_symbol(symbol)

if __name__ == "__main__":
    main()
