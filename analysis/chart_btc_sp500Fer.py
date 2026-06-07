# =============================================================================
# Graphique combine BTC + SP500
# Axe gauche : SP500 (prix reel)
# Axe droit  : BTC (prix reel)
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
    collection = get_collection(collection_name)
    documents  = list(collection.find({}, {"_id": 0}).sort("timestamp", 1))
    df         = pd.DataFrame(documents)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
    return df


def creer_graphique():
    print("Chargement des donnees depuis MongoDB...")

    df_btc = load_collection("btc_price_1d")
    df_sp  = load_collection("sp500_price_1d")

    # Aligner sur la periode commune
    start = max(df_btc.index[0], df_sp.index[0])
    end   = min(df_btc.index[-1], df_sp.index[-1])

    btc_close = df_btc.loc[start:end, "close"]
    sp_close  = df_sp.loc[start:end,  "close"]

    fig, ax1 = plt.subplots(figsize=(14, 6))
    fig.suptitle("BTC vs SP500 — Prix reels", fontsize=15, fontweight="bold")

    # Axe gauche : SP500
    color_sp = "#1f77b4"
    ax1.set_ylabel("SP500 (USD)", color=color_sp, fontsize=11)
    ax1.plot(sp_close.index, sp_close.values, label="SP500", color=color_sp, linewidth=1.5)
    ax1.tick_params(axis="y", labelcolor=color_sp)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    ax1.grid(True, alpha=0.2)

    # Axe droit : BTC
    color_btc = "#F7931A"
    ax2 = ax1.twinx()
    ax2.set_ylabel("BTC (USD)", color=color_btc, fontsize=11)
    ax2.plot(btc_close.index, btc_close.values, label="BTC", color=color_btc, linewidth=1.5)
    ax2.tick_params(axis="y", labelcolor=color_btc)

    # Legende combinee
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.tight_layout()

    os.makedirs(os.path.join(ROOT, "exports"), exist_ok=True)
    chemin = os.path.join(ROOT, "exports", "btc_sp500.png")
    plt.savefig(chemin, dpi=150, bbox_inches="tight")
    print(f"Graphique sauvegarde : {chemin}")
    return chemin


if __name__ == "__main__":
    creer_graphique()