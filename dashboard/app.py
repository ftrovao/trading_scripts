# =============================================================================
# Dashboard Flask - BTC + SP500
# Graphique genere en memoire - pas de fichier PNG
# =============================================================================

import sys
import os
import base64
import io
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from flask import Flask, render_template_string
from database.mongo_client import get_collection

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Trading Dashboard</title>
    <style>
        body   { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        h1     { text-align: center; color: #F7931A; margin-bottom: 30px; }
        .stats { display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }
        .card  { background: #16213e; padding: 20px 30px; border-radius: 8px; text-align: center; }
        .val   { font-size: 26px; font-weight: bold; color: #F7931A; }
        .lbl   { font-size: 12px; color: #aaa; margin-top: 6px; }
        img    { max-width: 100%; border-radius: 8px; display: block; margin: 0 auto; }
    </style>
</head>
<body>
    <h1>Trading Dashboard</h1>

    <div class="stats">
        <div class="card">
            <div class="val">{{ btc_price }}</div>
            <div class="lbl">BTC Prix USD</div>
        </div>
        <div class="card">
            <div class="val">{{ sp500_price }}</div>
            <div class="lbl">SP500</div>
        </div>
        <div class="card">
            <div class="val">{{ oil_price }}</div>
            <div class="lbl">Petrole WTI USD</div>
        </div>
    </div>

    <img src="data:image/png;base64,{{ chart }}" alt="BTC vs SP500">

</body>
</html>
"""


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


def generer_graphique():
    """
    Genere le graphique BTC vs SP500 en memoire.
    Retourne une image encodee en base64.
    Aucun fichier PNG cree sur le disque.
    """
    df_btc = load_collection("btc_price_1d")
    df_sp  = load_collection("sp500_price_1d")

    # Aligner sur la periode commune
    start = max(df_btc.index[0], df_sp.index[0])
    end   = min(df_btc.index[-1], df_sp.index[-1])

    btc_close = df_btc.loc[start:end, "close"]
    sp_close  = df_sp.loc[start:end,  "close"]

    # Creation du graphique
    fig, ax1 = plt.subplots(figsize=(14, 6))
    fig.suptitle("BTC vs SP500 - Prix reels", fontsize=15, fontweight="bold")

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

    # Convertir en base64 en memoire - pas de fichier PNG
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close()

    return image_base64


@app.route("/")
def index():
    # Derniers prix depuis MongoDB
    btc = get_collection("btc_price_1d").find_one(sort=[("timestamp", -1)])
    sp  = get_collection("sp500_price_1d").find_one(sort=[("timestamp", -1)])
    oil = get_collection("oil_price_1d").find_one(sort=[("timestamp", -1)])

    # Generer le graphique en memoire
    chart = generer_graphique()

    return render_template_string(
        TEMPLATE,
        btc_price   = f"${btc['close']:,.0f}" if btc else "N/A",
        sp500_price = f"${sp['close']:,.0f}"  if sp  else "N/A",
        oil_price   = f"${oil['close']:,.2f}" if oil else "N/A",
        chart       = chart
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)