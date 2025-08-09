import click
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from models.event import Event
from models.contract import Contract
from models.user import User
from utils.connection import engine
from utils.auth import get_current_user
from utils.auth_utils import require_role

session = sessionmaker(bind=engine)()


def create_event(contract_id, name, date_start, date_end, location, attendees, notes):
    """
       Crée un événement pour un contrat signé appartenant au commercial connecté.

       Args:
           contract_id (int): ID du contrat.
           name (str): Nom de l'événement.
           date_start (str): Date et heure de début (format YYYY-MM-DD HH:MM).
           date_end (str): Date et heure de fin (format YYYY-MM-DD HH:MM).
           location (str): Lieu de l'événement.
           attendees (int): Nombre de participants.
           notes (str): Notes supplémentaires.

       Access:
           Rôle requis : commercial

       Effets:
           Enregistre l'événement dans la base de données après vérifications.
       """
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


def assign_support(event_id, support_email):
    """
      Assigne un utilisateur du support à un événement donné.

      Args:
          event_id (int): ID de l'événement.
          support_email (str): Email de l'utilisateur à assigner.

      Access:
          Rôle requis : gestion

      Effets:
          Met à jour le support_contact_id de l'événement si valide.
      """
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


def update_my_event(event_id, date_start, date_end, location, attendees, notes):
    """
       Met à jour les informations d’un événement assigné au support connecté.

       Args:
           event_id (int): ID de l'événement à mettre à jour.
           date_start (str, optional): Nouvelle date de début.
           date_end (str, optional): Nouvelle date de fin.
           location (str, optional): Nouveau lieu.
           attendees (int, optional): Nombre de participants.
           notes (str, optional): Notes complémentaires.

       Access:
           Rôle requis : support

       Effets:
           Met à jour les champs de l'événement si l'utilisateur est bien assigné.
       """
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
    """
       Liste tous les événements enregistrés.

       Access:
           Rôles requis : commercial, gestion, support

       Effets:
           Affiche les détails de tous les événements existants.
       """
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
    """
    Liste les événements sans support assigné.

    Access:
        Rôle requis : gestion

    Effets:
        Affiche les événements dont le champ `support_contact_id` est vide.
    """
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
    """
       Liste les événements assignés au support connecté.

       Access:
           Rôle requis : support

       Effets:
           Affiche uniquement les événements où l'utilisateur est désigné comme support.
       """
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
