from utils.auth_utils import require_role

import click

# Clients
from controllers.client_controller import (
    create_client,
    list_clients,
    update_client,
    validate_email,
    validate_phone
)


@click.group()
def client_cli():
    """Commandes liées aux clients"""
    pass


@click.command("create")
@click.option('--name', prompt="Nom du client")
@click.option('--email', prompt="Email", callback=validate_email)
@click.option('--phone', prompt="Téléphone", callback=validate_phone)
@click.option('--company', prompt="Entreprise")
@require_role("commercial")
def create_client_cmd(name, email, phone, company):
    create_client(name, email, phone, company)


@click.command("list")
@require_role("commercial")
def list_clients_cmd():
    list_clients()


@click.command("update")
@click.option('--client-id', default=None, help="ID du client à modifier")
@click.option('--name', default=None, help="Nom du client (laisser vide pour conserver l'actuel)")
@click.option('--email', default=None, help="Email du client")
@click.option('--phone', default=None, help="Téléphone du client")
@click.option('--company', default=None, help="Entreprise du client")
@require_role("commercial")
def update_client_cmd(client_id, name, email, phone, company):
    if client_id is None:
        # Affiche la liste des clients avant de demander l'ID
        list_clients()  # Ta fonction qui liste les clients, qui fait click.echo
        client_id = click.prompt("\n\nID du client à modifier", type=int)

    update_client(client_id, name, email, phone, company)


client_cli.add_command(create_client_cmd)
client_cli.add_command(list_clients_cmd)
client_cli.add_command(update_client_cmd)