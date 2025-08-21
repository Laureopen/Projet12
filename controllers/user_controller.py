import sentry_sdk
from sqlalchemy.orm import sessionmaker
from models.department import Department
from models.user import User
from utils.auth import hash_password, get_current_user, get_user_role
from utils.auth_utils import require_role
from utils.connection import engine


# Création d'une session SQLAlchemy
session = sessionmaker(bind=engine)()


@require_role("gestion")
def create_user(name, email, department_id, password):
    """
    Crée un nouvel utilisateur avec le département et mot de passe spécifiés.
    """
    try:
        # Vérifie si le département existe
        department = session.get(Department, department_id)
        if not department:
            raise Exception("Département introuvable.")

        # Vérifie si l'email est déjà utilisé
        if session.query(User).filter_by(email=email).first():
            raise Exception("Utilisateur déjà existant.")

        # Hash du mot de passe
        hashed = hash_password(password)

        # Création et ajout de l'utilisateur
        user = User(name=name, email=email, password=hashed, department=department)
        session.add(user)
        session.commit()

        # Log pour Sentry
        current_user = get_current_user()
        sentry_sdk.capture_message(f"Utilisateur créé : {email} par {current_user.email}")

        return "Utilisateur créé avec succès."

    except Exception as e:
        raise Exception(f"Erreur lors de la création de l'utilisateur : {e}")


@require_role("gestion")
def update_user(email, name=None, password=None, department_id=None):
    """
    Met à jour un utilisateur existant.
    """
    try:
        user = session.query(User).filter_by(email=email).first()
        if not user:
            raise Exception("Utilisateur introuvable.")

        if name:
            user.name = name
        if password:
            user.password = hash_password(password)

        if department_id:
            department = session.get(Department, department_id)
            if not department:
                raise Exception("Département introuvable.")
            user.department = department

        session.commit()
        sentry_sdk.capture_message(f"Utilisateur modifié : {email} par {get_current_user().email}")
        return "Utilisateur mis à jour avec succès."

    except Exception as e:
        raise Exception(f"Erreur lors de la mise à jour de l'utilisateur : {e}")


@require_role("gestion")
def delete_user(email):
    """
    Supprime un utilisateur identifié par son email.
    """
    current_user = get_current_user()
    if get_user_role(current_user) != "gestion":
        raise Exception("Vous n'avez pas les droits pour supprimer un utilisateur.")

    user = session.query(User).filter_by(email=email).first()
    if not user:
        raise Exception(f"Utilisateur '{email}' introuvable.")

    # Vérifie associations
    if user.clients or user.contracts or user.supported_events:
        raise Exception(
            f"Impossible de supprimer '{email}' : "
            "des clients, contrats ou événements lui sont associés."
        )

    session.delete(user)
    session.commit()
    sentry_sdk.capture_message(f"Utilisateur supprimé : {email} par {current_user.email}")
    return f"Utilisateur avec l'email '{email}' supprimé avec succès."


@require_role("gestion")
def list_users():
    """
    Retourne la liste de tous les utilisateurs enregistrés sous forme de dictionnaire.
    """
    try:
        users = session.query(User).all()
        if not users:
            raise Exception("Aucun utilisateur trouvé.")

        users_dict = {}
        for user in users:
            dept_name = user.department.name if user.department else "Non défini"
            users_dict[user.email] = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "department_name": dept_name
            }

        return users_dict

    except Exception as e:
        return f"Erreur lors de la récupération des utilisateurs : {e}"


def list_departments():
    """
    Retourne la liste de tous les départements enregistrés.
    """
    try:
        departments = session.query(Department).all()
        if not departments:
            raise Exception("Aucun département trouvé.")

        lines = [f"{dept.id} | {dept.name}" for dept in departments]
        return "\n".join(lines)

    except Exception as e:
        return f"Erreur lors de la récupération des départements : {e}"
