# =============================================================================
# Or et Argent - Collecteur via yfinance
# Tickers : GC=F (Or), SI=F (Argent)
# Collections MongoDB : gold_price_1d, silver_price_1d
# Donnees depuis janvier 2019
# =============================================================================

import sys
import os
import yfinance as yf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from database.mongo_client import get_collection

# =============================================================================
# CONFIGURATION
# =============================================================================

START_DATE = "2019-01-01"

METALS = {
    "gold_price_1d":   "GC=F",   # Or futures
    "silver_price_1d": "SI=F"    # Argent futures
}

# =============================================================================
# COLLECTE ET SAUVEGARDE
# =============================================================================

def fetch_and_save(ticker, collection_name):
    """
    Recupere les prix d'un metal precieux via yfinance
    et les sauvegarde dans MongoDB Atlas.

    Parametres :
        ticker          (str) : Symbole yfinance ex: 'GC=F'
        collection_name (str) : Nom de la collection MongoDB
    """
    print(f"\nTelechargement {ticker}...")
    df = yf.download(ticker, start=START_DATE, auto_adjust=True)

    if df.empty:
        print(f"Aucune donnee pour {ticker}")
        return

    print(f"Lignes recuperees : {len(df)}")

    collection = get_collection(collection_name)
    saved = 0

    for date, row in df.iterrows():
        doc = {
            "timestamp": date.to_pydatetime(),
            "open":      round(float(row["Open"].iloc[0]),   2),
            "high":      round(float(row["High"].iloc[0]),   2),
            "low":       round(float(row["Low"].iloc[0]),    2),
            "close":     round(float(row["Close"].iloc[0]),  2),
            "volume":    round(float(row["Volume"].iloc[0]), 2),
            "ticker":    ticker,
            "source":    "yfinance"
        }

        result = collection.update_one(
            {"timestamp": doc["timestamp"]},
            {"$set": doc},
            upsert=True
        )

        if result.upserted_id:
            saved += 1

    total = collection.count_documents({})
    print(f"Nouvelles insertions : {saved}")
    print(f"Total en base        : {total} documents")


# =============================================================================
# POINT D'ENTREE
# =============================================================================

def run():
    print("=" * 60)
    print("Or et Argent - Collecteur yfinance")
    print(f"Depuis : {START_DATE}")
    print("=" * 60)

    for collection_name, ticker in METALS.items():
        fetch_and_save(ticker, collection_name)

    print("\n" + "=" * 60)
    print("Collecte terminee avec succes")
    print("=" * 60)


if __name__ == "__main__":
    run()