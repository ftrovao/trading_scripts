# =============================================================================
# Scheduler - Mise a jour automatique des donnees
# BTC toutes les 4 heures
# SP500, Petrole, Or, Argent, Inflation, Chomage toutes les 24 heures
# =============================================================================

import sys
import os
import time
import schedule
from datetime import datetime

ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

# =============================================================================
# IMPORTS DES COLLECTEURS
# =============================================================================

from collectors.macro.btc_price        import run as run_btc
from collectors.macro.sp500_price      import fetch_and_save as run_sp500
from collectors.macro.oil_price        import fetch_and_save as run_oil
from collectors.macro.gold_silver      import run as run_gold_silver
from collectors.macro.inflation_usa    import run as run_inflation
from collectors.macro.unemployment_usa import run as run_unemployment


# =============================================================================
# FONCTIONS DE MISE A JOUR
# =============================================================================

def log(message):
    """
    Affiche un message avec horodatage.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {message}")


def update_btc():
    """
    Mise a jour du prix BTC - toutes les 4 heures.
    """
    log("Mise a jour BTC en cours...")
    try:
        run_btc()
        log("BTC mis a jour avec succes")
    except Exception as e:
        log(f"Erreur BTC : {e}")


def update_macro():
    """
    Mise a jour des donnees macro - toutes les 24 heures.
    SP500, Petrole, Or, Argent, Inflation, Chomage
    """
    log("Mise a jour macro en cours...")

    try:
        run_sp500()
        log("SP500 mis a jour")
    except Exception as e:
        log(f"Erreur SP500 : {e}")

    try:
        run_oil()
        log("Petrole mis a jour")
    except Exception as e:
        log(f"Erreur Petrole : {e}")

    try:
        run_gold_silver()
        log("Or et Argent mis a jour")
    except Exception as e:
        log(f"Erreur Or/Argent : {e}")

    try:
        run_inflation()
        log("Inflation mise a jour")
    except Exception as e:
        log(f"Erreur Inflation : {e}")

    try:
        run_unemployment()
        log("Chomage mis a jour")
    except Exception as e:
        log(f"Erreur Chomage : {e}")

    log("Mise a jour macro terminee")


# =============================================================================
# PLANIFICATION
# =============================================================================

def run():
    log("=" * 60)
    log("Scheduler demarre")
    log("BTC   : mise a jour toutes les 4 heures")
    log("Macro : mise a jour tous les jours a 06h00")
    log("=" * 60)

    # Mise a jour immediate au demarrage
    log("Premiere mise a jour au demarrage...")
    update_btc()
    update_macro()

    # Planification BTC toutes les 4 heures
    schedule.every(4).hours.do(update_btc)

    # Planification macro tous les jours a 6h du matin
    schedule.every().day.at("06:00").do(update_macro)

    log("Scheduler actif - prochaines mises a jour planifiees")
    log("Appuie sur Ctrl+C pour arreter")

    # Boucle principale
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    run()