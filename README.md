# Projet VaR Desk Quant

Système exploratoire de monitoring du risque d'un portefeuille multi-actifs. Le
projet combine trois approches de Value-at-Risk (VaR), leur backtesting, et un
modèle de classification destiné à détecter les régimes de volatilité.

## Objectifs

- mesurer la perte potentielle du portefeuille à un horizon d'un jour ;
- comparer les méthodes paramétrique, historique et Monte Carlo ;
- vérifier la qualité des VaR avec un backtesting et le test de Kupiec ;
- prédire si les cinq prochains jours appartiendront à un régime de volatilité
	élevée.

## Données et portefeuille

L'analyse porte sur cinq ETF :

| Ticker | Exposition |
|---|---|
| SPY | Actions américaines large cap |
| QQQ | Nasdaq et valeurs technologiques |
| TLT | Obligations américaines long terme |
| GLD | Or |
| USO | Pétrole |

Les prix ajustés sont téléchargés avec `yfinance` sur une période de cinq ans,
puis transformés en rendements journaliers par :

```python
returns = data.pct_change().dropna()
```

Le portefeuille est équipondéré : chaque actif reçoit un poids de 20 %. Le
fichier [`returns.csv`](returns.csv) contient une exportation des rendements
utilisés dans l'analyse.

## Pipeline

Le pipeline complet est documenté dans [`pipeline.ipynb`](pipeline.ipynb).

### 1. Ingestion et préparation

Les cours de clôture ajustés de SPY, TLT, GLD, USO et QQQ sont récupérés, puis
convertis en rendements journaliers. Le notebook sauvegarde également les
rendements au format Parquet (`returns.parquet`).

### 2. Analyse exploratoire

Le notebook calcule la matrice de corrélation et étudie la distribution du
rendement du portefeuille équipondéré. La densité empirique est comparée à une
loi normale de même moyenne et de même écart-type. La skewness et le kurtosis
sont ensuite calculés pour évaluer l'asymétrie et l'épaisseur des queues.

### 3. Calcul de la VaR

La VaR est calculée pour un horizon d'un jour et des niveaux de confiance de
95 % et 99 %.

- **Paramétrique** : hypothèse de normalité des rendements, avec la moyenne et
	l'écart-type historiques.
- **Historique** : quantile empirique des rendements passés, sans hypothèse de
	distribution.
- **Monte Carlo** : simulation de 10 000 vecteurs de rendements selon une loi
	normale multivariée calibrée sur la moyenne et la covariance historiques.

La convention utilisée est une VaR positive représentant une perte :

```text
VaR = - quantile(rendement du portefeuille)
```

### 4. Backtesting

Une exception est comptée lorsqu'un rendement observé est inférieur à
`-VaR`. Le notebook compare le nombre d'exceptions observées au nombre attendu
et applique le test de Kupiec (couverture inconditionnelle). L'hypothèse nulle
est que la fréquence observée des exceptions correspond à la fréquence
théorique `1 - niveau_de_confiance`.

### 5. Détection des régimes de volatilité

La cible `high_vol` vaut 1 lorsque la volatilité réalisée sur les cinq jours
suivants dépasse le 75e percentile historique. Les variables explicatives sont
calculées uniquement à partir de l'information disponible au jour courant :

- volatilité glissante sur 5 jours ;
- volatilité glissante sur 20 jours ;
- rendement moyen glissant sur 20 jours ;
- drawdown courant.

Deux modèles sont comparés avec un split chronologique 80/20 : une régression
logistique standardisée et une forêt aléatoire de 200 arbres. L'évaluation
utilise le recall par classe, l'AUC et les courbes ROC.

## Résultats clés du notebook

Les valeurs ci-dessous sont celles consignées dans le notebook au moment de
l'analyse. Les simulations Monte Carlo étant aléatoires, elles peuvent varier
si le notebook est réexécuté sans graine aléatoire fixée.

### Dépendance entre actifs et distribution

- SPY et QQQ présentent une corrélation d'environ **0,95**, cohérente avec
	leurs expositions communes aux grandes valeurs technologiques américaines.
- La distribution du portefeuille est plus pointue qu'une loi normale de même
	moyenne et de même écart-type, avec des queues plus épaisses.
- Le notebook rapporte un kurtosis d'environ **5,07** et une skewness positive
	d'environ **0,20**. Cela indique des mouvements extrêmes plus fréquents que
	sous l'hypothèse normale et une légère asymétrie positive.

### VaR journalière du portefeuille équipondéré

| Niveau de confiance | Paramétrique | Historique | Monte Carlo |
|---:|---:|---:|---:|
| 95 % | 1,2723 % | 1,2299 % | 1,2846 % |
| 99 % | 1,8222 % | 2,0823 % | 1,8951 % |

À 99 %, la VaR historique est la plus élevée. Elle reflète davantage les
observations extrêmes présentes dans l'échantillon que les modèles basés sur
une loi normale.

### Backtesting et Kupiec

Sur les environ 1 254 observations, le nombre théorique d'exceptions est
d'environ 63 à 95 % et 13 à 99 %. L'analyse du notebook conclut que les trois
méthodes ne sont pas rejetées par le test de Kupiec aux seuils étudiés. La
méthode historique est celle qui se rapproche le plus des fréquences théoriques
dans le backtesting présenté, mais ce résultat ne suffit pas à établir qu'elle
sera la meilleure méthode hors échantillon.

### Classification des régimes

Le notebook rapporte **65 jours de stress détectés sur 247 jours de test** par
les modèles avec les quatre variables internes au portefeuille. Les résultats
suggèrent un signal prédictif limité pour un horizon de cinq jours. Une piste
d'amélioration identifiée est l'ajout du VIX, qui apporterait une mesure
externe du stress de marché.

## Installation et exécution

Créer un environnement Python, puis installer les dépendances utilisées par le
notebook :

```bash
python -m venv .venv
```

Sous Windows PowerShell :

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install numpy pandas scipy matplotlib seaborn scikit-learn yfinance pyarrow jupyter
```

Ouvrir ensuite [`pipeline.ipynb`](pipeline.ipynb) dans VS Code ou Jupyter et
exécuter les cellules dans l'ordre. L'accès réseau est nécessaire pour
télécharger les cours avec `yfinance`. Pour obtenir des résultats Monte Carlo
reproductibles, définir une graine avant la simulation, par exemple :

```python
np.random.seed(42)
```

## Organisation du dépôt

```text
.
├── pipeline.ipynb          # analyse complète et résultats
├── notebooks/              # notebooks d'exploration
├── src/
│   ├── data_ingestion.py   # prototype d'ingestion yfinance
│   ├── var_models.py       # emplacement des modèles de VaR
│   ├── backtesting.py      # emplacement du backtesting
│   ├── regime_model.py     # emplacement du modèle de régime
│   └── pipeline.py         # orchestration prévue
├── tests/                  # tests à compléter
├── returns.csv             # rendements exportés
├── config.yaml             # configuration prévue
└── requirements.txt        # dépendances à formaliser
```

## Limites et prochaines étapes

- Les modules de `src/`, les tests, `config.yaml` et `requirements.txt` sont
	encore des prototypes ou des fichiers à compléter ; le notebook constitue
	actuellement l'implémentation de référence.
- Les VaR sont estimées sur un échantillon historique unique et ne modélisent
	pas explicitement la volatilité conditionnelle ni les changements de régime.
- Le seuil de volatilité future est calculé sur l'ensemble de l'historique ;
	pour une évaluation strictement hors échantillon, il devrait être estimé
	uniquement sur la période d'entraînement.
- Les valeurs de VaR devraient être recalculées automatiquement plutôt que
	recopiées dans les cellules de backtesting.
- Les prochaines améliorations naturelles sont l'ajout du VIX, d'un modèle
	GARCH ou d'une distribution à queues épaisses, ainsi que la migration de la
	logique du notebook vers les modules testés de `src/`.
