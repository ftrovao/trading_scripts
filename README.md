# Trading Dashboard - Détection de signaux crypto

Système automatisé de détection de signaux de trading pour le marché
des futures Bitcoin, basé sur l'analyse de données macroéconomiques
et d'indicateurs techniques, avec intégration d'un modèle IA (Claude).

---

## Objectif

Détecter les entrées potentielles sur le marché des futures BTC
(positions LONG ou SHORT) en combinant :
- Les données de prix du Bitcoin (Binance API)
- Les indicateurs macroéconomiques américains (FRED API)
- Les marchés traditionnels (SP500, pétrole, or, argent)
- Les indicateurs techniques (RSI, MACD)
- L'analyse par intelligence artificielle (Claude API)

---

## Architecture
trading_scripts/
├── collectors/
│   └── macro/
│       ├── btc_price.py         # Prix BTC via Binance API
│       ├── sp500_price.py       # SP500 via yfinance
│       ├── oil_price.py         # Pétrole WTI via yfinance
│       ├── gold_silver.py       # Or et Argent via yfinance
│       ├── inflation_usa.py     # Inflation CPI via FRED API
│       └── unemployment_usa.py  # Chômage US via FRED API
├── database/
│   └── mongo_client.py          # Connexion MongoDB Atlas
├── analysis/
│   ├── indicators.py            # RSI et MACD
│   └── statistics.py            # Statistiques et corrélations
├── llm/
│   └── signal_generator.py      # Analyse IA via Claude API
├── dashboard/
│   └── app.py                   # Dashboard Flask
├── scheduler.py                 # Mise à jour automatique des données
└── requirements.txt
---

## Technologies utilisées

| Categorie | Technologie |
|---|---|
| Langage | Python 3.11 |
| Base de données | MongoDB Atlas |
| APIs données | Binance, yfinance, FRED |
| Analyse | pandas, numpy |
| Visualisation | matplotlib |
| IA | Claude API (Anthropic) |
| Dashboard | Flask |
| Environnement | Ubuntu 24.04 (WSL2) + Anaconda |
| Versionnement | Git + GitHub |

---

## APIs gratuites utilisées

| Source | Données | Collection MongoDB |
|---|---|---|
| Binance API | Prix BTC OHLCV | btc_price_1d, btc_price_4h |
| yfinance | SP500, Pétrole, Or, Argent | sp500_price_1d, oil_price_1d, gold_price_1d, silver_price_1d |
| FRED API | Inflation CPI, Chômage US | inflation_usa, unemployment_usa |

---

## Données collectées

| Collection | Documents | Période |
|---|---|---|
| btc_price_1d | 2378 bougies | Jan 2020 - Juil 2026 |
| btc_price_4h | 14021 bougies | Jan 2020 - Juil 2026 |
| sp500_price_1d | 1866 documents | Jan 2019 - Juil 2026 |
| oil_price_1d | 1868 documents | Jan 2019 - Juil 2026 |
| gold_price_1d | 1888 documents | Jan 2019 - Juil 2026 |
| silver_price_1d | 1888 documents | Jan 2019 - Juil 2026 |
| inflation_usa | 88 documents | Jan 2019 - Juil 2026 |
| unemployment_usa | 88 documents | Jan 2019 - Juil 2026 |

---

## Indicateurs techniques

### RSI (Relative Strength Index)
- Période : 14 jours
- RSI > 70 : Zone de surachat → signal potentiel SHORT
- RSI < 30 : Zone de survente → signal potentiel LONG

### MACD (Moving Average Convergence Divergence)
- Paramètres : 12 / 26 / 9
- MACD > Signal : momentum haussier → signal potentiel LONG
- MACD < Signal : momentum baissier → signal potentiel SHORT

### Signal final
- LONG : RSI et MACD confirment tous les deux une tendance haussière
- SHORT : RSI et MACD confirment tous les deux une tendance baissière
- NEUTRE : Signaux contradictoires ou zone neutre

---

## Statistiques clés (2020 - 2026)

| Actif | Rendement total | Volatilité annuelle | Max Drawdown |
|---|---|---|---|
| BTC | +771.6% | 50.6% | -76.6% |
| SP500 | +202.2% | 19.6% | -33.9% |
| Or | +226.9% | 18.0% | -25.0% |
| Pétrole | +99.9% | 131.7% | -156.8% |

### Corrélations avec BTC
- BTC / SP500 : **0.87** — très forte corrélation
- BTC / Or : **0.71** — corrélation modérée
- BTC / Pétrole : **0.15** — faible corrélation

---

## Installation

### Prérequis
- Windows avec WSL2 (Ubuntu 24.04)
- Anaconda installé dans WSL2
- Compte MongoDB Atlas (gratuit)
- Clé API FRED (gratuite)
- Clé API Anthropic

### 1. Cloner le projet

```bash
git clone https://github.com/ftrovao/trading_scripts.git
cd trading_scripts
```

### 2. Créer l'environnement

```bash
conda create -n crypto_signals python=3.11 -y
conda activate crypto_signals
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement

Créer un fichier `.env` à la racine :

MONGO_URI=mongodb+srv://utilisateur:motdepasse@cluster.mongodb.net/?appName=Cluster0
FRED_API_KEY=votre_cle_fred
ANTHROPIC_API_KEY=votre_cle_anthropic

### 4. Collecter les données

```bash
python collectors/macro/btc_price.py
python collectors/macro/sp500_price.py
python collectors/macro/oil_price.py
python collectors/macro/gold_silver.py
python collectors/macro/inflation_usa.py
python collectors/macro/unemployment_usa.py
```

### 5. Lancer le dashboard

```bash
# Terminal 1 - Dashboard
python dashboard/app.py

# Terminal 2 - Mise à jour automatique
python scheduler.py
```

Ouvrir dans le navigateur : **http://localhost:5000**

---

## Dashboard

Le dashboard Flask propose deux pages :

### Page principale - Dashboard
- Prix en temps réel : BTC, SP500, Pétrole, RSI, Inflation
- Signal de trading : LONG / SHORT / NEUTRE
- 5 graphiques navigables :
  - BTC x SP500
  - BTC x Pétrole
  - BTC x Inflation USA
  - RSI (14)
  - MACD (12/26/9)
- Analyse IA automatique par Claude
- Chat interactif pour poser des questions

### Page statistiques
- Rendements totaux et annuels
- Volatilité annualisée et Max Drawdown
- Corrélations entre BTC et les actifs macro
- Graphique de performance normalisée base 100

---

## Mise à jour automatique

Le scheduler met à jour les données automatiquement :

```bash
python scheduler.py
```

- BTC : toutes les 4 heures
- Macro (SP500, pétrole, or, argent, inflation, chômage) : tous les jours à 06h00

---

## Auteur

**Ousmane BAH**
Étudiant en Techniques de l'informatique
Collège Grasset — Montréal, Québec

Projet de stage supervisé par **Fernando Trovao**
Session été 2026

---

## Licence

Projet académique — Collège Grasset 2026