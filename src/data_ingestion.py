#-*- coding: utf-8 -*-

import logging
import yfinance as yf

# PARAMETRES & CONSTANTES
LOG_LEVEL = logging.INFO

# CONFIGURATION DU LOGGING
logger = logging.getLogger('data_ingestion')
logger.setLevel(LOG_LEVEL)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


tickers = ["SPY", "TLT", "GLD", "USO", "QQQ"]
data = yf.download(tickers, period="5y", auto_adjust=True)["Close"] #prix au close
print(data.head())
