import re
import sentry_sdk
from sqlalchemy.orm import sessionmaker
from models.client import Client
from utils import auth
from utils.connection import engine
from utils.auth import get_current_user
from utils.auth_utils import require_role

# Création d'une session SQLAlchemy pour interagir avec la base de données
session = sessionmaker(bind=engine)()


def validate_email(email):
    """
    Valide le format d'une adresse email.

    Args:
        email (str): Adresse email à valider.

    Returns:
        str: L'adresse email validée.

    Raises:
        Exception: Si le format de l'email est invalide.
    """
    pattern = r"^[^@]+@[^@]+\.[^@]+$"  # Expression régulière simple pour un email basique
    if not re.match(pattern, email):
        raise Exception("Format d'email invalide.")
    return email


def validate_phone(phone):
    """
    Valide le format d'un numéro de téléphone.

    Args:
        phone (str): Numéro de téléphone à valider.

    Returns:
        str: Le numéro de téléphone validé.

    Raises:
        Exception: Si le format du téléphone est invalide.
    """
    pattern = r"^\+?\d{10,15}$"  # Accepte un '+' optionnel suivi de 10 à 15 chiffres
    if not re.match(pattern, phone):
        raise Exception(
            "Numéro de téléphone invalide. Entrez entre 10 et 15 chiffres, avec éventuellement un '+'."
        )
    return phone


@require_role("commercial")
def create_client(name, email, phone, company):
    """
    Crée un nouveau client et l'associe au commercial connecté.

    Args:
        name (str): Nom du client.
        email (str): Adresse email.
        phone (str): Numéro de téléphone.
        company (str): Nom de l'entreprise.

    Returns:
        str: Message de succès.

    Raises:
        Exception: En cas d'erreur lors de la création.
    """
    try:
        # Validation des données
        validate_email(email)
        validate_phone(phone)

        user = get_current_user()  # Récupération du commercial connecté

        # Création de l'objet Client
        client = Client(
            name=name,
            email=email,
            phone=phone,
            company=company,
            sales_contact_id=user.id
        )

        # Enregistrement en base
        session.add(client)
        session.commit()

        # Log pour Sentry
        sentry_sdk.capture_message(f"Client créé : {email} par {user.email}")

        return "Client créé avec succès."

    except Exception as e:
        raise Exception(f"Erreur lors de la création du client : {e}")


@require_role("commercial", "gestion", "support")
def list_clients():
    """
    Retourne la liste des clients sous forme de dictionnaire.
    """
    try:
        clients = session.query(Client).all()
        if not clients:
            raise Exception("Aucun client trouvé.")

        clients_dict = {}
        for c in clients:
            # Formatage des dates ou affichage "Date inconnue"
            created_at_str = c.created_date.strftime("%d %B %Y") if c.created_date else "Date inconnue"
            updated_at_str = c.updated_date.strftime("%d %B %Y") if c.updated_date else "Date inconnue"
            sales_contact_name = c.sales_contact.name if c.sales_contact else "Aucun commercial assigné"

            clients_dict[c.id] = {
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "phone": c.phone,
                "company": c.company,
                "sales_contact_name": sales_contact_name,
                "created_date": created_at_str,
                "updated_date": updated_at_str
            }
        return clients_dict

    except Exception as e:
        raise Exception(f"Erreur lors de la récupération des clients : {e}")


@require_role("commercial")
def update_client(client_id, name, email, phone, company, db_session=None, current_user=None):
    """
    Met à jour les informations d'un client existant.

    Args:
        client_id (int): ID du client à mettre à jour.
        name (str): Nouveau nom.
        email (str): Nouvel email.
        phone (str): Nouveau téléphone.
        company (str): Nouvelle entreprise.
        db_session (Session | None): auth.session ou session de test
        current_user (User | None): utilisateur de la session ou de test

    Returns:
        str: Message de succès.

    Raises:
        Exception: En cas d'erreur lors de la mise à jour.
    """
    try:
        session_to_use = db_session if db_session is not None else auth.session

        client = session_to_use.query(Client).filter_by(id=client_id).first()

        if not client:
            raise Exception("Client non trouvé.")

        current_user = current_user or get_current_user()

        # Vérification : un commercial ne peut modifier que ses propres clients
        if client.sales_contact_id != current_user.id:
            raise Exception("Vous ne pouvez modifier que vos propres clients.")

        # Validation email et téléphone
        validate_email(email)
        validate_phone(phone)

        # Mise à jour des champs
        client.name = name
        client.email = email
        client.phone = phone
        client.company = company

        session_to_use.commit()

        # Log pour Sentry
        sentry_sdk.capture_message(f"Client modifié : {client_id} par {current_user.email}")

        return "Client mis à jour avec succès."

    except Exception as e:
        raise Exception(f"Erreur lors de la mise à jour du client : {e}")


@require_role("commercial")
def delete_client(client_id, db_session=None, current_user=None):
    """
    Supprime un client existant.

    Args:
        client_id (int): ID du client à supprimer.
        db_session (Session | None): auth.session ou session de test
        current_user (User | None): utilisateur de la session ou de test

    Returns:
        str: Message de succès.

    Raises:
        Exception: En cas d'erreur lors de la suppression.
    """
    try:
        session_to_use = db_session if db_session is not None else auth.session

        client = session_to_use.query(Client).filter_by(id=client_id).first()

        if not client:
            raise Exception("Client non trouvé.")

        current_user = current_user or get_current_user()

        # Vérification : un commercial ne peut supprimer que ses propres clients
        if client.sales_contact_id != current_user.id:
            raise Exception("Vous ne pouvez supprimer que vos propres clients.")

        # Vérifie associations (contrats, événements, etc.)
        if client.contracts or client.events:
            raise Exception(
                f"Impossible de supprimer le client '{client.name}' : "
                "des contrats ou événements lui sont associés."
            )

        session_to_use.delete(client)
        session_to_use.commit()

        # Log pour Sentry
        sentry_sdk.capture_message(f"Client supprimé : {client_id} par {current_user.email}")

        return f"Client '{client.name}' supprimé avec succès."

    except Exception as e:
        raise Exception(f"Erreur lors de la suppression du client : {e}")
