import click
from auth import login, create_user
from client_controller import create_client, list_clients, update_client
from contract_controller import create_contract, update_contract, list_contracts, list_unsigned_contracts
from event_controller import (
    create_event,
    assign_support,
    update_my_event,
    list_events,
    list_unassigned_events,
    list_my_events,
)

@click.group()
def cli():
    """Application CRM Epic Events"""
    pass

# Authentification
@cli.command()
def login_cmd():
    """Se connecter"""
    login()

@cli.command()
def create_user_cmd():
    """Créer un utilisateur"""
    create_user()

# Clients
@cli.group()
def client():
    """Gestion des clients"""
    pass

@client.command("create")
def create_client_cmd():
    """Créer un client (réservé aux commerciaux)"""
    create_client()

@client.command("list")
def list_clients_cmd():
    """Lister tous les clients"""
    list_clients()

@client.command("update")
def update_client_cmd():
    """Modifier un client"""
    update_client()

# Contrats
@cli.group()
def contract():
    """Gestion des contrats"""
    pass

@contract.command("create")
def create_contract_cmd():
    """Créer un contrat"""
    create_contract()

@contract.command("update")
def update_contract_cmd():
    """Mettre à jour un contrat"""
    update_contract()

@contract.command("list")
def list_contracts_cmd():
    """Lister tous les contrats"""
    list_contracts()

@contract.command("unsigned")
def list_unsigned_contracts_cmd():
    """Lister les contrats non signés"""
    list_unsigned_contracts()

# Événements
@cli.group()
def event():
    """Gestion des événements"""
    pass

@event.command("create")
def create_event_cmd():
    """Créer un événement (commercial uniquement)"""
    create_event()

@event.command("assign-support")
def assign_support_cmd():
    """Assigner un support à un événement (gestion uniquement)"""
    assign_support()

@event.command("update-my-event")
def update_my_event_cmd():
    """Mettre à jour un événement (support uniquement)"""
    update_my_event()

@event.command("list")
def list_events_cmd():
    """Lister tous les événements (tous les rôles)"""
    list_events()

@event.command("list-unassigned")
def list_unassigned_events_cmd():
    """Lister les événements sans support assigné (gestion uniquement)"""
    list_unassigned_events()

@event.command("list-my-events")
def list_my_events_cmd():
    """Lister mes événements assignés (support uniquement)"""
    list_my_events()

if __name__ == "__main__":
    cli()
