# =============================================================================
# SP500 - Collecteur via yfinance
# Ticker : ^GSPC
# Collection MongoDB : sp500_price_1d
# Donnees depuis janvier 2019
# =============================================================================

import sys
import os
import yfinance as yf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from database.mongo_client import get_collection

TICKER          = "^GSPC"
COLLECTION_NAME = "sp500_price_1d"
START_DATE      = "2019-01-01"


def fetch_and_save():
    print("=" * 60)
    print("SP500 - Collecteur yfinance")
    print(f"Ticker     : {TICKER}")
    print(f"Collection : {COLLECTION_NAME}")
    print(f"Depuis     : {START_DATE}")
    print("=" * 60)

    print("\nTelechargement en cours...")
    df = yf.download(TICKER, start=START_DATE, auto_adjust=True)

    if df.empty:
        print("Aucune donnee recuperee")
        return

    print(f"Lignes recuperees : {len(df)}")

    collection = get_collection(COLLECTION_NAME)
    saved = 0

    for date, row in df.iterrows():
        doc = {
            "timestamp": date.to_pydatetime(),
            "open":      round(float(row["Open"].iloc[0]),   2),
            "high":      round(float(row["High"].iloc[0]),   2),
            "low":       round(float(row["Low"].iloc[0]),    2),
            "close":     round(float(row["Close"].iloc[0]),  2),
            "volume":    round(float(row["Volume"].iloc[0]), 2),
            "ticker":    TICKER,
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
    print("\nCollecte terminee avec succes")


if __name__ == "__main__":
    fetch_and_save()