# =============================================================================
# Test - Recuperation des 6 bougies 4h d'une journee
# =============================================================================

import sys
import os
from datetime import datetime

# Pointer vers le dossier racine trading_scripts
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT)

from database.mongo_client import get_collection


def get_bougies_jour(annee, mois, jour):
    """
    Recupere les 6 bougies 4h d'une journee complete.

    Parametres :
        annee (int) : Annee ex: 2024
        mois  (int) : Mois  ex: 1
        jour  (int) : Jour  ex: 15

    Retourne :
        list : Les 6 bougies de la journee
    """
    collection = get_collection("btc_price_4h")

    debut = datetime(annee, mois, jour, 0, 0, 0)
    fin   = datetime(annee, mois, jour + 1, 0, 0, 0)

    bougies = collection.find({
        "timestamp": {
            "$gte": debut,
            "$lt":  fin
        }
    }).sort("timestamp", 1)

    return list(bougies)


def afficher_bougies(bougies):
    """
    Affiche les bougies dans le terminal de facon lisible.
    """
    print("=" * 60)
    print(f"Nombre de bougies : {len(bougies)}")
    print("=" * 60)
    print(f"{'Heure':<8} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Volume':>15}")
    print("-" * 60)

    for b in bougies:
        print(
            f"{b['timestamp'].strftime('%H:%M'):<8}"
            f"{b['open']:>10.2f}"
            f"{b['high']:>10.2f}"
            f"{b['low']:>10.2f}"
            f"{b['close']:>10.2f}"
            f"{b['volume']:>15.2f}"
        )


if __name__ == "__main__":

    # Changer la date ici pour tester un autre jour
    annee = 2024
    mois  = 1
    jour  = 15

    print(f"Bougies 4h du {jour}/{mois}/{annee}")
    bougies = get_bougies_jour(annee, mois, jour)

    if bougies:
        afficher_bougies(bougies)
    else:
        print("Aucune bougie trouvee pour cette date")