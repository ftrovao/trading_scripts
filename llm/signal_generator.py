# =============================================================================
# Analyse IA - Claude API
# Analyse les indicateurs techniques et repond aux questions
# =============================================================================

import sys
import os
import anthropic

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# =============================================================================
# ANALYSE AUTOMATIQUE
# =============================================================================

def analyser_marche(btc_price, rsi, macd, signal_macd, histogramme, signal, sp500, oil, inflation):
    """
    Envoie les indicateurs a Claude et retourne une analyse en francais.

    Parametres :
        btc_price   (float) : Prix actuel du BTC en USD
        rsi         (float) : Valeur RSI 14 periodes
        macd        (float) : Valeur MACD actuelle
        signal_macd (float) : Valeur de la ligne signal MACD
        histogramme (float) : Valeur de l histogramme MACD
        signal      (str)   : Signal genere LONG SHORT ou NEUTRE
        sp500       (float) : Dernier prix du SP500
        oil         (float) : Dernier prix du petrole WTI
        inflation   (float) : Dernier indice CPI

    Retourne :
        str : Analyse en francais sans formatage Markdown
    """
    prompt = f"""
Tu es un analyste crypto professionnel. Analyse ces donnees de marche et fournis
une analyse concise en francais de 3 a 4 phrases maximum.

=== DONNEES ACTUELLES ===
BTC Prix      : ${btc_price:,.0f}
RSI (14)      : {rsi:.1f}
MACD          : {macd:.2f}
Signal MACD   : {signal_macd:.2f}
Histogramme   : {histogramme:.2f}
Signal genere : {signal}
SP500         : ${sp500:,.0f}
Petrole WTI   : ${oil:.2f}
Inflation CPI : {inflation:.1f}

=== INSTRUCTIONS ===
- Explique ce que les indicateurs signifient
- Identifie les points cles a surveiller
- Reste factuel et professionnel
- Maximum 4 phrases en francais
- Reponds en texte simple sans Markdown
- Sans asterisques, sans hashtags, sans symboles speciaux
"""

    message = client.messages.create(
        model      = "claude-haiku-4-5-20251001",
        max_tokens = 300,
        messages   = [{"role": "user", "content": prompt}]
    )

    return message.content[0].text


# =============================================================================
# REPONSE AUX QUESTIONS
# =============================================================================

def repondre_question(question, btc_price, rsi, macd, signal, sp500, oil, inflation):
    """
    Repond a une question de l utilisateur sur le marche.

    Parametres :
        question  (str)   : Question posee par l utilisateur
        btc_price (float) : Prix actuel du BTC en USD
        rsi       (float) : Valeur RSI actuelle
        macd      (float) : Valeur MACD actuelle
        signal    (str)   : Signal genere LONG SHORT ou NEUTRE
        sp500     (float) : Dernier prix du SP500
        oil       (float) : Dernier prix du petrole WTI
        inflation (float) : Dernier indice CPI

    Retourne :
        str : Reponse en francais sans formatage Markdown
    """
    prompt = f"""
Tu es un assistant specialise en analyse crypto et macro-economie.
Reponds en francais de facon claire et concise.

=== DONNEES ACTUELLES ===
BTC Prix      : ${btc_price:,.0f}
RSI (14)      : {rsi:.1f}
MACD          : {macd:.2f}
Signal genere : {signal}
SP500         : ${sp500:,.0f}
Petrole WTI   : ${oil:.2f}
Inflation CPI : {inflation:.1f}

=== INSTRUCTIONS ===
- Reponds directement a la question
- Base toi sur les donnees fournies
- Maximum 4 phrases en francais
- Reponds en texte simple sans Markdown
- Sans asterisques, sans hashtags, sans symboles speciaux

Question : {question}
"""

    message = client.messages.create(
        model      = "claude-haiku-4-5-20251001",
        max_tokens = 300,
        messages   = [{"role": "user", "content": prompt}]
    )

    return message.content[0].text