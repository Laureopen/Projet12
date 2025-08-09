# Commandes événements
import click

from controllers.event_controller import (
    create_event,
    assign_support,
    update_my_event,
    list_events,
    list_unassigned_events,
    list_my_events
)
from utils.auth_utils import require_role


@click.group()
def event_cli():
    """Commandes liées aux évènements"""
    pass


@event_cli.group()
def event():
    """Gestion des événements"""
    pass


@click.command("create")
@click.option('--contract-id', prompt="ID du contrat")
@click.option('--name', prompt="Nom de l'événement")
@click.option('--date_start', prompt="Date et heure de début (format YYYY-MM-DD HH:MM)")
@click.option('--date_end', prompt="Date et heure de fin (format YYYY-MM-DD HH:MM)")
@click.option('--location', prompt="Lieu")
@click.option('--attendees', prompt="Nombre de participants", type=int)
@click.option('--notes', prompt="Notes")
@require_role("commercial")
def create_event_cmd(contract_id, name, date_start, date_end, location, attendees, notes):
    """Créer un évènement"""
    create_event(contract_id, name, date_start, date_end, location, attendees, notes)


@click.command("assign-support")
@click.option('--event-id', prompt="ID de l'événement")
@click.option('--support-email', prompt="Email du support à assigner")
@require_role("gestion")
def assign_support_cmd(event_id, support_email):
    """Affecter un évènement à un membre du support"""
    assign_support(event_id, support_email)


@click.command("update-event")
@click.option('--event-id', type=int, prompt="ID de l’événement à modifier", help="ID de l'événement")
@click.option('--date-start', default=None, help="Nouvelle date de début (YYYY-MM-DD HH:MM)")
@click.option('--date-end', default=None, help="Nouvelle date de fin (YYYY-MM-DD HH:MM)")
@click.option('--location', default=None, help="Nouveau lieu")
@click.option('--attendees', default=None, type=int, help="Nombre de participants")
@click.option('--notes', default=None, help="Notes")
@require_role("support")
def update_my_event_cmd(event_id, date_start, date_end, location, attendees, notes):
    """Mettre à jour un événement"""
    update_my_event(event_id, date_start, date_end, location, attendees, notes)


@event_cli.command("list")
def list_events_cmd():
    """Lister tous les événements"""
    list_events()


@event_cli.command("list-unassigned")
def list_unassigned_events_cmd():
    """Lister les événements sans support assigné"""
    list_unassigned_events()


@event_cli.command("list-my-events")
def list_my_events_cmd():
    """Lister mes événements assignés"""
    list_my_events()


event_cli.add_command(create_event_cmd)
event_cli.add_command(assign_support_cmd)
event_cli.add_command(update_my_event_cmd)
event_cli.add_command(list_events_cmd)
event_cli.add_command(list_unassigned_events_cmd)
event_cli.add_command(list_my_events_cmd)
