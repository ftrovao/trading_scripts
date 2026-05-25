# Trading Scripts

Ce projet rassemble des scripts Python pour collecter, stocker et analyser des données de marché, en particulier des données Bitcoin et des indicateurs macroéconomiques.

## Structure du projet

- `collectors/macro/` : collecteurs macroéconomiques pour les données BTC et d'autres indicateurs (prix BTC, DXY, inflation, pétrole, chômage, MSTR).
- `collectors/onchain/` : collecteurs de données on-chain et d'exchanges (structure présente, à compléter selon les besoins).
- `database/` : client MongoDB Atlas pour la connexion et l'accès aux collections.
- `analysis/` : scripts d'analyse et d'indicateurs (MVRV, Fibonacci, autres indicateurs techniques).
- `llm/` : génération de signaux basés sur des modèles ou des règles.
- `dashboard/` : interface de visualisation / dashboard (structure de dossier présente, à développer).

## Fonctionnalité principale

Le script `collectors/macro/btc_price.py` :

- récupère les bougies OHLCV de la paire `BTCUSDT` depuis l'API Binance
- collecte les données à partir du 1er janvier 2020
- stocke les données dans MongoDB avec des documents contenant : timestamp, open, high, low, close, volume, timeframe, source
- supporte deux timeframes : `btc_price_1d` et `btc_price_4h`
- utilise `upsert` pour éviter l'insertion de doublons

## Prérequis

- Python 3.x
- `requests`
- `pymongo`
- `python-dotenv`

> Les fichiers `requirements.txt`, `docker-compose.yml`, `Dockerfile` et `dashboard/app.py` sont présents dans le projet mais semblent actuellement vides. Ils peuvent être complétés ultérieurement selon l'environnement d'exécution et l'interface souhaitée.

## Configuration

1. Créez un fichier `.env` à la racine du projet.
2. Ajoutez la variable MongoDB :

```env
MONGO_URI=<votre_mongo_uri>
```

3. Installez les dépendances :

```bash
pip install requests pymongo python-dotenv
```

## Exécution

Pour lancer le collecteur BTC :

```bash
python collectors/macro/btc_price.py
```

Cela va récupérer les bougies Binance et les insérer dans les collections MongoDB : `btc_price_1d` et `btc_price_4h`.

## Remarques

- `database/mongo_client.py` gère la connexion à MongoDB Atlas via `MONGO_URI`.
- Le projet est conçu pour être étendu avec d'autres collecteurs et une interface de dashboard.
- Les fichiers de configuration Docker et le dashboard restent à implémenter.
