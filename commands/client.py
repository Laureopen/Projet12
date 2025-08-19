import click

# Import des fonctions liées aux clients
from controllers.client_controller import (
    create_client,
    list_clients,
    update_client,
    validate_email,
    validate_phone
)


@click.group()
def client_cli():
    """
   Commandes liées à la gestion des clients.

    Ce groupe permet de regrouper plusieurs sous-commandes :
    - create : créer un nouveau client
    - list : lister les clients existants
    - update : modifier un client existant
    """
    pass


@click.command("create")
@click.option('--name', prompt="Nom du client")
@click.option('--email', prompt="Email", callback=validate_email)
@click.option('--phone', prompt="Téléphone", callback=validate_phone)
@click.option('--company', prompt="Entreprise")
def create_client_cmd(name, email, phone, company):
    """
    Commande pour créer un nouveau client.

    Args:
        name (str): Nom complet du client.
        email (str): Adresse email valide du client (validation via `validate_email`).
        phone (str): Numéro de téléphone valide (validation via `validate_phone`).
        company (str): Nom de l'entreprise associée au client.
    """
    create_client(name, email, phone, company)


@click.command("list")
def list_clients_cmd():
    """
    Commande pour afficher la liste de tous les clients.
    """
    list_clients()


@click.command("update")
@click.option('--client-id', default=None, help="ID du client à modifier")
@click.option('--name', default=None, help="Nom du client (laisser vide pour conserver l'actuel)")
@click.option('--email', default=None, help="Email du client")
@click.option('--phone', default=None, help="Téléphone du client")
@click.option('--company', default=None, help="Entreprise du client")
def update_client_cmd(client_id, name, email, phone, company):
    """
    Commande pour mettre à jour les informations d'un client existant.

    Args:
        client_id (int, optional): Identifiant du client à modifier.
                                   Si non fourni, l'utilisateur devra le sélectionner après affichage de la liste.
        name (str, optional): Nouveau nom du client.
        email (str, optional): Nouvel email du client.
        phone (str, optional): Nouveau numéro de téléphone du client.
        company (str, optional): Nouvelle entreprise du client.
    """
    if client_id is None:
        # Affiche la liste des clients pour permettre à l'utilisateur de choisir l'ID
        list_clients()
        client_id = click.prompt("\n\nID du client à modifier", type=int)

    update_client(client_id, name, email, phone, company)


# Ajout des sous-commandes au groupe principal
client_cli.add_command(create_client_cmd)
client_cli.add_command(list_clients_cmd)
client_cli.add_command(update_client_cmd)