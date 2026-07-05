# =============================================================================
# Chomage USA - Collecteur via FRED API
# Serie : UNRATE (Unemployment Rate)
# Collection MongoDB : unemployment_usa
# Donnees mensuelles depuis janvier 2019
# =============================================================================

import sys
import os
import requests
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv
from database.mongo_client import get_collection

load_dotenv()

FRED_API_KEY    = os.getenv("FRED_API_KEY")
SERIES_ID       = "UNRATE"
COLLECTION_NAME = "unemployment_usa"
START_DATE      = "2019-01-01"
FRED_URL        = "https://api.stlouisfed.org/fred/series/observations"


def fetch_unemployment():
    print("Telechargement des donnees de chomage depuis FRED...")
    params = {
        "series_id":         SERIES_ID,
        "api_key":           FRED_API_KEY,
        "file_type":         "json",
        "observation_start": START_DATE
    }
    response     = requests.get(FRED_URL, params=params)
    data         = response.json()
    observations = data.get("observations", [])
    print(f"Observations recuperees : {len(observations)}")
    return observations


def save_to_mongo(observations):
    collection = get_collection(COLLECTION_NAME)
    saved = 0
    for obs in observations:
        if obs["value"] == ".":
            continue
        doc = {
            "timestamp": datetime.strptime(obs["date"], "%Y-%m-%d"),
            "value":     round(float(obs["value"]), 2),
            "series":    SERIES_ID,
            "source":    "fred"
        }
        result = collection.update_one(
            {"timestamp": doc["timestamp"], "series": doc["series"]},
            {"$set": doc},
            upsert=True
        )
        if result.upserted_id:
            saved += 1
    total = collection.count_documents({})
    print(f"Nouvelles insertions : {saved}")
    print(f"Total en base        : {total} documents")


def run():
    print("=" * 60)
    print("Chomage USA - Collecteur FRED API")
    print(f"Serie      : {SERIES_ID}")
    print(f"Collection : {COLLECTION_NAME}")
    print(f"Depuis     : {START_DATE}")
    print("=" * 60)
    if not FRED_API_KEY:
        print("Erreur : FRED_API_KEY manquante dans .env")
        return
    observations = fetch_unemployment()
    if observations:
        save_to_mongo(observations)
        print("\nCollecte terminee avec succes")
    else:
        print("\nAucune donnee recuperee")


if __name__ == "__main__":
    run()