# =============================================================================
# Dashboard Flask - BTC vs SP500 / Petrole / Inflation
# Graphiques generes en memoire avec navigation par boutons
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

from flask import Flask, render_template_string, request
from database.mongo_client import get_collection

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Trading Dashboard</title>
    <style>
        body        { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        h1          { text-align: center; color: #F7931A; margin-bottom: 30px; }
        .stats      { display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }
        .card       { background: #16213e; padding: 20px 30px; border-radius: 8px; text-align: center; }
        .val        { font-size: 26px; font-weight: bold; color: #F7931A; }
        .lbl        { font-size: 12px; color: #aaa; margin-top: 6px; }
        .buttons    { display: flex; justify-content: center; gap: 12px; margin-bottom: 30px; flex-wrap: wrap; }
        .btn        { background: #16213e; color: #eee; border: 1px solid #333; padding: 10px 24px;
                      border-radius: 6px; cursor: pointer; font-size: 14px; text-decoration: none; }
        .btn:hover  { background: #1f2a4a; }
        .btn.active { background: #F7931A; color: #1a1a2e; font-weight: bold; border-color: #F7931A; }
        img         { max-width: 100%; border-radius: 8px; display: block; margin: 0 auto; }
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
        <div class="card">
            <div class="val">{{ inflation_value }}</div>
            <div class="lbl">Inflation US CPI</div>
        </div>
    </div>

    <div class="buttons">
        <a href="/?graph=sp500" class="btn {{ 'active' if graph == 'sp500' else '' }}">BTC x SP500</a>
        <a href="/?graph=oil" class="btn {{ 'active' if graph == 'oil' else '' }}">BTC x Petrole</a>
        <a href="/?graph=inflation" class="btn {{ 'active' if graph == 'inflation' else '' }}">BTC x Inflation</a>
    </div>

    <img src="data:image/png;base64,{{ chart }}" alt="Graphique">

</body>
</html>
"""


def load_collection(collection_name):
    """
    Charge une collection MongoDB en DataFrame pandas trie par date.
    """
    collection = get_collection(collection_name)
    documents  = list(collection.find({}, {"_id": 0}).sort("timestamp", 1))
    df         = pd.DataFrame(documents)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
    return df


def generer_graphique_double_axe(serie_gauche, serie_droite, nom_gauche, nom_droite, titre):
    """
    Genere un graphique a deux axes Y en memoire.
    Retourne une image encodee en base64. Aucun fichier PNG cree.

    Parametres :
        serie_gauche  (Series) : Donnees pour l'axe gauche
        serie_droite  (Series) : Donnees pour l'axe droit
        nom_gauche    (str)    : Nom affiche pour l'axe gauche
        nom_droite    (str)    : Nom affiche pour l'axe droit
        titre         (str)    : Titre du graphique
    """
    fig, ax1 = plt.subplots(figsize=(14, 6))
    fig.suptitle(titre, fontsize=15, fontweight="bold")

    color_gauche = "#1f77b4"
    ax1.set_ylabel(f"{nom_gauche}", color=color_gauche, fontsize=11)
    ax1.plot(serie_gauche.index, serie_gauche.values, label=nom_gauche, color=color_gauche, linewidth=1.5)
    ax1.tick_params(axis="y", labelcolor=color_gauche)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    ax1.grid(True, alpha=0.2)

    color_droite = "#F7931A"
    ax2 = ax1.twinx()
    ax2.set_ylabel(f"{nom_droite}", color=color_droite, fontsize=11)
    ax2.plot(serie_droite.index, serie_droite.values, label=nom_droite, color=color_droite, linewidth=1.5)
    ax2.tick_params(axis="y", labelcolor=color_droite)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close()

    return image_base64


def get_chart(graph_type):
    """
    Genere le graphique demande selon le type choisi par l'utilisateur.

    Parametres :
        graph_type (str) : 'sp500', 'oil' ou 'inflation'
    """
    df_btc = load_collection("btc_price_1d")
    btc_close = df_btc["close"]

    if graph_type == "oil":
        df_oil    = load_collection("oil_price_1d")
        start     = max(df_btc.index[0], df_oil.index[0])
        end       = min(df_btc.index[-1], df_oil.index[-1])
        return generer_graphique_double_axe(
            df_oil.loc[start:end, "close"],
            btc_close.loc[start:end],
            "Petrole WTI (USD)",
            "BTC (USD)",
            "BTC vs Petrole - Prix reels"
        )

    elif graph_type == "inflation":
        df_inf    = load_collection("inflation_usa")
        start     = max(df_btc.index[0], df_inf.index[0])
        end       = min(df_btc.index[-1], df_inf.index[-1])
        return generer_graphique_double_axe(
            df_inf.loc[start:end, "value"],
            btc_close.loc[start:end],
            "Inflation US CPI",
            "BTC (USD)",
            "BTC vs Inflation US - Prix reels"
        )

    else:  # sp500 par defaut
        df_sp     = load_collection("sp500_price_1d")
        start     = max(df_btc.index[0], df_sp.index[0])
        end       = min(df_btc.index[-1], df_sp.index[-1])
        return generer_graphique_double_axe(
            df_sp.loc[start:end, "close"],
            btc_close.loc[start:end],
            "SP500 (USD)",
            "BTC (USD)",
            "BTC vs SP500 - Prix reels"
        )


@app.route("/")
def index():
    # Type de graphique demande - sp500 par defaut
    graph_type = request.args.get("graph", "sp500")

    # Derniers prix depuis MongoDB
    btc = get_collection("btc_price_1d").find_one(sort=[("timestamp", -1)])
    sp  = get_collection("sp500_price_1d").find_one(sort=[("timestamp", -1)])
    oil = get_collection("oil_price_1d").find_one(sort=[("timestamp", -1)])
    inf = get_collection("inflation_usa").find_one(sort=[("timestamp", -1)])

    chart = get_chart(graph_type)

    return render_template_string(
        TEMPLATE,
        btc_price       = f"${btc['close']:,.0f}" if btc else "N/A",
        sp500_price     = f"${sp['close']:,.0f}"  if sp  else "N/A",
        oil_price       = f"${oil['close']:,.2f}" if oil else "N/A",
        inflation_value = f"{inf['value']:.1f}"   if inf else "N/A",
        chart           = chart,
        graph           = graph_type
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)