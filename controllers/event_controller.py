import click
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from models.models import Event, Contract, User
from utils.connection import engine
from utils.auth import get_current_user
from utils.auth_utils import require_role

session = sessionmaker(bind=engine)()


@click.command()
@click.option('--contract-id', prompt="ID du contrat")
@click.option('--name', prompt="Nom de l'événement")
@click.option('--date_start', prompt="Date et heure de début (format YYYY-MM-DD HH:MM)")
@click.option('--date_end', prompt="Date et heure de fin (format YYYY-MM-DD HH:MM)")
@click.option('--location', prompt="Lieu")
@click.option('--attendees', prompt="Nombre de participants", type=int)
@click.option('--notes', prompt="Notes")
@require_role("commercial")
def create_event(contract_id, name, date_start, date_end, location, attendees, notes):
    user = get_current_user()
    contract = session.query(Contract).filter_by(id=contract_id).first()

    if not contract:
        click.echo("Contrat introuvable.")
        return

    if not contract.signed:
        click.echo("Le contrat n’est pas signé. Impossible de créer un événement.")
        return

    if contract.sales_contact_id != user.id:
        click.echo("Vous ne pouvez créer un événement que pour vos propres contrats.")
        return

    try:
        date_start_obj = datetime.strptime(date_start, "%Y-%m-%d %H:%M")
    except ValueError:
        click.echo("Format de date de début invalide.")
        return

    try:
        date_end_obj = datetime.strptime(date_end, "%Y-%m-%d %H:%M")
    except ValueError:
        click.echo("Format de date de fin invalide.")
        return

    # Vérification de la cohérence des dates
    if date_end_obj <= date_start_obj:
        click.echo("La date de fin doit être postérieure à la date de début.")
        return


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
    click.echo("Événement créé avec succès.")


@click.command()
@click.option('--event-id', prompt="ID de l'événement")
@click.option('--support-email', prompt="Email du support à assigner")
@require_role("gestion")
def assign_support(event_id, support_email):
    event = session.query(Event).filter_by(id=event_id).first()
    if not event:
        click.echo("Événement introuvable.")
        return

    support_user = session.query(User).filter(
        User.email == support_email,
        User.department.has(name="support")
    ).first()
    if not support_user:
        click.echo("Utilisateur support introuvable.")
        return

    event.support_contact_id = support_user.id
    session.commit()
    click.echo(f"Support {support_user.name} assigné à l’événement.")


@click.command()
@click.option('--event-id', type=int, prompt="ID de l’événement à modifier", help="ID de l'événement")
@click.option('--date-start', default=None, help="Nouvelle date de début (YYYY-MM-DD HH:MM)")
@click.option('--date-end', default=None, help="Nouvelle date de fin (YYYY-MM-DD HH:MM)")
@click.option('--location', default=None, help="Nouveau lieu")
@click.option('--attendees', default=None, type=int, help="Nombre de participants")
@click.option('--notes', default=None, help="Notes")
@require_role("support")
def update_my_event(event_id, date_start, date_end, location, attendees, notes):
    """Mettre à jour un événement (support uniquement)"""
    current_user = get_current_user()

    if not hasattr(current_user, "id"):
        click.echo("Erreur : utilisateur invalide (ID manquant).")
        return

    event = session.query(Event).filter_by(id=event_id).first()

    if not event or event.support_contact_id != current_user.id:
        click.echo("Événement introuvable ou non assigné à vous.")
        return

    # Saisie interactive si valeurs absentes
    if date_start is None:
        default_start = event.date_start.strftime("%Y-%m-%d %H:%M") if event.date_start else ""
        date_start = click.prompt("Date de début (YYYY-MM-DD HH:MM)", default=default_start)

    if date_end is None:
        default_end = event.date_end.strftime("%Y-%m-%d %H:%M") if event.date_end else ""
        date_end = click.prompt("Date de fin (YYYY-MM-DD HH:MM)", default=default_end)

    if location is None:
        location = click.prompt("Lieu", default=event.location)

    if attendees is None:
        attendees = click.prompt("Nombre de participants", default=event.attendees, type=int)

    if notes is None:
        notes = click.prompt("Notes", default=event.notes or "")

    try:
        event.date_start = datetime.strptime(date_start, "%Y-%m-%d %H:%M")
        event.date_end = datetime.strptime(date_end, "%Y-%m-%d %H:%M")
        event.location = location
        event.attendees = attendees
        event.notes = notes

        session.commit()
        click.echo("Événement mis à jour avec succès.")
    except ValueError:
        click.echo("Erreur : format de date invalide. Utilisez YYYY-MM-DD HH:MM.")
    except Exception as e:
        click.echo(f"Erreur lors de la mise à jour : {e}")

@require_role("commercial", "gestion", "support")
def list_events():
    """Lister tous les événements"""
    events = session.query(Event).all()
    if not events:
        click.echo("Aucun événement trouvé.")
        return
    for event in events:
        click.echo(
            f"ID: {event.id}, Nom: {event.name}, Date: {event.date_start}, "
            f"Lieu: {event.location}, Participants: {event.attendees}, "
            f"Support assigné: {event.support_contact_id}"
        )


@require_role("gestion")
def list_unassigned_events():
    """Lister les événements sans support assigné"""
    events = session.query(Event).filter_by(support_contact_id=None).all()
    if not events:
        click.echo("Aucun événement non assigné trouvé.")
        return
    for event in events:
        click.echo(
            f"ID: {event.id}, Nom: {event.name}, Date: {event.date_start}, "
            f"Lieu: {event.location}, Participants: {event.attendees}"
        )


@require_role("support")
def list_my_events():
    """Lister les événements assignés au support connecté"""
    user = get_current_user()
    events = session.query(Event).filter_by(support_contact_id=user.id).all()
    if not events:
        click.echo("Vous n’avez aucun événement assigné.")
        return
    for event in events:
        click.echo(
            f"ID: {event.id}, Nom: {event.name}, Date: {event.date_start}, "
            f"Lieu: {event.location}, Participants: {event.attendees}"
        )
