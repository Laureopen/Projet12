import bcrypt
import getpass
import jwt
import os
from sqlalchemy.orm import sessionmaker, joinedload
from models.user import User
from utils.connection import engine
from datetime import datetime, timedelta

# Clé secrète pour le JWT (à stocker en variable d'env !)
SECRET_KEY = os.getenv("EPIC_SECRET_KEY", "change_me")
ALGORITHM = "HS256"
TOKEN_FILE = "../.epic_token"

Session = sessionmaker(bind=engine)
session = Session()


def populate_departments():
    # importer les modèles ici pour éviter le problème de mapping
    from models.department import Department
    from models.user import User
    from models.client import Client
    from models.contract import Contract
    from models.event import Event

    Session = sessionmaker(bind=engine)
    with Session() as session:
        for name in ["commercial", "support", "gestion"]:
            if not session.query(Department).filter_by(name=name).first():
                session.add(Department(name=name))
        session.commit()


populate_departments()

session.commit()
session.close()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def login():
    email = input("Email : ")
    password = getpass.getpass("Mot de passe : ")

    user = session.query(User).filter_by(email=email).first()
    if not user:
        print("Utilisateur introuvable.")
        return

    if not check_password(password, user.password):
        print("Mot de passe incorrect.")
        return

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


def get_user_role(user):
    if user and user.department:
        return user.department.name
    return None

