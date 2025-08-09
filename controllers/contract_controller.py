from sqlalchemy.orm import sessionmaker
from models.contract import Contract
from models.client import Client
from utils.connection import engine
from utils.auth import get_current_user, get_user_role
from utils.auth_utils import require_role
import datetime
import click

session = sessionmaker(bind=engine)()

def validate_client_id(ctx, param, value):
    """
       Valide que l'ID client fourni correspond à un client existant.

       Args:
           ctx (click.Context): Contexte Click.
           param (click.Parameter): Paramètre Click.
           value (int): ID du client.

       Returns:
           int: L'ID validé du client.

       Raises:
           click.BadParameter: Si aucun client avec cet ID n'existe.
       """
    client = session.query(Client).filter_by(id=value).first()
    if not client:
        raise click.BadParameter(f"Aucun client trouvé avec l'ID {value}.")
    return value


def create_contract(client_id, amount_total, amount_remaining, signed):
    """
       Crée un contrat pour un client donné (mode interactif avec Click).

       Args:
           client_id (int): ID du client concerné.
           amount_total (float): Montant total du contrat.
           amount_remaining (float): Montant restant à payer.
           signed (str): Statut de signature ('oui' ou 'non').

       Access:
           Rôles requis : commercial, gestion

       Effets:
           Enregistre le contrat dans la base de données avec la date de signature si applicable.
       """
    user = get_current_user()

    contract = Contract(
        client_id=client_id,
        sales_contact_id=user.id,
        amount_total=amount_total,
        amount_remaining=amount_remaining,
        signed=(signed.lower() == "oui"),
        signed_date = datetime.datetime.now() if signed.lower() == "oui" else None
    )

    session.add(contract)
    session.commit()
    click.echo(" Contrat créé avec succès.")


def update_contract(contract_id, amount_total, amount_remaining, signed):
    """
      Met à jour les informations d'un contrat existant.

      Args:
          contract_id (int): ID du contrat à modifier.
          amount_total (float, optional): Nouveau montant total.
          amount_remaining (float, optional): Nouveau montant restant.
          signed (str, optional): Statut de signature ('oui' ou 'non').

      Access:
          Rôles requis : commercial, gestion

      Effets:
          Modifie le contrat si l'utilisateur a les droits. Met à jour la date de signature si applicable.
      """
    contract = session.query(Contract).filter_by(id=contract_id).first()

    if not contract:
        click.echo("Contrat introuvable.")
        return

    current_user = get_current_user()

    if not hasattr(current_user, "department") or not hasattr(current_user, "id"):
        click.echo("Erreur : utilisateur invalide (rôle ou ID manquant).")
        return

    if get_user_role(current_user) == "commercial" and contract.sales_contact_id != current_user.id:
        click.echo("Vous ne pouvez modifier que vos propres contrats.")
        return

    # Saisie interactive si valeurs non fournies
    if amount_total is None:
        amount_total = click.prompt("Montant total", default=contract.amount_total, type=float)
    if amount_remaining is None:
        amount_remaining = click.prompt("Montant restant", default=contract.amount_remaining, type=float)
    if signed is None:
        signed = click.prompt("Contrat signé ? (oui/non)", default="oui" if contract.signed else "non")

    # Mise à jour
    contract.amount_total = amount_total
    contract.amount_remaining = amount_remaining
    if signed.lower() == "oui":
        contract.signed = True
        contract.signed_date = datetime.datetime.now()
    else:
        contract.signed = False
        contract.signed_date = None

    session.commit()
    click.echo("Contrat mis à jour avec succès.")


@require_role("commercial", "gestion", "support")
def list_contracts():
    """
       Affiche la liste de tous les contrats.

       Access:
           Rôles requis : commercial, gestion, support

       Effets:
           Affiche les informations principales de chaque contrat existant.
       """
    contracts = session.query(Contract).all()

    for c in contracts:
        click.echo(f"[{c.id}] Client ID: {c.client_id}, Montant: {c.amount_total}, Restant: {c.amount_remaining}, Signé: {c.signed}")


@require_role("commercial")
def list_unsigned_contracts():
    """
      Affiche la liste des contrats non signés.

      Access:
          Rôle requis : commercial

      Effets:
          Affiche les contrats dont le champ `signed` est à False.
      """
    contracts = session.query(Contract).filter_by(signed=False).all()
    for c in contracts:
        click.echo(f"[{c.id}] Client ID: {c.client_id}, Montant: {c.amount_total}, Restant: {c.amount_remaining}")