import click
from auth import login, create_user
from client_controller import create_client
from contract_controller import create_contract, update_contract, list_contracts, list_unsigned_contracts


@click.group()
def cli():
    """Application CRM Epic Events"""
    pass

@cli.command()
def login_cmd():
    """Se connecter"""
    login()

@cli.command()
def create_user_cmd():
    """Créer un utilisateur"""
    create_user()

@cli.group()
def client():
    """Gestion des clients"""
    pass

@client.command("create")
def create_client_cmd():
    """Créer un client (réservé aux commerciaux)"""
    create_client()

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


if __name__ == "__main__":
    cli()
