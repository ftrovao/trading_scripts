# =============================================================================
# MongoDB Atlas - Client de connexion
# =============================================================================

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_collection(collection_name, db_name="trading_db"):
    """
    Retourne une collection MongoDB Atlas.

    Parametres :
        collection_name (str) : Nom de la collection cible
        db_name         (str) : Nom de la base de donnees (defaut: trading_db)

    Retourne :
        Collection MongoDB prete a l'emploi
    """
    uri    = os.getenv("MONGO_URI")
    client = MongoClient(uri)
    db     = client[db_name]
    return db[collection_name]


def test_connection():
    """
    Teste la connexion a MongoDB Atlas.
    Affiche la liste des collections existantes.
    """
    try:
        uri    = os.getenv("MONGO_URI")
        client = MongoClient(uri)
        client.admin.command("ping")
        collections = client["trading_db"].list_collection_names()
        print(f"Connexion ok : {collections}")
    except Exception as e:
        print(f"Erreur de connexion : {e}")


if __name__ == "__main__":
    test_connection()