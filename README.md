# bullion-az

azure functions demo

Hindsight:
Positional Trading is connecting to Kite to give us good trending scripts

Note To Users:
Stock Market Trading is strictly not advised

However investing in stock market is a wise decision. Always remember to chose consumer based stocks.

Program Description:
The thread runs for ten minutes after every 15 mins. This is a automated solution to automatically pick stocks Intraday stocks. The Buy or Sell calls are made based on their Latest Trade Volume, Current Market price, days's support and days resistance. The alogrithm is self enriched to make most best square-off bets during the loss. The script has the ability to adjust Stop Loss triggers and Target triggers based on the volume and current 2min and 5min trends after placing the order. Algorithm avoids bets on most of news driven stocks and only suitable to trade with non-volatile derivatives.

Build and Deploy Pipeline:
Using Github delivery protocols, automated merge into the cloud is triggered. Solution is deployed into Azure host for Functions. Cron jobs in Azure ensure to trigger the solution and every 15 mins.

Tools and Programming language
Python, REST packages, vscode with python interpreter is used to develop the solution
  Zerodha API services are used to perform stock picks and analyze technicals. Order are placed in zerodha platform
