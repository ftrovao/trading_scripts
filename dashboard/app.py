# =============================================================================
# Dashboard Flask - BTC + SP500 + Petrole + Inflation + Indicateurs + IA
# Graphiques generes en memoire - pas de fichier PNG
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

from flask import Flask, render_template_string, request, jsonify
from database.mongo_client import get_collection
from analysis.indicators  import calcul_rsi, calcul_macd, generer_signal, load_btc
from analysis.statistics  import generer_statistiques
from llm.signal_generator import analyser_marche, repondre_question

app = Flask(__name__)

# =============================================================================
# TEMPLATE PRINCIPAL
# =============================================================================

TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Trading Dashboard</title>
    <style>
        body           { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        h1             { text-align: center; color: #F7931A; margin-bottom: 30px; }
        .stats         { display: flex; justify-content: center; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
        .card          { background: #16213e; padding: 16px 24px; border-radius: 8px; text-align: center; }
        .val           { font-size: 22px; font-weight: bold; color: #F7931A; }
        .lbl           { font-size: 11px; color: #aaa; margin-top: 4px; }
        .signal        { text-align: center; margin-bottom: 24px; }
        .signal-box    { display: inline-block; padding: 12px 40px; border-radius: 8px;
                         font-size: 22px; font-weight: bold; letter-spacing: 2px; }
        .LONG          { background: #1a4a1a; color: #2ecc71; border: 1px solid #2ecc71; }
        .SHORT         { background: #4a1a1a; color: #e74c3c; border: 1px solid #e74c3c; }
        .NEUTRE        { background: #2a2a1a; color: #f39c12; border: 1px solid #f39c12; }
        .nav           { display: flex; justify-content: center; gap: 8px; margin-bottom: 24px; flex-wrap: wrap; }
        .nav-btn       { background: #0f1a2e; color: #eee; border: 1px solid #444;
                         padding: 10px 20px; border-radius: 6px; cursor: pointer;
                         font-size: 14px; text-decoration: none; }
        .nav-btn:hover  { background: #1f2a4a; }
        .nav-btn.active { background: #F7931A; color: #1a1a2e; font-weight: bold; border-color: #F7931A; }
        .buttons       { display: flex; justify-content: center; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
        .btn           { background: #16213e; color: #eee; border: 1px solid #333;
                         padding: 10px 24px; border-radius: 6px; cursor: pointer;
                         font-size: 14px; text-decoration: none; }
        .btn:hover     { background: #1f2a4a; }
        .btn.active    { background: #F7931A; color: #1a1a2e; font-weight: bold; border-color: #F7931A; }
        img            { max-width: 100%; border-radius: 8px; display: block; margin: 0 auto 30px auto; }
        .analyse       { background: #16213e; padding: 20px; border-radius: 8px; margin: 20px 0; line-height: 1.7; }
        .analyse h3    { color: #F7931A; margin: 0 0 10px 0; font-size: 14px; text-transform: uppercase; }
        .chat          { background: #16213e; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .chat h3       { color: #F7931A; margin: 0 0 12px 0; font-size: 14px; text-transform: uppercase; }
        .chat-messages { min-height: 80px; max-height: 300px; overflow-y: auto; margin-bottom: 12px; }
        .msg-user      { background: #1f2a4a; padding: 8px 12px; border-radius: 6px; margin: 6px 0; font-size: 13px; }
        .msg-assistant { background: #0f1a2e; padding: 8px 12px; border-radius: 6px;
                         margin: 6px 0; font-size: 13px; border-left: 3px solid #F7931A; line-height: 1.6; }
        .chat-input    { display: flex; gap: 10px; }
        .chat-input input  { flex: 1; padding: 10px; border-radius: 6px; border: 1px solid #333;
                             background: #0f1a2e; color: #eee; font-size: 14px; }
        .chat-input button { padding: 10px 20px; background: #F7931A; color: #1a1a2e;
                             border: none; border-radius: 6px; cursor: pointer;
                             font-weight: bold; font-size: 14px; }
        .chat-input button:hover { background: #e08010; }
        .loading       { color: #aaa; font-style: italic; font-size: 13px; }
    </style>
</head>
<body>
    <h1>Trading Dashboard</h1>

    <!-- Prix actuels -->
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
            <div class="lbl">Petrole WTI</div>
        </div>
        <div class="card">
            <div class="val">{{ rsi_value }}</div>
            <div class="lbl">RSI (14)</div>
        </div>
        <div class="card">
            <div class="val">{{ inflation_value }}</div>
            <div class="lbl">Inflation CPI</div>
        </div>
    </div>

    <!-- Signal de trading -->
    <div class="signal">
        <div class="signal-box {{ signal }}">
            SIGNAL : {{ signal }}
        </div>
    </div>

    <!-- Navigation principale -->
    <div class="nav">
        <a href="/"             class="nav-btn {{ 'active' if page == 'dashboard' else '' }}">Dashboard</a>
        <a href="/statistiques" class="nav-btn {{ 'active' if page == 'statistiques' else '' }}">Statistiques</a>
    </div>

    <!-- Boutons graphiques et contenu dashboard -->
    {% if page == 'dashboard' %}
    <div class="buttons">
        <a href="/?graph=sp500"     class="btn {{ 'active' if graph == 'sp500' else '' }}">BTC x SP500</a>
        <a href="/?graph=oil"       class="btn {{ 'active' if graph == 'oil' else '' }}">BTC x Petrole</a>
        <a href="/?graph=inflation" class="btn {{ 'active' if graph == 'inflation' else '' }}">BTC x Inflation</a>
        <a href="/?graph=rsi"       class="btn {{ 'active' if graph == 'rsi' else '' }}">RSI</a>
        <a href="/?graph=macd"      class="btn {{ 'active' if graph == 'macd' else '' }}">MACD</a>
    </div>

    <!-- Graphique -->
    <img src="data:image/png;base64,{{ chart }}" alt="Graphique">

    <!-- Analyse IA automatique -->
    <div class="analyse">
        <h3>Analyse IA - Claude</h3>
        <p>{{ analyse_ia }}</p>
    </div>

    <!-- Chat avec l'IA -->
    <div class="chat">
        <h3>Posez votre question a l'IA</h3>
        <div class="chat-messages" id="messages"></div>
        <div class="chat-input">
            <input type="text" id="question"
                   placeholder="Ex: Quel est le signal actuel pour le BTC ?">
            <button id="btn-envoyer">Envoyer</button>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', function() {

        const input    = document.getElementById('question');
        const messages = document.getElementById('messages');
        const btnEnv   = document.getElementById('btn-envoyer');

        async function envoyerQuestion() {
            const question = input.value.trim();
            if (!question) return;

            // Afficher la question
            messages.innerHTML += `<div class="msg-user"><strong>Vous :</strong> ${question}</div>`;
            input.value = '';

            // Indicateur de chargement
            const loadingId = 'loading-' + Date.now();
            messages.innerHTML += `<div class="msg-assistant loading" id="${loadingId}">IA en train de reflechir...</div>`;
            messages.scrollTop = messages.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method:  'POST',
                    headers: {'Content-Type': 'application/json'},
                    body:    JSON.stringify({question: question})
                });

                const data = await response.json();
                document.getElementById(loadingId).remove();
                messages.innerHTML += `<div class="msg-assistant"><strong>IA :</strong> ${data.reponse}</div>`;
                messages.scrollTop  = messages.scrollHeight;

            } catch (error) {
                document.getElementById(loadingId).remove();
                messages.innerHTML += `<div class="msg-assistant">Erreur de connexion a l'IA.</div>`;
            }
        }

        btnEnv.addEventListener('click', envoyerQuestion);

        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') envoyerQuestion();
        });

    });
    </script>

    {% endif %}

</body>
</html>
"""

# =============================================================================
# TEMPLATE STATISTIQUES
# =============================================================================

TEMPLATE_STATS = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Trading Dashboard - Statistiques</title>
    <style>
        body        { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        h1          { text-align: center; color: #F7931A; margin-bottom: 30px; }
        .stats      { display: flex; justify-content: center; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
        .card       { background: #16213e; padding: 16px 24px; border-radius: 8px; text-align: center; }
        .val        { font-size: 22px; font-weight: bold; color: #F7931A; }
        .lbl        { font-size: 11px; color: #aaa; margin-top: 4px; }
        .nav        { display: flex; justify-content: center; gap: 8px; margin-bottom: 24px; flex-wrap: wrap; }
        .nav-btn    { background: #0f1a2e; color: #eee; border: 1px solid #444;
                      padding: 10px 20px; border-radius: 6px; cursor: pointer;
                      font-size: 14px; text-decoration: none; }
        .nav-btn:hover  { background: #1f2a4a; }
        .nav-btn.active { background: #F7931A; color: #1a1a2e; font-weight: bold; border-color: #F7931A; }
        .section    { background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .section h2 { color: #F7931A; margin: 0 0 16px 0; font-size: 14px; text-transform: uppercase; }
        table       { width: 100%; border-collapse: collapse; }
        th          { text-align: left; color: #aaa; font-size: 12px; padding: 8px 12px;
                      border-bottom: 1px solid #333; }
        td          { padding: 10px 12px; font-size: 14px; border-bottom: 1px solid #222; }
        td.pos      { color: #2ecc71; font-weight: bold; }
        td.neg      { color: #e74c3c; font-weight: bold; }
        td.neu      { color: #F7931A; font-weight: bold; }
        .corr-bar   { height: 8px; border-radius: 4px; background: #F7931A; display: inline-block; margin-left: 10px; }
        img         { max-width: 100%; border-radius: 8px; display: block; margin: 0 auto; }
        .periode    { text-align: center; color: #aaa; font-size: 12px; margin-bottom: 20px; }
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
            <div class="lbl">Petrole WTI</div>
        </div>
        <div class="card">
            <div class="val">{{ rsi_value }}</div>
            <div class="lbl">RSI (14)</div>
        </div>
        <div class="card">
            <div class="val">{{ inflation_value }}</div>
            <div class="lbl">Inflation CPI</div>
        </div>
    </div>

    <div class="nav">
        <a href="/"             class="nav-btn">Dashboard</a>
        <a href="/statistiques" class="nav-btn active">Statistiques</a>
    </div>

    <p class="periode">Periode analysee : {{ s.debut }} -> {{ s.fin }}</p>

    <div class="section">
        <h2>Rendements totaux</h2>
        <table>
            <tr>
                <th>Actif</th>
                <th>Prix actuel</th>
                <th>Rendement total</th>
                <th>Rendement annuel moyen</th>
            </tr>
            <tr>
                <td>Bitcoin (BTC)</td>
                <td>${{ "{:,.0f}".format(s.btc_prix) }}</td>
                <td class="pos">+{{ s.btc_rendement_total }}%</td>
                <td class="pos">+{{ s.btc_rendement_annuel }}%/an</td>
            </tr>
            <tr>
                <td>SP500</td>
                <td>${{ "{:,.0f}".format(s.sp_prix) }}</td>
                <td class="pos">+{{ s.sp_rendement_total }}%</td>
                <td class="pos">+{{ s.sp_rendement_annuel }}%/an</td>
            </tr>
            <tr>
                <td>Or (Gold)</td>
                <td>${{ "{:,.0f}".format(s.gold_prix) }}</td>
                <td class="pos">+{{ s.gold_rendement_total }}%</td>
                <td class="pos">+{{ s.gold_rendement_annuel }}%/an</td>
            </tr>
            <tr>
                <td>Petrole WTI</td>
                <td>${{ "{:.2f}".format(s.oil_prix) }}</td>
                <td class="pos">+{{ s.oil_rendement_total }}%</td>
                <td class="pos">+{{ s.oil_rendement_annuel }}%/an</td>
            </tr>
        </table>
    </div>

    <div class="section">
        <h2>Risque et volatilite</h2>
        <table>
            <tr>
                <th>Actif</th>
                <th>Volatilite annualisee</th>
                <th>Max Drawdown</th>
            </tr>
            <tr>
                <td>Bitcoin (BTC)</td>
                <td class="neu">{{ s.btc_volatilite }}%</td>
                <td class="neg">{{ s.btc_drawdown }}%</td>
            </tr>
            <tr>
                <td>SP500</td>
                <td class="neu">{{ s.sp_volatilite }}%</td>
                <td class="neg">{{ s.sp_drawdown }}%</td>
            </tr>
            <tr>
                <td>Or (Gold)</td>
                <td class="neu">{{ s.gold_volatilite }}%</td>
                <td class="neg">{{ s.gold_drawdown }}%</td>
            </tr>
            <tr>
                <td>Petrole WTI</td>
                <td class="neu">{{ s.oil_volatilite }}%</td>
                <td class="neg">{{ s.oil_drawdown }}%</td>
            </tr>
        </table>
    </div>

    <div class="section">
        <h2>Correlations avec BTC</h2>
        <table>
            <tr>
                <th>Paire</th>
                <th>Coefficient</th>
                <th>Interpretation</th>
                <th>Force</th>
            </tr>
            <tr>
                <td>BTC / SP500</td>
                <td class="neu">{{ s.corr_btc_sp }}</td>
                <td>Tres forte correlation — BTC suit les marches actions</td>
                <td><span class="corr-bar" style="width: {{ (s.corr_btc_sp * 200)|int }}px"></span></td>
            </tr>
            <tr>
                <td>BTC / Or</td>
                <td class="neu">{{ s.corr_btc_gold }}</td>
                <td>Correlation moderee — BTC parfois valeur refuge</td>
                <td><span class="corr-bar" style="width: {{ (s.corr_btc_gold * 200)|int }}px"></span></td>
            </tr>
            <tr>
                <td>BTC / Petrole</td>
                <td class="neu">{{ s.corr_btc_oil }}</td>
                <td>Faible correlation — actifs presque independants</td>
                <td><span class="corr-bar" style="width: {{ (s.corr_btc_oil * 200)|int }}px"></span></td>
            </tr>
        </table>
    </div>

    <div class="section">
        <h2>Performance normalisee base 100</h2>
        <img src="data:image/png;base64,{{ chart }}" alt="Performance normalisee">
    </div>

</body>
</html>
"""

# =============================================================================
# CHARGEMENT DES COLLECTIONS
# =============================================================================

def load_collection(collection_name):
    collection = get_collection(collection_name)
    documents  = list(collection.find({}, {"_id": 0}).sort("timestamp", 1))
    df         = pd.DataFrame(documents)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
    return df


# =============================================================================
# GENERATION DES GRAPHIQUES EN MEMOIRE
# =============================================================================

def graphique_double_axe(serie_gauche, serie_droite, nom_gauche, nom_droite, titre):
    fig, ax1 = plt.subplots(figsize=(14, 6))
    fig.suptitle(titre, fontsize=15, fontweight="bold")

    color_g = "#1f77b4"
    ax1.set_ylabel(nom_gauche, color=color_g, fontsize=11)
    ax1.plot(serie_gauche.index, serie_gauche.values, color=color_g, linewidth=1.5, label=nom_gauche)
    ax1.tick_params(axis="y", labelcolor=color_g)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    ax1.grid(True, alpha=0.2)

    color_d = "#F7931A"
    ax2 = ax1.twinx()
    ax2.set_ylabel(nom_droite, color=color_d, fontsize=11)
    ax2.plot(serie_droite.index, serie_droite.values, color=color_d, linewidth=1.5, label=nom_droite)
    ax2.tick_params(axis="y", labelcolor=color_d)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.tight_layout()
    return figure_to_base64(fig)


def graphique_rsi(df):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    fig.suptitle("BTC - Prix et RSI (14)", fontsize=15, fontweight="bold")

    ax1.plot(df.index, df["close"], color="#F7931A", linewidth=1.5)
    ax1.set_ylabel("Prix BTC (USD)", fontsize=11)
    ax1.grid(True, alpha=0.2)

    ax2.plot(df.index, df["rsi"], color="#9b59b6", linewidth=1.5, label="RSI 14")
    ax2.axhline(y=70, color="#e74c3c", linestyle="--", linewidth=1, label="Surachat (70)")
    ax2.axhline(y=30, color="#2ecc71", linestyle="--", linewidth=1, label="Survente (30)")
    ax2.axhline(y=50, color="#aaa",    linestyle="--", linewidth=0.5)
    ax2.fill_between(df.index, df["rsi"], 70, where=(df["rsi"] >= 70), alpha=0.2, color="#e74c3c")
    ax2.fill_between(df.index, df["rsi"], 30, where=(df["rsi"] <= 30), alpha=0.2, color="#2ecc71")
    ax2.set_ylabel("RSI", fontsize=11)
    ax2.set_ylim(0, 100)
    ax2.legend(loc="upper left")
    ax2.grid(True, alpha=0.2)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

    plt.tight_layout()
    return figure_to_base64(fig)


def graphique_macd(df):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    fig.suptitle("BTC - Prix et MACD (12/26/9)", fontsize=15, fontweight="bold")

    ax1.plot(df.index, df["close"], color="#F7931A", linewidth=1.5)
    ax1.set_ylabel("Prix BTC (USD)", fontsize=11)
    ax1.grid(True, alpha=0.2)

    ax2.plot(df.index, df["macd"],   color="#1f77b4", linewidth=1.5, label="MACD")
    ax2.plot(df.index, df["signal"], color="#e74c3c", linewidth=1.5, label="Signal")
    ax2.bar(df.index, df["histo"],
            color=["#2ecc71" if v >= 0 else "#e74c3c" for v in df["histo"]],
            alpha=0.5, label="Histogramme")
    ax2.axhline(y=0, color="#aaa", linestyle="--", linewidth=0.5)
    ax2.set_ylabel("MACD", fontsize=11)
    ax2.legend(loc="upper left")
    ax2.grid(True, alpha=0.2)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

    plt.tight_layout()
    return figure_to_base64(fig)


def graphique_performance_normalisee():
    df_btc  = load_collection("btc_price_1d")
    df_sp   = load_collection("sp500_price_1d")
    df_oil  = load_collection("oil_price_1d")
    df_gold = load_collection("gold_price_1d")

    start = max(df_btc.index[0], df_sp.index[0], df_oil.index[0], df_gold.index[0])
    end   = min(df_btc.index[-1], df_sp.index[-1], df_oil.index[-1], df_gold.index[-1])

    def norm(serie):
        s = serie.loc[start:end]
        return (s / s.iloc[0]) * 100

    btc_n  = norm(df_btc["close"])
    sp_n   = norm(df_sp["close"])
    oil_n  = norm(df_oil["close"])
    gold_n = norm(df_gold["close"])

    fig, ax = plt.subplots(figsize=(14, 6))
    fig.suptitle("Performance normalisee base 100", fontsize=15, fontweight="bold")

    ax.plot(btc_n.index,  btc_n.values,  label="BTC",     color="#F7931A", linewidth=2)
    ax.plot(sp_n.index,   sp_n.values,   label="SP500",   color="#1f77b4", linewidth=1.5)
    ax.plot(gold_n.index, gold_n.values, label="Or",      color="#FFD700", linewidth=1.5)
    ax.plot(oil_n.index,  oil_n.values,  label="Petrole", color="#2ca02c", linewidth=1.5)

    ax.axhline(y=100, color="#aaa", linestyle="--", linewidth=0.5)
    ax.set_ylabel("Indice base 100")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.2)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    plt.tight_layout()
    return figure_to_base64(fig)


def figure_to_base64(fig):
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close()
    return image_base64


# =============================================================================
# SELECTION DU GRAPHIQUE
# =============================================================================

def get_chart(graph_type, df_btc):
    btc_close = df_btc["close"]

    if graph_type == "oil":
        df_oil = load_collection("oil_price_1d")
        start  = max(df_btc.index[0], df_oil.index[0])
        end    = min(df_btc.index[-1], df_oil.index[-1])
        return graphique_double_axe(
            df_oil.loc[start:end, "close"],
            btc_close.loc[start:end],
            "Petrole WTI (USD)", "BTC (USD)",
            "BTC vs Petrole - Prix reels"
        )

    elif graph_type == "inflation":
        df_inf = load_collection("inflation_usa")
        start  = max(df_btc.index[0], df_inf.index[0])
        end    = min(df_btc.index[-1], df_inf.index[-1])
        return graphique_double_axe(
            df_inf.loc[start:end, "value"],
            btc_close.loc[start:end],
            "Inflation US CPI", "BTC (USD)",
            "BTC vs Inflation USA"
        )

    elif graph_type == "rsi":
        return graphique_rsi(df_btc)

    elif graph_type == "macd":
        return graphique_macd(df_btc)

    else:
        df_sp = load_collection("sp500_price_1d")
        start = max(df_btc.index[0], df_sp.index[0])
        end   = min(df_btc.index[-1], df_sp.index[-1])
        return graphique_double_axe(
            df_sp.loc[start:end, "close"],
            btc_close.loc[start:end],
            "SP500 (USD)", "BTC (USD)",
            "BTC vs SP500 - Prix reels"
        )


# =============================================================================
# FONCTION COMMUNE - CHARGER INDICATEURS
# =============================================================================

def charger_indicateurs():
    df_btc           = load_btc()
    df_btc["rsi"]    = calcul_rsi(df_btc["close"])
    macd_df          = calcul_macd(df_btc["close"])
    df_btc["macd"]   = macd_df["macd"]
    df_btc["signal"] = macd_df["signal"]
    df_btc["histo"]  = macd_df["histogramme"]

    derniere = df_btc.iloc[-1]
    signal   = generer_signal(derniere["rsi"], derniere["macd"], derniere["signal"])

    btc = get_collection("btc_price_1d").find_one(sort=[("timestamp", -1)])
    sp  = get_collection("sp500_price_1d").find_one(sort=[("timestamp", -1)])
    oil = get_collection("oil_price_1d").find_one(sort=[("timestamp", -1)])
    inf = get_collection("inflation_usa").find_one(sort=[("timestamp", -1)])

    return df_btc, derniere, signal, btc, sp, oil, inf


def contexte_commun(derniere, signal, btc, sp, oil, inf):
    return {
        "btc_price":       f"${btc['close']:,.0f}" if btc else "N/A",
        "sp500_price":     f"${sp['close']:,.0f}"  if sp  else "N/A",
        "oil_price":       f"${oil['close']:,.2f}" if oil else "N/A",
        "rsi_value":       f"{derniere['rsi']:.1f}",
        "inflation_value": f"{inf['value']:.1f}"   if inf else "N/A",
        "signal":          signal,
    }


# =============================================================================
# ROUTES FLASK
# =============================================================================

@app.route("/")
def index():
    graph_type = request.args.get("graph", "sp500")

    df_btc, derniere, signal, btc, sp, oil, inf = charger_indicateurs()

    analyse_ia = analyser_marche(
        btc_price   = btc["close"],
        rsi         = derniere["rsi"],
        macd        = derniere["macd"],
        signal_macd = derniere["signal"],
        histogramme = derniere["histo"],
        signal      = signal,
        sp500       = sp["close"],
        oil         = oil["close"],
        inflation   = inf["value"]
    )

    chart = get_chart(graph_type, df_btc)
    ctx   = contexte_commun(derniere, signal, btc, sp, oil, inf)

    return render_template_string(
        TEMPLATE,
        **ctx,
        analyse_ia = analyse_ia,
        chart      = chart,
        graph      = graph_type,
        page       = "dashboard"
    )


@app.route("/statistiques")
def statistiques():
    df_btc, derniere, signal, btc, sp, oil, inf = charger_indicateurs()

    stats = generer_statistiques()

    from analysis.statistics import load_serie, calcul_rendement_annuel
    stats["btc_rendement_annuel"]  = round(calcul_rendement_annuel(load_serie("btc_price_1d")),  1)
    stats["sp_rendement_annuel"]   = round(calcul_rendement_annuel(load_serie("sp500_price_1d")), 1)
    stats["gold_rendement_annuel"] = round(calcul_rendement_annuel(load_serie("gold_price_1d")), 1)
    stats["oil_rendement_annuel"]  = round(calcul_rendement_annuel(load_serie("oil_price_1d")),  1)

    class Stats:
        pass

    s = Stats()
    for k, v in stats.items():
        setattr(s, k, v)

    chart = graphique_performance_normalisee()
    ctx   = contexte_commun(derniere, signal, btc, sp, oil, inf)

    return render_template_string(
        TEMPLATE_STATS,
        **ctx,
        s     = s,
        chart = chart,
        page  = "statistiques"
    )


@app.route("/chat", methods=["POST"])
def chat():
    data     = request.get_json()
    question = data.get("question", "")

    df_btc, derniere, signal, btc, sp, oil, inf = charger_indicateurs()

    reponse = repondre_question(
        question  = question,
        btc_price = btc["close"],
        rsi       = derniere["rsi"],
        macd      = derniere["macd"],
        signal    = signal,
        sp500     = sp["close"],
        oil       = oil["close"],
        inflation = inf["value"]
    )

    return jsonify({"reponse": reponse})


if __name__ == "__main__":
    app.run(debug=True, port=5000)