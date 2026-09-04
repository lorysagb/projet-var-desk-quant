#-*- coding: utf-8 -*-
"""
Cette script permet de : 
 -calculer les trois méthodes de var avec confiance 99% et 95%
 - faire un tableau récapitulatif

"""

import logging
import yfinance as yf
import numpy as np
from scipy.stats import norm

# PARAMETRES & CONSTANTES
LOG_LEVEL = logging.INFO

# CONFIGURATION DU LOGGING
logger = logging.getLogger('var_models')
logger.setLevel(LOG_LEVEL)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# Console Handler
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def calculate_var_parametrique(portfolio_returns, confiance):
#on suppose que les rendements du portfolio suivent une loi normale
# parametres : moyennne mu, quantile z, et volatilité sigma (ecart-type)

    mu = np.mean(portfolio_returns)
    z = norm.ppf(1 - confiance)
    sigma = np.std(portfolio_returns, ddof = 1)
    var_parametrique = -(mu + z*sigma)
    return var_parametrique

def calculate_var_historique(portfolio_returns, confiance):
#on suppose que le passé se repete
    return np.quantile(portfolio_returns, confiance)

def calculate_var_monte_carlo(portfolio_returns, confiance):
    
    #var Monte Carlo
    # Paramètres de simulation
    n_scenarios = 10_000
    confiances = [0.95, 0.99]

    # Moyenne et covariance des rendements des actifs
    mu_actifs = portfolio_returns.mean().values  #pas le rendement du portefeuille mais celui des actifs
    cov_actifs = portfolio_returns.cov().values

    # Simulation des rendements des actifs
    simulations_actifs = np.random.multivariate_normal(
        mean=mu_actifs,
        cov=cov_actifs,
        size=n_scenarios
    )

    # Rendement simulé du portefeuille
    simulations_portfolio = simulations_actifs.dot(np.array([1/5, 1/5, 1/5, 1/5, 1/5])) #poids

    for confiance in confiances:
        quantile = np.quantile(simulations_portfolio, 1 - confiance)
        var_monte_carlo = -quantile
        
    return var_monte_carlo