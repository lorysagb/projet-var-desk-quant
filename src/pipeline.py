import logging
import yfinance as yf
import numpy as np

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


from data_ingestion import ingestion_nettoyage, calculer_portfolio_returns
from var_models import calculate_var_historique, calculate_var_monte_carlo, calculate_var_parametrique

def process(tickers):
    data_cleaned = ingestion_nettoyage(tickers)
    
    portfolio_returns = calculer_portfolio_returns(data_cleaned)
    
    logger.info("calcul de var")
    