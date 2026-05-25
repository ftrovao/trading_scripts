# =============================================================================
# BTC Price Collector - Binance API
# Collecte les bougies OHLCV du BTC depuis janvier 2020
# Collections : btc_price_1d (journalier) et btc_price_4h (4 heures)
# =============================================================================

import requests
import sys
import os
from datetime import datetime
import time

# Ajout du dossier racine au path pour les imports internes
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from database.mongo_client import get_collection

# =============================================================================
# CONFIGURATION
# =============================================================================

BINANCE_URL = "https://api.binance.com/api/v3/klines"
SYMBOL      = "BTCUSDT"       # Paire de trading Bitcoin / USDT
START_MS    = 1577836800000   # Timestamp Unix en ms : 2020-01-01 00:00:00 UTC

# Dictionnaire des timeframes a collecter
# cle    = nom de la collection MongoDB
# valeur = intervalle Binance
TIMEFRAMES = {
    "btc_price_1d": "1d",   # Une bougie par jour
    "btc_price_4h": "4h"    # Une bougie par 4 heures
}

# =============================================================================
# RECUPERATION DES BOUGIES DEPUIS BINANCE
# =============================================================================

def fetch_candles(interval, start_ms):
    """
    Recupere toutes les bougies OHLCV depuis Binance API.

    Binance limite chaque reponse a 1000 bougies maximum.
    La fonction boucle en avancant le timestamp de depart
    jusqu'a recuperer toutes les donnees disponibles.

    Parametres :
        interval  (str) : Intervalle Binance ex: '1d', '4h'
        start_ms  (int) : Timestamp de depart en millisecondes

    Retourne :
        list : Liste brute des bougies Binance
    """
    all_candles = []
    current_ms  = start_ms
    call_count  = 0

    while True:

        # Parametres de la requete Binance
        params = {
            "symbol":    SYMBOL,
            "interval":  interval,
            "startTime": current_ms,
            "limit":     1000        # Maximum autorise par Binance
        }

        response = requests.get(BINANCE_URL, params=params)
        call_count += 1

        # Verification du statut de la reponse HTTP
        if response.status_code != 200:
            print(f"Erreur Binance API : statut {response.status_code}")
            break

        candles = response.json()

        # Si la reponse est vide, toutes les donnees ont ete recuperees
        if not candles:
            break

        all_candles.extend(candles)
        print(f"Appel #{call_count} - {len(all_candles)} bougies recuperees")

        # Moins de 1000 resultats signifie que c'est le dernier batch
        if len(candles) < 1000:
            break

        # Avancer le timestamp au-dela de la derniere bougie recue
        # +1 ms pour eviter de recuperer la meme bougie deux fois
        current_ms = candles[-1][0] + 1

        # Pause pour respecter les limites de taux Binance
        # Binance autorise 1200 requetes par minute
        time.sleep(0.3)

    print(f"Total appels API : {call_count}")
    return all_candles


# =============================================================================
# FORMATAGE D'UNE BOUGIE
# =============================================================================

def format_candle(candle, interval):
    """
    Transforme une bougie brute Binance en document MongoDB.

    Format brut Binance (liste) :
        [0]  timestamp open  (ms)
        [1]  open price
        [2]  high price
        [3]  low price
        [4]  close price
        [5]  volume
        [6+] autres champs ignores

    Parametres :
        candle   (list) : Bougie brute retournee par Binance
        interval (str)  : Intervalle de la bougie ex: '1d', '4h'

    Retourne :
        dict : Document formate pour MongoDB
    """
    return {
        "timestamp": datetime.fromtimestamp(candle[0] / 1000),  # ms vers datetime
        "open":      float(candle[1]),
        "high":      float(candle[2]),
        "low":       float(candle[3]),
        "close":     float(candle[4]),
        "volume":    float(candle[5]),
        "timeframe": interval,
        "source":    "binance"
    }


# =============================================================================
# SAUVEGARDE DANS MONGODB
# =============================================================================

def save_candles(candles, collection_name, interval):
    """
    Sauvegarde les bougies dans MongoDB Atlas.

    Utilise upsert pour eviter les doublons :
    - Si le document existe deja (meme timestamp + timeframe) : mise a jour
    - Si le document n'existe pas : insertion

    Parametres :
        candles         (list) : Liste de bougies brutes Binance
        collection_name (str)  : Nom de la collection MongoDB cible
        interval        (str)  : Intervalle de la bougie
    """
    collection  = get_collection(collection_name)
    saved_count = 0

    for candle in candles:

        # Formatage de la bougie brute en document MongoDB
        doc = format_candle(candle, interval)

        # Upsert : insertion ou mise a jour selon l'existence du document
        # Le filtre combine timestamp + timeframe pour identifier chaque bougie
        result = collection.update_one(
            filter = {"timestamp": doc["timestamp"], "timeframe": doc["timeframe"]},
            update = {"$set": doc},
            upsert = True
        )

        # upserted_id est defini uniquement lors d'une nouvelle insertion
        if result.upserted_id:
            saved_count += 1

    total_documents = collection.count_documents({})
    print(f"Nouvelles bougies inserees    : {saved_count}")
    print(f"Total documents en base       : {total_documents}")


# =============================================================================
# POINT D'ENTREE PRINCIPAL
# =============================================================================

def run():
    """
    Fonction principale du collecteur BTC.

    Itere sur chaque timeframe defini dans TIMEFRAMES,
    recupere les bougies depuis Binance depuis janvier 2020,
    et les sauvegarde dans la collection MongoDB correspondante.
    """
    print("=" * 60)
    print("BTC Price Collector - Binance API")
    print("Periode : janvier 2020 -> aujourd'hui")
    print("=" * 60)

    for collection_name, interval in TIMEFRAMES.items():

        print(f"\nCollecte en cours : {collection_name} (intervalle : {interval})")
        print("-" * 40)

        # Recuperation de toutes les bougies depuis Binance
        candles = fetch_candles(
            interval = interval,
            start_ms = START_MS
        )

        if candles:
            print(f"Bougies recuperees : {len(candles)}")
            save_candles(candles, collection_name, interval)
        else:
            print(f"Aucune donnee recuperee pour {interval}")

    print("\n" + "=" * 60)
    print("Collecte terminee avec succes")
    print("=" * 60)


if __name__ == "__main__":
    run()