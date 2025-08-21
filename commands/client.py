import click
import re

# Import des fonctions liées aux clients
from controllers.client_controller import (
    create_client,
    list_clients,
    update_client,
    delete_client
)


def validate_email(ctx, param, value):
    """
    Valide le format d'une adresse email.

    Args:
        ctx: Contexte Click (non utilisé directement, mais requis par Click).
        param: Paramètre CLI lié (non utilisé directement).
        value (str): Adresse email à valider.

    Returns:
        str: L'adresse email validée.

    Raises:
        click.BadParameter: Si le format de l'email est invalide.
    """
    pattern = r"^[^@]+@[^@]+\.[^@]+$"  # Expression régulière simple pour un email basique
    if not re.match(pattern, value):
        raise click.BadParameter("Format d'email invalide.")
    return value


def validate_phone(ctx, param, value):
    """
    Valide le format d'un numéro de téléphone.

    Args:
        ctx: Contexte Click (non utilisé directement).
        param: Paramètre CLI lié (non utilisé directement).
        value (str): Numéro de téléphone à valider.

    Returns:
        str: Le numéro de téléphone validé.

    Raises:
        click.BadParameter: Si le format du téléphone est invalide.
    """
    pattern = r"^\+?\d{10,15}$"  # Accepte un '+' optionnel suivi de 10 à 15 chiffres
    if not re.match(pattern, value):
        raise click.BadParameter(
            "Numéro de téléphone invalide. Entrez entre 10 et 15 chiffres, avec éventuellement un '+'."
        )
    return value


@click.group()
def client_cli():
    """
   Commandes liées à la gestion des clients.

    Ce groupe permet de regrouper plusieurs sous-commandes :
    - create : créer un nouveau client
    - list : lister les clients existants
    - update : modifier un client existant
    - delete : supprimer un client existant
    """
    pass


@click.command("create")
@click.option('--name', type=str, prompt="Nom du client", help="Nom complet du client")
@click.option('--email', type=str, prompt="Email", callback=validate_email, help="Adresse email du client")
@click.option('--phone', type=str, prompt="Téléphone", callback=validate_phone, help="Numéro de téléphone du client")
@click.option('--company', type=str, prompt="Entreprise", help="Nom de l'entreprise")
def create_client_cmd(name, email, phone, company):
    """
    Commande pour créer un nouveau client.
    """
    try:
        result = create_client(name, email, phone, company)
        click.echo(result)
    except Exception as e:
        click.echo(f"Erreur lors de la création : {e}")


@click.command("list")
def list_clients_cmd():
    """
    Commande pour afficher la liste de tous les clients.
    """
    try:
        clients_data = list_clients()

        lines = [f"[{c['id']}] | {c['name']} | {c['email']} | "
                 f"{c['phone']} | {c['company']} | "
                 f"Commercial : {c['sales_contact_name']} | "
                 f"Créé le : {c['created_date']} | Modifié le : {c['updated_date']}"
                 for c in clients_data.values()]
        message = "\n".join(lines)
        click.echo(message)

    except Exception as e:
        click.echo(f"Erreur : {e}")


@click.command("update")
@click.option('--name', type=str, default=None, help="Nouveau nom du client")
@click.option('--email', type=str, default=None, help="Nouvel email du client")
@click.option('--phone', type=str, default=None, help="Nouveau téléphone du client")
@click.option('--company', type=str, default=None, help="Nouvelle entreprise du client")
def update_client_cmd(name, email, phone, company):
    """
    Commande pour mettre à jour les informations d'un client existant.
    """
    try:
        # Affiche la liste des clients
        clients_data = list_clients()

        lines = [f"[{c['id']}] | {c['name']} | {c['email']} | "
                 f"{c['phone']} | {c['company']} | "
                 f"Commercial : {c['sales_contact_name']} | "
                 f"Créé le : {c['created_date']} | Modifié le : {c['updated_date']}"
                 for c in clients_data.values()]
        message = "\n".join(lines)
        click.echo(message)

        # Demande l'ID après affichage
        client_id = click.prompt("ID du client à modifier", type=int)

        if client_id not in clients_data:
            click.echo("Client non trouvé.")
            return

        client_defaults = clients_data[client_id]

        # Prompts pour les valeurs non fournies
        if name is None:
            name = click.prompt("Nom", type=str, default=client_defaults["name"])

        if email is None:
            email = click.prompt("Email", type=str, default=client_defaults["email"])
            try:
                validate_email(None, None, email)
            except click.BadParameter as e:
                click.echo(f"Erreur : {e}")
                return

        if phone is None:
            phone = click.prompt("Téléphone", type=str, default=client_defaults["phone"])
            try:
                validate_phone(None, None, phone)
            except click.BadParameter as e:
                click.echo(f"Erreur : {e}")
                return

        if company is None:
            company = click.prompt("Entreprise", type=str, default=client_defaults["company"])

        result = update_client(client_id, name, email, phone, company)
        click.echo(result)

    except Exception as e:
        click.echo(f"Erreur lors de la mise à jour : {e}")


@click.command("delete")
def delete_client_cmd():
    """
    Commande pour supprimer un client existant.
    """
    try:
        # Affiche la liste des clients
        clients_data = list_clients()

        lines = [f"[{c['id']}] | {c['name']} | {c['email']} | "
                 f"{c['phone']} | {c['company']} | "
                 f"Commercial : {c['sales_contact_name']} | "
                 f"Créé le : {c['created_date']} | Modifié le : {c['updated_date']}"
                 for c in clients_data.values()]
        message = "\n".join(lines)
        click.echo(message)

        # Demande l'ID après affichage
        client_id = click.prompt("ID du client à supprimer", type=int)

        if client_id not in clients_data:
            click.echo("Client non trouvé.")
            return

        client_name = clients_data[client_id]["name"]

        if not click.confirm(f"Êtes-vous sûr de vouloir supprimer le client '{client_name}' ? Cette action est irréversible."):
            click.echo("Suppression annulée.")
            return

        result = delete_client(client_id)
        click.echo(result)

    except Exception as e:
        click.echo(f"Erreur lors de la suppression : {e}")


# Ajout des sous-commandes au groupe principal
client_cli.add_command(create_client_cmd)
client_cli.add_command(list_clients_cmd)
client_cli.add_command(update_client_cmd)
client_cli.add_command(delete_client_cmd)