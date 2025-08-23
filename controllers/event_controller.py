from datetime import datetime
from sqlalchemy.orm import sessionmaker, joinedload
from models.event import Event
from models.contract import Contract
from models.user import User
from utils.connection import engine
from utils.auth import get_current_user, get_user_role
from utils.auth_utils import require_role

# Création d'une session SQLAlchemy pour interagir avec la base de données
session = sessionmaker(bind=engine)()


@require_role("commercial")
def create_event(contract_id, name, date_start, date_end, location, attendees, notes):
    """
    Crée un événement pour un contrat signé appartenant au commercial connecté.

    Args:
        contract_id (int): ID du contrat lié à l'événement.
        name (str): Nom de l'événement.
        date_start (str): Date et heure de début au format 'YYYY-MM-DD HH:MM'.
        date_end (str): Date et heure de fin au format 'YYYY-MM-DD HH:MM'.
        location (str): Lieu de l'événement.
        attendees (int): Nombre de participants.
        notes (str): Informations complémentaires.

    Règles métier:
        - Le contrat doit exister.
        - Le contrat doit être signé.
        - Le commercial connecté doit être le propriétaire du contrat.
        - La date de fin doit être postérieure à la date de début.
    """
    user = get_current_user()
    contract = session.query(Contract).filter_by(id=contract_id).first()

    if not contract:
        raise Exception("Contrat introuvable.")

    if not contract.signed:
        raise Exception("Le contrat n'est pas signé. Impossible de créer un événement.")

    if contract.sales_contact_id != user.id:
        raise Exception("Vous ne pouvez créer un événement que pour vos propres contrats.")

    try:
        date_start_obj = datetime.strptime(date_start, "%Y-%m-%d %H:%M")
    except ValueError:
        raise Exception("Format de date de début invalide.")

    try:
        date_end_obj = datetime.strptime(date_end, "%Y-%m-%d %H:%M")
    except ValueError:
        raise Exception("Format de date de fin invalide.")

    # Vérification de la cohérence temporelle
    if date_end_obj <= date_start_obj:
        raise Exception("La date de fin doit être postérieure à la date de début.")

    # Création et enregistrement de l'événement
    event = Event(
        name=name,
        contract_id=contract.id,
        date_start=date_start_obj,
        date_end=date_end_obj,
        location=location,
        attendees=attendees,
        notes=notes
    )
    session.add(event)
    session.commit()
    return "Événement créé avec succès."


@require_role("commercial")
def delete_event(event_id):
    """
    Supprime un événement uniquement si le commercial connecté est le propriétaire du contrat lié.

    Args:
        event_id (int): ID de l'événement à supprimer.
    """
    current_user = get_current_user()

    if get_user_role(current_user) != "commercial":
        raise Exception("Vous n'avez pas les droits pour supprimer un événement.")

    # Chargement de l'événement avec le contrat associé
    event = session.query(Event).options(joinedload(Event.contract)).filter_by(id=event_id).first()
    if not event:
        raise Exception("Événement introuvable.")

    if event.contract.sales_contact_id != current_user.id:
        raise Exception("Vous ne pouvez supprimer que les événements liés à vos propres contrats.")

    session.delete(event)
    session.commit()
    return f"Événement ID {event_id} supprimé avec succès."


@require_role("gestion")
def assign_support(event_id, support_email):
    """
    Assigne un utilisateur de type 'support' à un événement.

    Args:
        event_id (int): ID de l'événement.
        support_email (str): Email du support à assigner.
    """
    event = session.query(Event).filter_by(id=event_id).first()
    if not event:
        raise Exception("Événement introuvable.")

    # Recherche de l'utilisateur dans le département "support"
    support_user = session.query(User).filter(
        User.email == support_email,
        User.department.has(name="support")
    ).first()
    if not support_user:
        raise Exception("Utilisateur support introuvable.")

    event.support_contact_id = support_user.id
    session.commit()
    return f"Support {support_user.name} assigné à l'événement."


@require_role("support")
def update_my_event(event_id, date_start=None, date_end=None, location=None, attendees=None, notes=None):
    """
    Met à jour un événement assigné au support connecté.

    Args:
        event_id (int): ID de l'événement à modifier.
        date_start (str): Nouvelle date/heure de début (YYYY-MM-DD HH:MM).
        date_end (str): Nouvelle date/heure de fin (YYYY-MM-DD HH:MM).
        location (str): Nouveau lieu.
        attendees (int): Nouveau nombre de participants.
        notes (str): Nouvelles notes.
    """
    current_user = get_current_user()

    if not hasattr(current_user, "id"):
        raise Exception("Erreur : utilisateur invalide (ID manquant).")

    event = session.query(Event).filter_by(id=event_id).first()

    if not event or event.support_contact_id != current_user.id:
        raise Exception("Événement introuvable ou non assigné à vous.")

    try:
        if date_start is not None:
            event.date_start = datetime.strptime(date_start, "%Y-%m-%d %H:%M")
        if date_end is not None:
            event.date_end = datetime.strptime(date_end, "%Y-%m-%d %H:%M")
        if location is not None:
            event.location = location
        if attendees is not None:
            event.attendees = attendees
        if notes is not None:
            event.notes = notes

        session.commit()
        return "Événement mis à jour avec succès."
    except ValueError:
        raise Exception("Erreur : format de date invalide. Utilisez YYYY-MM-DD HH:MM.")
    except Exception as e:
        raise Exception(f"Erreur lors de la mise à jour : {e}")


@require_role("commercial", "gestion", "support")
def list_events():
    """
    Retourne la liste de tous les événements sous forme de dictionnaire.
    """
    try:
        events = session.query(Event).all()
        if not events:
            raise Exception("Aucun événement trouvé.")

        events_dict = {}
        for event in events:
            events_dict[event.id] = {
                "id": event.id,
                "name": event.name,
                "date_start": event.date_start.strftime("%Y-%m-%d %H:%M"),
                "date_end": event.date_end.strftime("%Y-%m-%d %H:%M"),
                "location": event.location,
                "attendees": event.attendees,
                "notes": event.notes or "",
                "support_contact_id": event.support_contact_id
            }

        return events_dict

    except Exception as e:
        raise Exception(f"Erreur lors de la récupération des événements : {e}")


@require_role("gestion")
def list_unassigned_events():
    """
    Retourne la liste des événements non assignés sous forme de dictionnaire.
    """
    try:
        events = session.query(Event).filter_by(support_contact_id=None).all()
        if not events:
            raise Exception("Aucun événement non assigné trouvé.")

        events_dict = {}
        for event in events:
            events_dict[event.id] = {
                "id": event.id,
                "name": event.name,
                "date_start": event.date_start.strftime("%Y-%m-%d %H:%M"),
                "date_end": event.date_end.strftime("%Y-%m-%d %H:%M"),
                "location": event.location,
                "attendees": event.attendees,
                "notes": event.notes or ""
            }

        return events_dict

    except Exception as e:
        raise Exception(f"Erreur lors de la récupération des événements non assignés : {e}")


@require_role("support")
def list_my_events():
    """
    Retourne la liste des événements assignés au support connecté sous forme de dictionnaire.
    """
    try:
        user = get_current_user()
        events = session.query(Event).filter_by(support_contact_id=user.id).all()
        if not events:
            raise Exception("Vous n'avez aucun événement assigné.")

        events_dict = {}
        for event in events:
            events_dict[event.id] = {
                "id": event.id,
                "name": event.name,
                "date_start": event.date_start.strftime("%Y-%m-%d %H:%M"),
                "date_end": event.date_end.strftime("%Y-%m-%d %H:%M"),
                "location": event.location,
                "attendees": event.attendees,
                "notes": event.notes or ""
            }

        return events_dict

    except Exception as e:
        raise Exception(f"Erreur lors de la récupération de vos événements : {e}")


def list_signed_contracts():
    """
    Retourne la liste des contrats signés sous forme de dictionnaire.
    """
    try:
        from models.client import Client

        contracts = (
            session.query(Contract, Client, User)
            .join(Client, Contract.client_id == Client.id)
            .join(User, Contract.sales_contact_id == User.id)
            .filter(Contract.signed)
            .all()
        )

        if not contracts:
            raise Exception("Aucun contrat signé trouvé.")

        contracts_dict = {}
        for contract, client, commercial in contracts:
            contracts_dict[contract.id] = {
                "id": contract.id,
                "client_name": client.name,
                "client_email": client.email,
                "commercial_name": commercial.name,
                "amount_total": contract.amount_total,
                "signed_date": (contract.signed_date.strftime('%Y-%m-%d')
                                if contract.signed_date else "Non défini")

            }

        return contracts_dict

    except Exception as e:
        raise Exception(f"Erreur lors de la récupération des contrats signés : {e}")


def list_support_users():
    """
    Retourne la liste des utilisateurs du support sous forme de dictionnaire.
    """
    try:
        support_users = session.query(User).filter(
            User.department.has(name="support")
        ).all()

        if not support_users:
            raise Exception("Aucun utilisateur support trouvé.")

        users_dict = {}
        for user in support_users:
            users_dict[user.email] = {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }

        return users_dict

    except Exception as e:
        raise Exception(f"Erreur lors de la récupération des utilisateurs support : {e}")
