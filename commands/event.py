# Commandes événements
import click

from controllers.event_controller import (
    create_event,
    assign_support,
    update_my_event,
    list_events,
    list_unassigned_events,
    list_my_events,
    delete_event
)


@click.group()
def event_cli():
    """
    Commandes liées aux événements.

    Ce groupe permet de gérer toutes les opérations concernant les événements :
    - create : création d'un événement
    - assign-support : affectation à un membre du support
    - update-event : mise à jour d'un événement existant
    - list : affichage de tous les événements
    - list-unassigned : affichage des événements non assignés
    - list-my-events : affichage des événements assignés à l'utilisateur courant
    - delete : suppression d'un événement
    """
    pass


@event_cli.group()
def event():
    """
    Sous-groupe pour la gestion des événements.
    Utile si l'on veut regrouper certaines commandes spécifiques sous un même namespace.
    """
    pass


@click.command("create")
@click.option('--contract-id', prompt="ID du contrat")
@click.option('--name', prompt="Nom de l'événement")
@click.option('--date_start', prompt="Date et heure de début (format YYYY-MM-DD HH:MM)")
@click.option('--date_end', prompt="Date et heure de fin (format YYYY-MM-DD HH:MM)")
@click.option('--location', prompt="Lieu")
@click.option('--attendees', prompt="Nombre de participants", type=int)
@click.option('--notes', prompt="Notes")
def create_event_cmd(contract_id, name, date_start, date_end, location, attendees, notes):
    """
    Commande pour créer un nouvel événement.

    Args:
        contract_id (int): ID du contrat lié à l'événement.
        name (str): Nom de l'événement.
        date_start (str): Date et heure de début au format YYYY-MM-DD HH:MM.
        date_end (str): Date et heure de fin au format YYYY-MM-DD HH:MM.
        location (str): Lieu de l'événement.
        attendees (int): Nombre de participants.
        notes (str): Notes complémentaires sur l'événement.
    """
    create_event(contract_id, name, date_start, date_end, location, attendees, notes)


@click.command("assign-support")
@click.option('--event-id', prompt="ID de l'événement")
@click.option('--support-email', prompt="Email du support à assigner")
def assign_support_cmd(event_id, support_email):
    """
    Commande pour affecter un événement à un membre du support.

    Args:
        event_id (int): Identifiant de l'événement.
        support_email (str): Adresse email du membre du support.
    """
    assign_support(event_id, support_email)


@click.command("update-event")
@click.option('--date-start', default=None, help="Nouvelle date de début (YYYY-MM-DD HH:MM)")
@click.option('--date-end', default=None, help="Nouvelle date de fin (YYYY-MM-DD HH:MM)")
@click.option('--location', default=None, help="Nouveau lieu")
@click.option('--attendees', default=None, type=int, help="Nombre de participants")
@click.option('--notes', default=None, help="Notes")
def update_my_event_cmd(date_start, date_end, location, attendees, notes):
    """
    Commande pour mettre à jour un événement assigné à l'utilisateur courant.

    Args:
        date_start (str, optional): Nouvelle date de début.
        date_end (str, optional): Nouvelle date de fin.
        location (str, optional): Nouveau lieu.
        attendees (int, optional): Nouveau nombre de participants.
        notes (str, optional): Nouvelles notes.
    """
    # Affiche la liste pour que l'utilisateur choisisse l'événement à modifier
    list_events()
    event_id = click.prompt("\n\nID de l'événement à modifier", type=int)

    update_my_event(event_id, date_start, date_end, location, attendees, notes)


@event_cli.command("list")
def list_events_cmd():
    """
    Commande  pour afficher tous les événements.
    """
    list_events()


@event_cli.command("list-unassigned")
def list_unassigned_events_cmd():
    """
    Commande pour afficher les événements qui n'ont pas encore de membre du support assigné.
    """
    list_unassigned_events()


@event_cli.command("list-my-events")
def list_my_events_cmd():
    """
    Commande  pour afficher uniquement les événements assignés à l'utilisateur courant.
    """
    list_my_events()


@event_cli.command("delete")
def delete_event_cmd():
    """
    Commande pour supprimer un événement existant.
    L'utilisateur doit sélectionner l'ID dans la liste affichée.
    """
    # Affiche tous les événements pour aider au choix
    list_events()
    event_id = click.prompt("\n\nID de l'événement à supprimer", type=int)

    delete_event(event_id)


# Enregistrement des sous-commandes dans le groupe principal
event_cli.add_command(create_event_cmd)
event_cli.add_command(assign_support_cmd)
event_cli.add_command(update_my_event_cmd)
event_cli.add_command(list_events_cmd)
event_cli.add_command(list_unassigned_events_cmd)
event_cli.add_command(list_my_events_cmd)
event_cli.add_command(delete_event_cmd)
