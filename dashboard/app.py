# =============================================================================
# Dashboard Flask - BTC + SP500 + Petrole
# =============================================================================

import sys
import os
import base64

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
        body       { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        h1         { text-align: center; color: #F7931A; margin-bottom: 30px; }
        .stats     { display: flex; justify-content: center; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }
        .card      { background: #16213e; padding: 20px 30px; border-radius: 8px; text-align: center; }
        .val       { font-size: 26px; font-weight: bold; color: #F7931A; }
        .lbl       { font-size: 12px; color: #aaa; margin-top: 6px; }
        .chart     { text-align: center; }
        img        { max-width: 100%; border-radius: 8px; }
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

    <div class="chart">
        <img src="data:image/png;base64,{{ chart }}" alt="Graphique">
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    btc = get_collection("btc_price_1d").find_one(sort=[("timestamp", -1)])
    sp  = get_collection("sp500_price_1d").find_one(sort=[("timestamp", -1)])
    oil = get_collection("oil_price_1d").find_one(sort=[("timestamp", -1)])

    chemin = os.path.join(ROOT, "exports", "btc_sp500_oil.png")
    with open(chemin, "rb") as f:
        chart_b64 = base64.b64encode(f.read()).decode("utf-8")

    return render_template_string(
        TEMPLATE,
        btc_price   = f"${btc['close']:,.0f}" if btc  else "N/A",
        sp500_price = f"${sp['close']:,.0f}"  if sp   else "N/A",
        oil_price   = f"${oil['close']:,.2f}" if oil  else "N/A",
        chart       = chart_b64
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)