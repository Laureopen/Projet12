# Commandes événements
import click

from controllers.event_controller import (
    create_event,
    assign_support,
    update_my_event,
    list_events,
    list_unassigned_events,
    list_my_events,
    delete_event,
    list_signed_contracts,
    list_support_users
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
@click.option('--name', type=str, help="Nom de l'événement")
@click.option('--date_start', type=str, help="Date et heure de début (format YYYY-MM-DD HH:MM)")
@click.option('--date_end', type=str, help="Date et heure de fin (format YYYY-MM-DD HH:MM)")
@click.option('--location', type=str, help="Lieu")
@click.option('--attendees', type=int, help="Nombre de participants")
@click.option('--notes', type=str, help="Notes")
def create_event_cmd(name, date_start, date_end, location, attendees, notes):
    """
    Commande pour créer un nouvel événement.

    Args:
        name (str): Nom de l'événement.
        date_start (str): Date et heure de début au format YYYY-MM-DD HH:MM.
        date_end (str): Date et heure de fin au format YYYY-MM-DD HH:MM.
        location (str): Lieu de l'événement.
        attendees (int): Nombre de participants.
        notes (str): Notes complémentaires sur l'événement.
    """
    try:
        # Affiche la liste des contrats signés
        contracts_data = list_signed_contracts()

        lines = [f"{c['id']} | Client: {c['client_name']} ({c['client_email']}) | Commercial: {c['commercial_name']} | "
                 f"Montant: {c['amount_total']} | Signé le: {c['signed_date']}"
                 for c in contracts_data.values()]
        message = "\n".join(lines)
        click.echo(message)

        contract_id = click.prompt("\nID du contrat", type=int)

        # Validation du contrat
        if contract_id not in contracts_data:
            click.echo("Contrat non trouvé.")
            return

        # Prompts pour les autres champs
        if name is None:
            name = click.prompt("Nom de l'événement", type=str)

        if date_start is None:
            date_start = click.prompt("Date et heure de début (format YYYY-MM-DD HH:MM)", type=str)

        if date_end is None:
            date_end = click.prompt("Date et heure de fin (format YYYY-MM-DD HH:MM)", type=str)

        if location is None:
            location = click.prompt("Lieu", type=str)

        if attendees is None:
            attendees = click.prompt("Nombre de participants", type=int)

        if notes is None:
            notes = click.prompt("Notes", type=str)

        result = create_event(contract_id, name, date_start, date_end, location, attendees, notes)
        click.echo(result)

    except Exception as e:
        click.echo(f"Erreur lors de la création : {e}")


@click.command("assign-support")
@click.option('--support-email', type=str, help="Email du support à assigner")
def assign_support_cmd(support_email):
    """
    Commande pour affecter un événement à un membre du support.

    Args:
        support_email (str): Adresse email du membre du support.
    """
    try:
        # Affiche la liste des événements non assignés
        events_data = list_unassigned_events()

        lines = [f"[{e['id']}] {e['name']} | Début: {e['date_start']} | Fin: {e['date_end']} | "
                 f"Lieu: {e['location']} | Participants: {e['attendees']}"
                 for e in events_data.values()]
        message = "\n".join(lines)
        click.echo(message)

        event_id = click.prompt("\nID de l'événement", type=int)

        if event_id not in events_data:
            click.echo("Événement non trouvé.")
            return

        if support_email is None:
            # Affiche la liste des utilisateurs support
            click.echo("\nUtilisateurs support disponibles :")
            support_users = list_support_users()

            support_lines = [f"{u['email']} | {u['name']}"
                             for u in support_users.values()]
            support_message = "\n".join(support_lines)
            click.echo(support_message)

            support_email = click.prompt("Email du support à assigner", type=str)

        result = assign_support(event_id, support_email)
        click.echo(result)

    except Exception as e:
        click.echo(f"Erreur lors de l'assignation : {e}")


@click.command("update-event")
@click.option('--date-start', type=str, default=None, help="Nouvelle date de début (YYYY-MM-DD HH:MM)")
@click.option('--date-end', type=str, default=None, help="Nouvelle date de fin (YYYY-MM-DD HH:MM)")
@click.option('--location', type=str, default=None, help="Nouveau lieu")
@click.option('--attendees', type=int, default=None, help="Nombre de participants")
@click.option('--notes', type=str, default=None, help="Notes")
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
    try:
        # Affiche la liste des événements assignés à l'utilisateur
        events_data = list_my_events()

        lines = [f"[{e['id']}] {e['name']} | Début: {e['date_start']} | Fin: {e['date_end']} | "
                 f"Lieu: {e['location']} | Participants: {e['attendees']}"
                 for e in events_data.values()]
        message = "\n".join(lines)
        click.echo(message)

        event_id = click.prompt("\nID de l'événement à modifier", type=int)

        if event_id not in events_data:
            click.echo("Événement non trouvé.")
            return

        event_defaults = events_data[event_id]

        # Prompts avec valeurs par défaut
        if date_start is None:
            date_start = click.prompt("Date de début (YYYY-MM-DD HH:MM)", type=str,
                                      default=event_defaults["date_start"])

        if date_end is None:
            date_end = click.prompt("Date de fin (YYYY-MM-DD HH:MM)", type=str, default=event_defaults["date_end"])

        if location is None:
            location = click.prompt("Lieu", type=str, default=event_defaults["location"])

        if attendees is None:
            attendees = click.prompt("Nombre de participants", type=int, default=event_defaults["attendees"])

        if notes is None:
            notes = click.prompt("Notes", type=str, default=event_defaults["notes"])

        result = update_my_event(event_id, date_start, date_end, location, attendees, notes)
        click.echo(result)

    except Exception as e:
        click.echo(f"Erreur lors de la mise à jour : {e}")


@event_cli.command("list")
def list_events_cmd():
    """
    Commande pour afficher tous les événements.
    """
    try:
        events_data = list_events()

        lines = [f"[{e['id']}] {e['name']} | Début: {e['date_start']} | Fin: {e['date_end']} | "
                 f"Lieu: {e['location']} | Participants: {e['attendees']} | "
                 f"Support: {e['support_contact_id'] or 'Non assigné'}"
                 for e in events_data.values()]
        message = "\n".join(lines)
        click.echo(message)

    except Exception as e:
        click.echo(f"Erreur : {e}")


@event_cli.command("list-unassigned")
def list_unassigned_events_cmd():
    """
    Commande pour afficher les événements qui n'ont pas encore de membre du support assigné.
    """
    try:
        events_data = list_unassigned_events()

        lines = [f"[{e['id']}] {e['name']} | Début: {e['date_start']} | Fin: {e['date_end']} | "
                 f"Lieu: {e['location']} | Participants: {e['attendees']}"
                 for e in events_data.values()]
        message = "\n".join(lines)
        click.echo(message)

    except Exception as e:
        click.echo(f"Erreur : {e}")


@event_cli.command("list-my-events")
def list_my_events_cmd():
    """
    Commande pour afficher uniquement les événements assignés à l'utilisateur courant.
    """
    try:
        events_data = list_my_events()

        lines = [f"[{e['id']}] {e['name']} | Début: {e['date_start']} | Fin: {e['date_end']} | "
                 f"Lieu: {e['location']} | Participants: {e['attendees']}"
                 for e in events_data.values()]
        message = "\n".join(lines)
        click.echo(message)

    except Exception as e:
        click.echo(f"Erreur : {e}")


@event_cli.command("delete")
def delete_event_cmd():
    """
    Commande pour supprimer un événement existant.
    L'utilisateur doit sélectionner l'ID dans la liste affichée.
    """
    try:
        # Affiche tous les événements pour aider au choix
        events_data = list_events()

        lines = [f"[{e['id']}] {e['name']} | Début: {e['date_start']} | Fin: {e['date_end']} | "
                 f"Lieu: {e['location']} | Participants: {e['attendees']}"
                 for e in events_data.values()]
        message = "\n".join(lines)
        click.echo(message)

        event_id = click.prompt("\nID de l'événement à supprimer", type=int)

        if event_id not in events_data:
            click.echo("Événement non trouvé.")
            return

        if not click.confirm(
                f"Êtes-vous sûr de vouloir supprimer l'événement '"
                f"{events_data[event_id]['name']}' ? Cette action est irréversible."):
            click.echo("Suppression annulée.")
            return

        result = delete_event(event_id)
        click.echo(result)

    except Exception as e:
        click.echo(f"Erreur lors de la suppression : {e}")


# Enregistrement des sous-commandes dans le groupe principal
event_cli.add_command(create_event_cmd)
event_cli.add_command(assign_support_cmd)
event_cli.add_command(update_my_event_cmd)
event_cli.add_command(list_events_cmd)
event_cli.add_command(list_unassigned_events_cmd)
event_cli.add_command(list_my_events_cmd)
event_cli.add_command(delete_event_cmd)
