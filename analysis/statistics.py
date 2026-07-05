# =============================================================================
# Statistiques et Correlations - BTC vs Macro
# Rendements, volatilite, correlations chiffrees
# =============================================================================

import sys
import os
import pandas as pd
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from database.mongo_client import get_collection


# =============================================================================
# CHARGEMENT DES DONNEES
# =============================================================================

def load_serie(collection_name, colonne="close"):
    """
    Charge une serie de prix depuis MongoDB.

    Parametres :
        collection_name (str) : Nom de la collection
        colonne         (str) : Colonne a charger (close ou value)

    Retourne :
        Series pandas avec index timestamp
    """
    collection = get_collection(collection_name)
    documents  = list(collection.find({}, {"_id": 0}).sort("timestamp", 1))
    df         = pd.DataFrame(documents)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
    return df[colonne].astype(float)


# =============================================================================
# CALCULS STATISTIQUES
# =============================================================================

def calcul_rendement_total(serie):
    """
    Calcule le rendement total depuis le debut.
    Ex : +1050% depuis janvier 2020
    """
    return ((serie.iloc[-1] / serie.iloc[0]) - 1) * 100


def calcul_volatilite_annuelle(serie):
    """
    Calcule la volatilite annualisee (ecart-type des rendements quotidiens).
    """
    rendements = serie.pct_change().dropna()
    return rendements.std() * np.sqrt(252) * 100


def calcul_max_drawdown(serie):
    """
    Calcule le maximum drawdown — perte maximale depuis un sommet.
    """
    cummax = serie.cummax()
    drawdown = (serie - cummax) / cummax * 100
    return drawdown.min()


def calcul_correlation(serie1, serie2):
    """
    Calcule la correlation de Pearson entre deux series.
    Resample en mensuel pour aligner les dates.

    Retourne :
        float : Coefficient de correlation entre -1 et 1
    """
    # Resample en mensuel pour aligner les deux series
    s1 = serie1.resample("M").last()
    s2 = serie2.resample("M").last()

    # Aligner sur les dates communes
    df = pd.DataFrame({"s1": s1, "s2": s2}).dropna()

    if len(df) < 2:
        return 0.0

    return df["s1"].corr(df["s2"])


def calcul_rendement_annuel(serie):
    """
    Calcule le rendement moyen par annee.
    """
    rendements = serie.pct_change().dropna()
    return rendements.mean() * 252 * 100


# =============================================================================
# RAPPORT COMPLET
# =============================================================================

def generer_statistiques():
    """
    Genere toutes les statistiques du projet.

    Retourne :
        dict : Toutes les statistiques formatees
    """
    print("Chargement des donnees...")

    # Chargement des series
    btc  = load_serie("btc_price_1d",  "close")
    sp   = load_serie("sp500_price_1d", "close")
    oil  = load_serie("oil_price_1d",  "close")
    gold = load_serie("gold_price_1d", "close")

    print("Calcul des statistiques...")

    stats = {
        # Rendements totaux
        "btc_rendement_total":  round(calcul_rendement_total(btc),  1),
        "sp_rendement_total":   round(calcul_rendement_total(sp),   1),
        "oil_rendement_total":  round(calcul_rendement_total(oil),  1),
        "gold_rendement_total": round(calcul_rendement_total(gold), 1),

        # Volatilite annualisee
        "btc_volatilite":  round(calcul_volatilite_annuelle(btc),  1),
        "sp_volatilite":   round(calcul_volatilite_annuelle(sp),   1),
        "oil_volatilite":  round(calcul_volatilite_annuelle(oil),  1),
        "gold_volatilite": round(calcul_volatilite_annuelle(gold), 1),

        # Max Drawdown
        "btc_drawdown":  round(calcul_max_drawdown(btc),  1),
        "sp_drawdown":   round(calcul_max_drawdown(sp),   1),
        "oil_drawdown":  round(calcul_max_drawdown(oil),  1),
        "gold_drawdown": round(calcul_max_drawdown(gold), 1),

        # Correlations avec BTC
        "corr_btc_sp":   round(calcul_correlation(btc, sp),   2),
        "corr_btc_oil":  round(calcul_correlation(btc, oil),  2),
        "corr_btc_gold": round(calcul_correlation(btc, gold), 2),

        # Prix actuels
        "btc_prix":  round(btc.iloc[-1],  0),
        "sp_prix":   round(sp.iloc[-1],   0),
        "oil_prix":  round(oil.iloc[-1],  2),
        "gold_prix": round(gold.iloc[-1], 0),

        # Periode
        "debut": btc.index[0].strftime("%Y-%m-%d"),
        "fin":   btc.index[-1].strftime("%Y-%m-%d"),
    }

    return stats


# =============================================================================
# POINT D'ENTREE
# =============================================================================

def run():
    stats = generer_statistiques()

    print("\n" + "=" * 60)
    print("STATISTIQUES DU PROJET")
    print("=" * 60)
    print(f"Periode analysee : {stats['debut']} -> {stats['fin']}")

    print("\n--- Rendements totaux ---")
    print(f"BTC  : +{stats['btc_rendement_total']}%")
    print(f"SP500: +{stats['sp_rendement_total']}%")
    print(f"Or   : +{stats['gold_rendement_total']}%")
    print(f"WTI  : +{stats['oil_rendement_total']}%")

    print("\n--- Volatilite annualisee ---")
    print(f"BTC  : {stats['btc_volatilite']}%")
    print(f"SP500: {stats['sp_volatilite']}%")
    print(f"Or   : {stats['gold_volatilite']}%")
    print(f"WTI  : {stats['oil_volatilite']}%")

    print("\n--- Max Drawdown ---")
    print(f"BTC  : {stats['btc_drawdown']}%")
    print(f"SP500: {stats['sp_drawdown']}%")
    print(f"Or   : {stats['gold_drawdown']}%")
    print(f"WTI  : {stats['oil_drawdown']}%")

    print("\n--- Correlations avec BTC ---")
    print(f"BTC / SP500 : {stats['corr_btc_sp']}")
    print(f"BTC / Or    : {stats['corr_btc_gold']}")
    print(f"BTC / Petrole: {stats['corr_btc_oil']}")

    print("=" * 60)

    return stats


if __name__ == "__main__":
    run()