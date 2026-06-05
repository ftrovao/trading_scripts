# Trading Scripts

Ce projet rassemble des scripts Python pour collecter, stocker et analyser des données de marché, notamment des données Bitcoin, SP500 et pétrole.

## Structure du projet

- `collectors/macro/` : collecteurs macroéconomiques pour les données de marché.
- `collectors/onchain/` : collecteurs on-chain / exchange (scaffold présent, contenu à compléter).
- `database/` : client MongoDB Atlas pour la connexion et l'accès aux collections.
- `analysis/` : scripts d'analyse et visualisation des séries de prix.
- `llm/` : génération de signaux basée sur des modèles ou des règles (module vide pour l'instant).
- `dashboard/` : interface Flask légère pour afficher les prix et un graphique.

## Fonctionnalités implémentées

### Collecteurs macro

- `collectors/macro/btc_price.py`
  - récupère les bougies OHLCV de `BTCUSDT` depuis l'API Binance
  - collecte les données depuis le 1er janvier 2020
  - stocke les documents dans MongoDB avec : `timestamp`, `open`, `high`, `low`, `close`, `volume`, `timeframe`, `source`
  - supporte deux collections : `btc_price_1d` et `btc_price_4h`
  - utilise `upsert` pour éviter les doublons

- `collectors/macro/sp500_price.py`
  - récupère les données journalières du SP500 via `yfinance` (`^GSPC`)
  - stocke les données dans la collection `sp500_price_1d`
  - collecte les données depuis le 1er janvier 2019

- `collectors/macro/oil_price.py`
  - récupère les données journalières du WTI via `yfinance` (`CL=F`)
  - stocke les données dans la collection `oil_price_1d`
  - collecte les données depuis le 1er janvier 2019

### Base de données

- `database/mongo_client.py`
  - charge la variable `MONGO_URI` depuis `.env`
  - renvoie une collection MongoDB depuis la base `trading_db`
  - inclut une fonction de test de connexion

### Analyse et visualisation

- `analysis/chart_btc_sp500_oil.py`
  - charge les séries `btc_price_1d`, `sp500_price_1d` et `oil_price_1d`
  - normalise chaque série sur une base 100
  - créé un graphique comparatif et le sauvegarde dans `exports/btc_sp500_oil.png`

### Dashboard

- `dashboard/app.py`
  - application Flask simple
  - affiche les derniers prix de BTC, SP500 et pétrole
  - intègre une image PNG générée dans `exports/btc_sp500_oil.png`

## Etat actuel des fichiers

- `requirements.txt` est rempli avec les dépendances nécessaires : `pymongo`, `python-dotenv`, `requests`, `yfinance`, `pandas`, `numpy`, `matplotlib`, `seaborn`, `flask`, `python-dateutil`.
- `docker-compose.yml` reste vide.
- `Dockerfile` reste vide.
- `collectors/onchain/` contient des fichiers vides ou en attente de développement.
- `analysis/indicators.py`, `analysis/fibonacci.py`, `analysis/mvrv.py` sont pour l’instant des placeholders.
- `llm/signal_generator.py` est actuellement vide.

## Prérequis

- Python 3.x
- `pip install -r requirements.txt`

## Configuration

1. Créez un fichier `.env` à la racine du projet.
2. Ajoutez la variable MongoDB :

```env
MONGO_URI=<votre_mongo_uri>
```

## Exécution

### Collecteurs

- BTC :

```bash
python collectors/macro/btc_price.py
```

- SP500 :

```bash
python collectors/macro/sp500_price.py
```

- Pétrole :

```bash
python collectors/macro/oil_price.py
```

### Analyse

```bash
python analysis/chart_btc_sp500_oil.py
```

### Dashboard

```bash
python dashboard/app.py
```

Ensuite, ouvrez `http://127.0.0.1:5000` dans votre navigateur.

## Notes

- Le projet contient déjà des collecteurs fonctionnels pour BTC, SP500 et pétrole.
- Les autres collecteurs macro et on-chain sont en structure de projet mais restent à implémenter.
- Le dashboard Flask affiche des données stockées en base et dépend du graphique exporté dans `exports/btc_sp500_oil.png`.
