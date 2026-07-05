# =============================================================================
# Indicateurs techniques - RSI et MACD sur BTC
# Calcul a partir des donnees MongoDB btc_price_1d
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

def load_btc():
    """
    Charge les prix BTC journaliers depuis MongoDB.

    Retourne :
        DataFrame pandas trie par date avec index timestamp
    """
    collection = get_collection("btc_price_1d")
    documents  = list(collection.find({}, {"_id": 0}).sort("timestamp", 1))
    df         = pd.DataFrame(documents)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
    df["close"] = df["close"].astype(float)
    return df


# =============================================================================
# RSI - Relative Strength Index
# =============================================================================

def calcul_rsi(serie, periode=14):
    """
    Calcule le RSI (Relative Strength Index).

    Interpretation :
        RSI > 70  : Zone de surachat  - signal potentiel SHORT
        RSI < 30  : Zone de survente  - signal potentiel LONG
        RSI 30-70 : Zone neutre

    Parametres :
        serie   (Series) : Serie de prix de cloture
        periode (int)    : Periode de calcul (defaut 14)

    Retourne :
        Series : Valeurs RSI entre 0 et 100
    """
    delta   = serie.diff()
    gain    = delta.where(delta > 0, 0.0)
    loss    = -delta.where(delta < 0, 0.0)

    avg_gain = gain.ewm(com=periode - 1, min_periods=periode).mean()
    avg_loss = loss.ewm(com=periode - 1, min_periods=periode).mean()

    rs  = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


# =============================================================================
# MACD - Moving Average Convergence Divergence
# =============================================================================

def calcul_macd(serie, rapide=12, lent=26, signal=9):
    """
    Calcule le MACD et sa ligne de signal.

    Interpretation :
        MACD croise Signal vers le haut  : signal potentiel LONG
        MACD croise Signal vers le bas   : signal potentiel SHORT
        Histogramme positif              : momentum haussier
        Histogramme negatif              : momentum baissier

    Parametres :
        serie   (Series) : Serie de prix de cloture
        rapide  (int)    : Periode EMA rapide (defaut 12)
        lent    (int)    : Periode EMA lente  (defaut 26)
        signal  (int)    : Periode EMA signal (defaut 9)

    Retourne :
        DataFrame avec colonnes : macd, signal, histogramme
    """
    ema_rapide   = serie.ewm(span=rapide, adjust=False).mean()
    ema_lent     = serie.ewm(span=lent,   adjust=False).mean()
    macd         = ema_rapide - ema_lent
    signal_line  = macd.ewm(span=signal,  adjust=False).mean()
    histogramme  = macd - signal_line

    return pd.DataFrame({
        "macd":        macd,
        "signal":      signal_line,
        "histogramme": histogramme
    })


# =============================================================================
# SIGNAL DE TRADING
# =============================================================================

def generer_signal(rsi_value, macd_value, signal_value):
    """
    Genere un signal de trading base sur RSI et MACD.

    Parametres :
        rsi_value    (float) : Valeur RSI actuelle
        macd_value   (float) : Valeur MACD actuelle
        signal_value (float) : Valeur Signal MACD actuelle

    Retourne :
        str : LONG, SHORT ou NEUTRE
    """
    signal_rsi  = ""
    signal_macd = ""

    # Signal RSI
    if rsi_value < 30:
        signal_rsi = "LONG"
    elif rsi_value > 70:
        signal_rsi = "SHORT"
    else:
        signal_rsi = "NEUTRE"

    # Signal MACD
    if macd_value > signal_value:
        signal_macd = "LONG"
    elif macd_value < signal_value:
        signal_macd = "SHORT"
    else:
        signal_macd = "NEUTRE"

    # Confirmation : les deux doivent etre d'accord
    if signal_rsi == signal_macd and signal_rsi != "NEUTRE":
        return signal_rsi
    else:
        return "NEUTRE"


# =============================================================================
# POINT D'ENTREE
# =============================================================================

def run():
    print("=" * 60)
    print("Indicateurs techniques BTC - RSI et MACD")
    print("=" * 60)

    # Chargement des donnees
    df = load_btc()
    print(f"Donnees chargees : {len(df)} bougies")
    print(f"Periode          : {df.index[0].date()} -> {df.index[-1].date()}")

    # Calcul RSI
    df["rsi"] = calcul_rsi(df["close"], periode=14)

    # Calcul MACD
    macd_df        = calcul_macd(df["close"])
    df["macd"]     = macd_df["macd"]
    df["signal"]   = macd_df["signal"]
    df["histo"]    = macd_df["histogramme"]

    # Derniere bougie
    derniere = df.iloc[-1]

    print("\n--- Derniers indicateurs BTC ---")
    print(f"Date        : {df.index[-1].date()}")
    print(f"Prix close  : ${derniere['close']:,.2f}")
    print(f"RSI (14)    : {derniere['rsi']:.2f}")
    print(f"MACD        : {derniere['macd']:.2f}")
    print(f"Signal MACD : {derniere['signal']:.2f}")
    print(f"Histogramme : {derniere['histo']:.2f}")

    # Signal de trading
    signal = generer_signal(
        derniere["rsi"],
        derniere["macd"],
        derniere["signal"]
    )

    print("\n" + "=" * 60)
    print(f"SIGNAL DE TRADING : {signal}")
    print("=" * 60)

    return df


if __name__ == "__main__":
    df = run()