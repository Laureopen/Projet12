from sqlalchemy.orm import sessionmaker
from models import Event, Contract, User
from connection import engine
from auth import get_current_user
from auth_utils import require_role
from datetime import datetime

session = sessionmaker(bind=engine)()

@require_role("commercial")
def create_event():
    user = get_current_user()
    contract_id = input("ID du contrat : ")

    contract = session.query(Contract).filter_by(id=contract_id).first()

    if not contract:
        print("Contrat introuvable.")
        return

    if not contract.signed:
        print("Le contrat n’est pas signé. Impossible de créer un événement.")
        return

    if contract.sales_contact_id != user.id:
        print("Vous ne pouvez créer un événement que pour vos propres contrats.")
        return

    name = input("Nom de l'événement : ")
    date_str = input("Date et heure (format YYYY-MM-DD HH:MM) : ")
    location = input("Lieu : ")
    attendees = int(input("Nombre de participants : "))
    notes = input("Notes : ")

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except ValueError:
        print("Format de date invalide.")
        return

    event = Event(
        name=name,
        contract_id=contract.id,
        date=date,
        location=location,
        attendees=attendees,
        notes=notes
    )
    session.add(event)
    session.commit()
    print("Événement créé avec succès.")

@require_role("gestion")
def assign_support():
    event_id = input("ID de l'événement : ")
    support_email = input("Email du support à assigner : ")

    event = session.query(Event).filter_by(id=event_id).first()
    if not event:
        print("Événement introuvable.")
        return

    support_user = session.query(User).filter_by(email=support_email, department="support").first()
    if not support_user:
        print("Utilisateur support introuvable.")
        return

    event.support_contact_id = support_user.id
    session.commit()
    print(f"Support {support_user.name} assigné à l’événement.")

@require_role("support")
def update_my_event():
    user = get_current_user()
    event_id = input("ID de l’événement : ")

    event = session.query(Event).filter_by(id=event_id, support_contact_id=user.id).first()
    if not event:
        print("Événement non trouvé ou non assigné à vous.")
        return

    new_date = input(f"Nouvelle date [{event.date}] (YYYY-MM-DD HH:MM) : ") or event.date
    location = input(f"Nouveau lieu [{event.location}] : ") or event.location
    attendees = input(f"Nouveau nombre de participants [{event.attendees}] : ") or event.attendees
    notes = input(f"Nouvelles notes : ") or event.notes

    try:
        if isinstance(new_date, str):
            event.date = datetime.strptime(new_date, "%Y-%m-%d %H:%M")
        else:
            event.date = new_date
        event.location = location
        event.attendees = int(attendees)
        event.notes = notes
        session.commit()
        print("Événement mis à jour.")
    except Exception as e:
        print("Erreur lors de la mise à jour :", e)

@require_role("commercial", "gestion", "support")
def list_events():
    events = session.query(Event).all()
    print("Liste des événements :")
    for e in events:
        print(f"[{e.id}] {e.name} - {e.date} - Lieu : {e.location} - Participants : {e.attendees}")

@require_role("gestion")
def list_unassigned_events():
    events = session.query(Event).filter_by(support_contact_id=None).all()
    print("Événements sans support assigné :")
    for e in events:
        print(f"[{e.id}] {e.name} - Contrat #{e.contract_id} - {e.date} - {e.location}")

@require_role("support")
def list_my_events():
    user = get_current_user()
    events = session.query(Event).filter_by(support_contact_id=user.id).all()
    print("Vos événements assignés :")
    for e in events:
        print(f"[{e.id}] {e.name} - {e.date} - {e.location} - Participants : {e.attendees}")
