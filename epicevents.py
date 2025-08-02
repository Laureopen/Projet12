import click
from utils.auth import login, create_user

# Clients
from controllers.client_controller import (
    create_client,
    list_clients,
    update_client
)

# Contrats
from controllers.contract_controller import (
    create_contract,
    update_contract,
    list_contracts,
    list_unsigned_contracts
)

# Événements
from controllers.event_controller import (
    create_event,
    assign_support,
    update_my_event,
    list_events,
    list_unassigned_events,
    list_my_events
)


@click.group()
def cli():
    """Application CRM Epic Events"""
    pass


# --- Authentification ---
@cli.command()
def login_cmd():
    """Se connecter"""
    login()


@cli.command()
def create_user_cmd():
    """Créer un utilisateur"""
    create_user()


# --- Clients ---
@cli.group()
def client():
    """Gestion des clients"""
    pass


client.add_command(create_client)
client.add_command(list_clients)
client.add_command(update_client)


# --- Contrats ---
@cli.group()
def contract():
    """Gestion des contrats"""
    pass


contract.add_command(create_contract)
contract.add_command(update_contract)


@contract.command("list")
def list_contracts_cmd():
    """Lister tous les contrats"""
    list_contracts()


@contract.command("unsigned")
def list_unsigned_contracts_cmd():
    """Lister les contrats non signés"""
    list_unsigned_contracts()


# --- Événements ---
@cli.group()
def event():
    """Gestion des événements"""
    pass


event.add_command(create_event, name="create")
event.add_command(assign_support, name="assign-support")
event.add_command(update_my_event, name="update-my-event")


@event.command("list")
def list_events_cmd():
    """Lister tous les événements"""
    list_events()


@event.command("list-unassigned")
def list_unassigned_events_cmd():
    """Lister les événements sans support assigné"""
    list_unassigned_events()


@event.command("list-my-events")
def list_my_events_cmd():
    """Lister mes événements assignés"""
    list_my_events()


if __name__ == "__main__":
    cli()
