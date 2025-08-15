import bcrypt
import getpass
import jwt
import os
from sqlalchemy.orm import sessionmaker, joinedload
from models.user import User
from utils.connection import engine
from datetime import datetime, timedelta


# Clé secrète pour le JWT (à stocker idéalement en variable d'environnement !)
SECRET_KEY = os.getenv("EPIC_SECRET_KEY", "change_me")
ALGORITHM = "HS256"
TOKEN_FILE = "../.epic_token"

# Création d'une session SQLAlchemy
Session = sessionmaker(bind=engine)
session = Session()


def populate_departments():
    """
    Initialise la table Department avec les départements 'commercial', 'support' et 'gestion'
    si ceux-ci n'existent pas déjà.
    """
    # Import local pour éviter les problèmes d'import circulaire
    from models.department import Department

    Session = sessionmaker(bind=engine)
    with Session() as session:
        # Ajout des départements par défaut
        for name in ["commercial", "support", "gestion"]:
            if not session.query(Department).filter_by(name=name).first():
                session.add(Department(name=name))
        session.commit()


# Initialisation des départements si nécessaire
populate_departments()

session.commit()
session.close()


def hash_password(password: str) -> str:
    """
    Hash un mot de passe en utilisant bcrypt.

    Args:
        password (str): Mot de passe en clair.

    Returns:
        str: Mot de passe hashé.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, hashed: str) -> bool:
    """
    Vérifie qu'un mot de passe correspond au hash stocké.

    Args:
        password (str): Mot de passe en clair à vérifier.
        hashed (str): Mot de passe hashé stocké.

    Returns:
        bool: True si le mot de passe correspond, False sinon.
    """
    return bcrypt.checkpw(password.encode(), hashed.encode())


def login():
    """
    Gère la procédure d'authentification de l'utilisateur.
    Demande l'email et le mot de passe, vérifie les identifiants,
    puis génère et stocke un token JWT en cas de succès.
    """
    email = input("Email : ")
    password = getpass.getpass("Mot de passe : ")

    user = session.query(User).filter_by(email=email).first()
    if not user:
        print("Utilisateur introuvable.")
        return

    if not check_password(password, user.password):
        print("Mot de passe incorrect.")
        return

    # Création du payload du token JWT avec expiration
    payload = {
        "user_id": user.id,
        "exp": datetime.utcnow() + timedelta(hours=2),
        "department": get_user_role(user),
        "email": user.email,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    # Écriture du token dans un fichier local pour la session
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

    print("Authentification réussie.")


def get_current_user():
    """
    Récupère l'utilisateur courant en décodant le token JWT stocké localement.

    Returns:
        User: Objet utilisateur correspondant au token.

    Raises:
        Exception: Si aucun token n'est trouvé, token invalide ou expiré,
                   ou si l'utilisateur n'existe pas en base.
    """
    if not os.path.exists(TOKEN_FILE):
        raise Exception("Vous n'êtes pas connecté.")

    with open(TOKEN_FILE, "r") as f:
        token = f.read().strip()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise Exception("Session expirée. Veuillez vous reconnecter.")
    except jwt.InvalidTokenError:
        raise Exception("Jeton invalide. Veuillez vous reconnecter.")

    user_id = payload.get("user_id")
    if user_id is None:
        raise Exception("Jeton invalide : user_id manquant.")

    session = Session()
    try:
        # Chargement de l'utilisateur avec son département en une seule requête
        user = session.query(User).options(joinedload(User.department)).filter_by(id=user_id).first()
        if not user:
            raise Exception("Utilisateur introuvable pour l'ID du token.")
        return user
    finally:
        session.close()


def get_user_role(user):
    """
    Récupère le rôle (nom du département) d'un utilisateur donné.

    Args:
        user (User): Objet utilisateur.

    Returns:
        str or None: Nom du département de l'utilisateur, ou None si absent.
    """
    if user and user.department:
        return user.department.name
    return None
