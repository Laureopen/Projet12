# Commandes contrats
import click

from controllers.contract_controller import (
    create_contract,
    update_contract,
    list_contracts,
    list_unsigned_contracts, delete_contract
)
from controllers.client_controller import list_clients


@click.group()
def contract_cli():
    """
     Commandes liées aux contrats.

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
    Utile pour organiser logiquement les commandes lorsqu'il y a plusieurs sous-catégories.
    """
    pass


@click.command("create")
@click.option('--amount-total', type=float, help="Montant total du contrat")
@click.option('--amount-remaining', type=float, help="Montant restant à payer")
@click.option(
    '--signed',
    type=click.Choice(['oui', 'non'], case_sensitive=False),
    help="Statut de signature du contrat"
)
def create_contract_cmd(amount_total, amount_remaining, signed):
    """
    Commande pour créer un nouveau contrat.

    Args:
        amount_total (float): Montant total du contrat.
        amount_remaining (float): Montant restant dû sur le contrat.
        signed (str): Statut de signature ('oui' ou 'non').
    """
    try:
        # Affiche la liste des clients
        clients_data = list_clients()

        lines = [f"{c['id']} | {c['name']} ({c['email']}) | Téléphone: {c['phone']} | "
                 f"Entreprise: {c['company']} | Commercial: {c['sales_contact_name']}"
                 for c in clients_data.values()]
        message = "\n".join(lines)
        click.echo(message)

        client_id = click.prompt("\nID du client", type=int)

        # Validation du client
        if client_id not in clients_data:
            click.echo("Client non trouvé.")
            return

        # Prompts pour les autres champs
        if amount_total is None:
            amount_total = click.prompt("Montant total", type=float)

        if amount_remaining is None:
            amount_remaining = click.prompt("Montant restant", type=float)

        if signed is None:
            signed = click.prompt("Le contrat est-il signé ? (oui/non)",
                                  type=click.Choice(['oui', 'non'], case_sensitive=False),
                                  default="non", show_default=True)

        result = create_contract(client_id, amount_total, amount_remaining, signed)
        click.echo(result)
    except Exception as e:
        click.echo(f"Erreur lors de la création : {e}")


@click.command("update")
@click.option('--amount-total', type=float, default=None,
              help="Nouveau montant total (laisser vide pour conserver l'actuel)")
@click.option('--amount-remaining', type=float, default=None,
              help="Nouveau montant restant (laisser vide pour conserver l'actuel)")
@click.option('--signed', type=click.Choice(['oui', 'non'], case_sensitive=False),
              default=None, help="Statut de signature du contrat ('oui' ou 'non')")
def update_contract_cmd(amount_total, amount_remaining, signed):
    """
    Commande pour mettre à jour un contrat existant.

    Args:
        amount_total (float, optional): Nouveau montant total.
        amount_remaining (float, optional): Nouveau montant restant.
        signed (str, optional): Nouveau statut de signature ('oui' ou 'non').
    """
    try:
        # Affiche la liste des contrats
        contracts_data = list_contracts()

        lines = [
            (
                f"{c['id']} | Client: {c['client_name']} ({c['client_email']}) | "
                f"Commercial: {c['commercial_name']} | Total: {c['amount_total']} | "
                f"Restant: {c['amount_remaining']} | Date: {c['created_date']} | "
                f"Signé: {'Oui' if c['signed'] else 'Non'}"
            )
            for c in contracts_data.values()
        ]

        message = "\n".join(lines)
        click.echo(message)

        contract_id = click.prompt("\nID du contrat à modifier", type=int)

        if contract_id not in contracts_data:
            click.echo("Contrat non trouvé.")
            return

        contract_defaults = contracts_data[contract_id]

        amount_total = click.prompt(
            "Montant total",
            default=contract_defaults["amount_total"],
            type=float
        )

        if amount_remaining is None:
            amount_remaining = click.prompt("Montant restant", default=contract_defaults["amount_remaining"],
                                            type=float)

        if signed is None:
            signed = click.prompt(
                "Contrat signé ? (oui/non)",
                default="oui" if contract_defaults["signed"] else "non")

        result = update_contract(contract_id, amount_total, amount_remaining, signed)
        click.echo(result)

    except Exception as e:
        click.echo(f"Erreur lors de la mise à jour : {e}")


@contract_cli.command("list")
def list_contracts_cmd():
    """
    Commande pour afficher tous les contrats existants.
    """
    try:
        contracts_data = list_contracts()

        lines = [
            (
                f"[{c['id']}] Client: {c['client_name']} ({c['client_email']}) | "
                f"Commercial: {c['commercial_name']} | Montant total: {c['amount_total']} | "
                f"Restant: {c['amount_remaining']} | Date création: {c['created_date']} | "
                f"Signé: {'Oui' if c['signed'] else 'Non'}"
            )
            for c in contracts_data.values()
        ]

        message = "\n".join(lines)
        click.echo(message)

    except Exception as e:
        click.echo(f"Erreur : {e}")


@contract_cli.command("unsigned")
def list_unsigned_contracts_cmd():
    """
    Commande pour afficher uniquement les contrats non signés.
    """
    try:
        contracts_data = list_unsigned_contracts()

        lines = [
            (
                f"[{c['id']}] Client: {c['client_name']} ({c['client_email']}) | "
                f"Commercial: {c['commercial_name']} | Montant total: {c['amount_total']} | "
                f"Restant: {c['amount_remaining']} | Date création: {c['created_date']} | "
                f"Signé: {'Oui' if c['signed'] else 'Non'}"
            )
            for c in contracts_data.values()
        ]

        message = "\n".join(lines)
        click.echo(message)

    except Exception as e:
        click.echo(f"Erreur : {e}")


@click.command("delete")
def delete_contract_cmd():
    """
    Commande pour supprimer un contrat (uniquement si aucun événement lié).
    """
    try:
        # On affiche d'abord les contrats pour aider au choix
        contracts_data = list_contracts()

        lines = [f"[{c['id']}] Client: {c['client_name']} ({c['client_email']}) | "
                 f"Commercial: {c['commercial_name']} | Total: {c['amount_total']} | "
                 f"Restant: {c['amount_remaining']} | Date: {c['created_date']} | "
                 f"Signé: {'Oui' if c['signed'] else 'Non'}"
                 for c in contracts_data.values()]
        message = "\n".join(lines)
        click.echo(message)

        contract_id = click.prompt("\nID du contrat à supprimer", type=int)

        if contract_id not in contracts_data:
            click.echo("Contrat non trouvé.")
            return

        confirm = click.confirm("Voulez-vous vraiment supprimer ce contrat ?", default=False)
        if not confirm:
            click.echo("Suppression annulée.")
            return

        result = delete_contract(contract_id)
        click.echo(result)

    except Exception as e:
        click.echo(f"Erreur : {str(e)}")


# Enregistrement des sous-commandes dans le groupe principal
contract_cli.add_command(create_contract_cmd)
contract_cli.add_command(list_contracts_cmd)
contract_cli.add_command(list_unsigned_contracts_cmd)
contract_cli.add_command(update_contract_cmd)
contract_cli.add_command(delete_contract_cmd)
