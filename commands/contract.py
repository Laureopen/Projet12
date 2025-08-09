# Commandes contrats
import click

from controllers.contract_controller import (
    create_contract,
    update_contract,
    list_contracts,
    list_unsigned_contracts, validate_client_id
)
from utils.auth_utils import require_role


@click.group()
def contract_cli():
    """Commandes liées aux contracts"""
    pass


@contract_cli.group()
def contract():
    """Gestion des contrats"""
    pass


@click.command("create")
@click.option(
    '--client-id',
    type=int,
    prompt="ID du client",
    callback=validate_client_id,
    help="ID du client"
)
@click.option('--amount-total', type=float, prompt="Montant total", help="Montant total du contrat")
@click.option('--amount-remaining', type=float, prompt="Montant restant", help="Montant restant à payer")
@click.option(
    '--signed',
    type=click.Choice(['oui', 'non'], case_sensitive=False),
    prompt="Le contrat est-il signé ? (oui/non)",
    default="non",
    show_default=True,
    help="Statut de signature du contrat"
)
@require_role("commercial", "gestion")
def create_contract_cmd(client_id, amount_total, amount_remaining, signed):
    """Créer un contrat"""
    create_contract(client_id, amount_total, amount_remaining, signed)


@click.command("update")
@click.option('--contract-id', type=int, prompt="ID du contrat à modifier", help="ID du contrat")
@click.option('--amount-total', type=float, default=None, help="Montant total (laisser vide pour conserver l'actuel)")
@click.option('--amount-remaining', type=float, default=None,
              help="Montant restant (laisser vide pour conserver l'actuel)")
@click.option('--signed', type=click.Choice(['oui', 'non'], case_sensitive=False), default=None,
              help="Contrat signé ? (oui/non)")
@require_role("commercial", "gestion")
def update_contract_cmd(contract_id, amount_total, amount_remaining, signed):
    update_contract(contract_id, amount_total, amount_remaining, signed)


@contract_cli.command("list")
def list_contracts_cmd():
    """Lister tous les contrats"""
    list_contracts()


@contract_cli.command("unsigned")
def list_unsigned_contracts_cmd():
    """Lister les contrats non signés"""
    list_unsigned_contracts()


contract_cli.add_command(create_contract_cmd)
contract_cli.add_command(list_contracts_cmd)
contract_cli.add_command(list_unsigned_contracts_cmd)
contract_cli.add_command(update_contract_cmd)
