from sqlalchemy import create_engine
import os
from models.base import Base

# Informations de connexion à la base de données
db_user = "crm"  # Nom d'utilisateur pour la base de données
db_password = os.getenv("EPIC_DB_PASSWORD")  # Mot de passe stocké en variable d'environnement pour plus de sécurité
db_host = "localhost"  # Adresse du serveur de base de données
db_port = "5432"  # Port utilisé par PostgreSQL par défaut
db_name = "epic_crm"  # Nom de la base de données

# Construction de l'URL de connexion pour SQLAlchemy avec PostgreSQL et psycopg2
db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Création de l'objet engine SQLAlchemy qui gère la connexion à la base de données
engine = create_engine(db_url)

try:
    # Connexion à la base pour tester la connexion
    conn = engine.connect()

    # Création des tables en base définies dans les classes héritant de Base (ORM)
    Base.metadata.create_all(bind=engine)
except Exception as ex:
    # Affiche l'erreur si la connexion ou la création des tables échoue
    print(ex)
