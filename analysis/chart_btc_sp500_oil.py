# =============================================================================
# Graphique combine BTC + SP500 + Petrole
# Sauvegarde en PNG et affichage via Flask
# =============================================================================

import sys
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from database.mongo_client import get_collection


def load_collection(collection_name):
    """
    Charge une collection MongoDB en DataFrame pandas.
    """
    collection = get_collection(collection_name)
    documents  = list(collection.find({}, {"_id": 0}).sort("timestamp", 1))
    df         = pd.DataFrame(documents)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
    return df


def normaliser(serie):
    """
    Normalise une serie a base 100 pour comparer sur le meme graphique.
    """
    return (serie / serie.iloc[0]) * 100


def creer_graphique():
    """
    Cree le graphique combine et le sauvegarde en PNG.
    """
    print("Chargement des donnees depuis MongoDB...")

    df_btc = load_collection("btc_price_1d")
    df_sp  = load_collection("sp500_price_1d")
    df_oil = load_collection("oil_price_1d")

    # Aligner sur la periode commune
    start = max(df_btc.index[0], df_sp.index[0], df_oil.index[0])
    end   = min(df_btc.index[-1], df_sp.index[-1], df_oil.index[-1])

    btc_close = df_btc.loc[start:end, "close"]
    sp_close  = df_sp.loc[start:end,  "close"]
    oil_close = df_oil.loc[start:end, "close"]

    # Normalisation base 100
    btc_norm = normaliser(btc_close)
    sp_norm  = normaliser(sp_close)
    oil_norm = normaliser(oil_close)

    # Creation du graphique
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    fig.suptitle("BTC vs SP500 vs Petrole", fontsize=16, fontweight="bold")

    # Graphique 1 : Performance normalisee base 100
    ax1 = axes[0]
    ax1.plot(btc_norm.index, btc_norm.values, label="BTC",     color="#F7931A", linewidth=1.5)
    ax1.plot(sp_norm.index,  sp_norm.values,  label="SP500",   color="#1f77b4", linewidth=1.5)
    ax1.plot(oil_norm.index, oil_norm.values, label="Petrole", color="#2ca02c", linewidth=1.5)
    ax1.set_title("Performance normalisee base 100")
    ax1.set_ylabel("Indice base 100")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

    # Graphique 2 : Prix reel BTC
    ax2 = axes[1]
    ax2.plot(btc_close.index, btc_close.values, color="#F7931A", linewidth=1.5)
    ax2.set_title("Prix BTC en USD")
    ax2.set_ylabel("Prix USD")
    ax2.set_xlabel("Date")
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

    plt.tight_layout()

    # Sauvegarder en PNG
    os.makedirs("exports", exist_ok=True)
    chemin = os.path.join(ROOT, "exports", "btc_sp500_oil.png")
    plt.savefig(chemin, dpi=150, bbox_inches="tight")
    print(f"Graphique sauvegarde : {chemin}")
    return chemin


if __name__ == "__main__":
    creer_graphique()