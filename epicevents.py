import click
from commands.client import client_cli
from commands.contract import contract_cli
from commands.event import event_cli
from commands.user import user_cli
from utils.auth import login


@click.group()
def cli():
    """Application CRM Epic Events"""
    pass


@cli.command()
def login_cmd():
    """Se connecter"""
    login()


cli.add_command(user_cli, name="user")
cli.add_command(client_cli, name="client")
cli.add_command(contract_cli, name="contract")
cli.add_command(event_cli, name="event")

if __name__ == "__main__":
    cli()
