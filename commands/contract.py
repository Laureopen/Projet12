# Commandes contrats
import click

from controllers.contract_controller import (
    create_contract,
    update_contract,
    list_contracts,
    list_unsigned_contracts,
    validate_client_id
)


@click.group()
def contract_cli():
    """
    Groupe principal de commandes CLI liées aux contrats.

    Ce groupe regroupe toutes les commandes relatives aux contrats clients :
    - create : créer un contrat
    - update : modifier un contrat existant
    - list : lister tous les contrats
    - unsigned : lister les contrats non signés
    """
    pass


@contract_cli.group()
def contract():
    """
    Sous-groupe CLI pour la gestion des contrats.
    Utile pour organiser logiquement les commandes lorsqu’il y a plusieurs sous-catégories.
    """
    pass


@click.command("create")
@click.option(
    '--client-id',
    type=int,
    prompt="ID du client",
    callback=validate_client_id,
    help="ID du client lié au contrat"
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
def create_contract_cmd(client_id, amount_total, amount_remaining, signed):
    """
    Commande CLI pour créer un nouveau contrat.

    Args:
        client_id (int): Identifiant du client (validation via `validate_client_id`).
        amount_total (float): Montant total du contrat.
        amount_remaining (float): Montant restant dû sur le contrat.
        signed (str): Statut de signature ('oui' ou 'non').
    """
    create_contract(client_id, amount_total, amount_remaining, signed)


@click.command("update")
@click.option('--amount-total', type=float, default=None,
              help="Nouveau montant total (laisser vide pour conserver l'actuel)")
@click.option('--amount-remaining', type=float, default=None,
              help="Nouveau montant restant (laisser vide pour conserver l'actuel)")
@click.option('--signed', type=click.Choice(['oui', 'non'], case_sensitive=False),
              default=None, help="Statut de signature du contrat ('oui' ou 'non')")
def update_contract_cmd(amount_total, amount_remaining, signed):
    """
    Commande CLI pour mettre à jour un contrat existant.

    Args:
        amount_total (float, optional): Nouveau montant total.
        amount_remaining (float, optional): Nouveau montant restant.
        signed (str, optional): Nouveau statut de signature ('oui' ou 'non').
    """
    # Affiche la liste des contrats pour que l'utilisateur choisisse l'ID
    list_contracts()
    contract_id = click.prompt("\n\nID du contrat à modifier", type=int)

    update_contract(contract_id, amount_total, amount_remaining, signed)


@contract_cli.command("list")
def list_contracts_cmd():
    """
    Commande CLI pour afficher tous les contrats existants.
    """
    list_contracts()


@contract_cli.command("unsigned")
def list_unsigned_contracts_cmd():
    """
    Commande CLI pour afficher uniquement les contrats non signés.
    """
    list_unsigned_contracts()


# Enregistrement des sous-commandes dans le groupe principal
contract_cli.add_command(create_contract_cmd)
contract_cli.add_command(list_contracts_cmd)
contract_cli.add_command(list_unsigned_contracts_cmd)
contract_cli.add_command(update_contract_cmd)
