# utils/auth.py
import bcrypt
import getpass
import jwt
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker, joinedload
from utils.connection import engine
from models import User, Department  # importer via models/__init__.py

# --- Configuration ---
SECRET_KEY = os.getenv("EPIC_SECRET_KEY", "change_me")
ALGORITHM = "HS256"
TOKEN_FILE = ".epic_token"

Session = sessionmaker(bind=engine)


# --- Helpers mot de passe ---
def hash_password(password: str) -> str:
    """Retourne le mot de passe hashé (str)."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, hashed: str) -> bool:
    """Vérifie qu'un mot de passe correspond au hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


# --- Initialisation des départements (à appeler explicitement au démarrage) ---
def init_departments(defaults=None):
    """
    Crée les départements par défaut s'ils n'existent pas.
    Ne s'exécute pas à l'import — appelle cette fonction depuis ton script d'initialisation.
    """
    if defaults is None:
        defaults = ["commercial", "support", "gestion"]

    session = Session()
    try:
        for name in defaults:
            if not session.query(Department).filter_by(name=name).first():
                session.add(Department(name=name))
        session.commit()
    finally:
        session.close()


# --- Création d'utilisateur (interactive) ---
def create_user_interactive():
    """Crée un utilisateur via input() (mode console interactif)."""
    session = Session()
    try:
        name = input("Nom complet : ").strip()
        email = input("Email : ").strip()
        password = getpass.getpass("Mot de passe : ").strip()

        # Affiche les départements disponibles
        departments = session.query(Department).all()
        for dept in departments:
            print(f"{dept.id} - {dept.name}")

        dep_input = input("Département (id) : ").strip()
        try:
            dep_id = int(dep_input)
        except ValueError:
            print("Entrée invalide, veuillez entrer un ID numérique.")
            return

        department = session.query(Department).get(dep_id)
        if not department:
            print("Département introuvable.")
            return

        if session.query(User).filter_by(email=email).first():
            print("Utilisateur déjà existant.")
            return

        hashed = hash_password(password)
        user = User(name=name, email=email, password=hashed, department=department)
        session.add(user)
        session.commit()
        print("Utilisateur créé avec succès.")
    finally:
        session.close()


# --- Création d'utilisateur non interactive (fonctionnelle) ---
def create_user(name: str, email: str, password: str, department_name: str):
    """
    Crée un utilisateur programmaticalement.
    Lève ValueError si le département n'existe pas ou si l'email est déjà pris.
    """
    session = Session()
    try:
        department = session.query(Department).filter_by(name=department_name).first()
        if not department:
            raise ValueError(f"Le département '{department_name}' n'existe pas.")

        if session.query(User).filter_by(email=email).first():
            raise ValueError("Utilisateur déjà existant.")

        hashed = hash_password(password)
        user = User(name=name, email=email, password=hashed, department=department)
        session.add(user)
        session.commit()
        return user
    finally:
        session.close()


# --- Login (console interactive) ---
def login_interactive():
    """Login interactif : demande email + mot de passe, écrit le token dans TOKEN_FILE."""
    email = input("Email : ").strip()
    password = getpass.getpass("Mot de passe : ").strip()
    return _login_and_write_token(email, password)


def _login_and_write_token(email: str, password: str):
    session = Session()
    try:
        user = session.query(User).filter_by(email=email).first()
        if not user:
            print("Utilisateur introuvable.")
            return False

        if not check_password(password, user.password):
            print("Mot de passe incorrect.")
            return False

        payload = {
            "user_id": user.id,
            "exp": datetime.utcnow() + timedelta(hours=2),
            "department": get_user_role(user),
            "email": user.email,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        with open(TOKEN_FILE, "w") as f:
            f.write(token)

        print("Authentification réussie.")
        return True
    finally:
        session.close()


# --- Récupération utilisateur courant depuis le token ---
def get_current_user():
    """
    Renvoie l'objet User correspondant au token stocké dans TOKEN_FILE.
    Lève Exception si non connecté / token invalide / expiré.
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
        user = session.query(User).options(joinedload(User.department)).filter_by(id=user_id).first()
        if not user:
            raise Exception("Utilisateur introuvable pour l'ID du token.")
        return user
    finally:
        session.close()


# --- Role helper ---
def get_user_role(user):
    """Renvoie le nom du département (role) si disponible."""
    if user and getattr(user, "department", None):
        return user.department.name
    return None


# --- Petit utilitaire pour supprimer le token (logout) ---
def logout():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        print("Déconnecté.")
    else:
        print("Aucun token trouvé.")


# --- Si on souhaite initialiser les départements via ce module en script ---
if __name__ == "__main__":
    # Exemple d'usage : python utils/auth.py init
    # On exécute l'init seulement si le module est lancé directement.
    init_departments()
    print("Départements initialisés (si besoin).")
