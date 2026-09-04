#-*- coding: utf-8 -*-
"""
Cette script permet de : 
 - télécharger un dataset de cours historiques
 - prétraiter ce dataset (valeurs manquantes, etc)

"""

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

def ingestion_nettoyage(tickers) : 
    
    data = yf.download(tickers, period="5y", auto_adjust=True)["Close"] #prix au close
    
    if data:
        logger.info(f"le dataset a été téléchargé avec succès : {data}")
    else:
        logger.error("erreur lors du telechargement des données")
    
    data_cleaned  = data.dropna() #suppression des valeurs manquantes
    
    return data_cleaned

def calculer_portfolio_returns(data):
    
    returns = data.pct_change().dropna()
    
    # Portefeuille équipondéré 20%
    poids = np.array([1/5, 1/5, 1/5, 1/5, 1/5])
    
    portfolio_returns = returns.dot(poids)
    
    return portfolio_returns





