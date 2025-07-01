# EURUSD Strategy Bot

This bot downloads 4h candles from the Twelve Data API and checks a simple EMA-based strategy.
It now processes both **EUR/USD** and **XAU/USD (Gold)**. When a buy or sell signal is detected,
a notification email is sent to the configured recipients.

Set the `EMAIL_FROM` and `EMAIL_PASSWORD` environment variables for sending email.
