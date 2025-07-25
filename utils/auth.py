import bcrypt
import getpass
import jwt
import os
from sqlalchemy.orm import sessionmaker
from models.models import User
from utils.connection import engine  # à créer dans connexion.py
from datetime import datetime, timedelta

# Clé secrète pour le JWT (à stocker en variable d'env !)
SECRET_KEY = os.getenv("EPIC_SECRET_KEY", "change_me")
ALGORITHM = "HS256"
TOKEN_FILE = "../.epic_token"

Session = sessionmaker(bind=engine)
session = Session()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_user():
    name = input("Nom complet : ")
    email = input("Email : ")
    password = getpass.getpass("Mot de passe : ")
    department = input("Département (sales, support, management) : ")
    role = input("Rôle : ")

    if session.query(User).filter_by(email=email).first():
        print("Utilisateur déjà existant.")
        return

    hashed = hash_password(password)
    user = User(name=name, email=email, password=hashed,
                department=department, role=role)
    session.add(user)
    session.commit()
    print("Utilisateur créé avec succès.")

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
        "role": user.role,
        "department": user.department,
        "email": user.email,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    with open(TOKEN_FILE, "w") as f:
        f.write(token)

    print("Authentification réussie.")

def get_current_user():
    if not os.path.exists(TOKEN_FILE):
        raise Exception("Vous n'êtes pas connecté.")

    with open(TOKEN_FILE, "r") as f:
        token = f.read()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = session.query(User).filter_by(id=payload["user_id"]).first()
        return user
    except jwt.ExpiredSignatureError:
        raise Exception("Session expirée. Veuillez vous reconnecter.")
    except jwt.InvalidTokenError:
        raise Exception("Jeton invalide. Veuillez vous reconnecter.")
