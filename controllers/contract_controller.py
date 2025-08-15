from sqlalchemy.orm import sessionmaker
from models.contract import Contract
from models.client import Client
from models.user import User
from utils import auth
from utils.connection import engine
from utils.auth import get_current_user, get_user_role
import datetime
import click
from utils.auth_utils import require_role

# Création d'une session SQLAlchemy pour interagir avec la base de données
session = sessionmaker(bind=engine)()


def validate_client_id(ctx, param, value):
    """
    Valide que l'ID client fourni correspond à un client existant dans la base.

    Args:
        ctx: Contexte Click (non utilisé ici, mais requis par la signature d'une callback Click).
        param: Paramètre CLI lié (non utilisé directement ici).
        value (int): ID du client à valider.

    Returns:
        int: L'ID client validé.

    Raises:
        click.BadParameter: Si aucun client avec cet ID n'existe.
    """
    client = session.query(Client).filter_by(id=value).first()
    if not client:
        raise click.BadParameter(f"Aucun client trouvé avec l'ID {value}.")
    return value


@require_role("commercial", "gestion")
def create_contract(client_id, amount_total, amount_remaining, signed):
    """
    Crée un contrat pour un client donné.

    Args:
        client_id (int): ID du client.
        amount_total (float): Montant total du contrat.
        amount_remaining (float): Montant restant à payer.
        signed (str): "oui" ou "non" selon que le contrat est signé.

    Notes:
        - Le contrat est associé au commercial actuellement connecté.
        - Si le contrat est signé, la date de signature est définie à la date courante.
    """
    user = get_current_user()  # Récupération de l'utilisateur connecté

    contract = Contract(
        client_id=client_id,
        sales_contact_id=user.id,
        amount_total=amount_total,
        amount_remaining=amount_remaining,
        signed=(signed.lower() == "oui"),
        signed_date=datetime.datetime.now() if signed.lower() == "oui" else None
    )

    session.add(contract)
    session.commit()
    click.echo("Contrat créé avec succès.")


@require_role("commercial", "gestion")
def update_contract(contract_id, amount_total, amount_remaining, signed, db_session=None, current_user=None):
    """
    Met à jour les informations d'un contrat existant.

    Args:
        contract_id (int): ID du contrat à mettre à jour.
        amount_total (float | None): Nouveau montant total (ou None pour conserver l'existant).
        amount_remaining (float | None): Nouveau montant restant (ou None pour conserver l'existant).
        signed (str | None): "oui" ou "non" (ou None pour conserver l'existant).

    Notes:
        - Un commercial ne peut mettre à jour que ses propres contrats.
        - Les champs non fournis sont demandés en mode interactif avec Click.
    """
    session = db_session or auth.session
    contract = session.query(Contract).filter_by(id=contract_id).first()
    if not contract:
        click.echo("Contrat introuvable.")
        return

    current_user = current_user or get_current_user()

    # Vérification que l'utilisateur a bien les attributs nécessaires
    if not hasattr(current_user, "department") or not hasattr(current_user, "id"):
        click.echo("Erreur : utilisateur invalide (rôle ou ID manquant).")
        return

    # Un commercial ne peut modifier que ses propres contrats
    if get_user_role(current_user) == "commercial" and contract.sales_contact_id != current_user.id:
        click.echo("Vous ne pouvez modifier que vos propres contrats.")
        return

    # Demande interactive des valeurs si elles ne sont pas fournies
    if amount_total is None:
        amount_total = click.prompt("Montant total", default=contract.amount_total, type=float)
    if amount_remaining is None:
        amount_remaining = click.prompt("Montant restant", default=contract.amount_remaining, type=float)
    if signed is None:
        signed = click.prompt("Contrat signé ? (oui/non)", default="oui" if contract.signed else "non")

    # Mise à jour des champs
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
    Affiche la liste de tous les contrats avec les informations :
    - ID du contrat
    - Nom et email du client
    - Nom du commercial
    - Montant total
    - Montant restant
    - Date de création
    - Statut signé / non signé
    """
    contracts = (
        session.query(Contract, Client, User)
        .join(Client, Contract.client_id == Client.id)
        .join(User, Contract.sales_contact_id == User.id)
        .all()
    )

    for contract, client, commercial in contracts:
        click.echo(
            f"[{contract.id}] "
            f"Client: {client.name} ({client.email}) | "
            f"Commercial: {commercial.name} | "
            f"Montant total: {contract.amount_total} | "
            f"Restant: {contract.amount_remaining} | "
            f"Date création: {contract.created_date.strftime('%Y-%m-%d')} | "
            f"Signé: {'Oui' if contract.signed else 'Non'}"
        )


@require_role("commercial", "gestion")
def list_unsigned_contracts():
    """
    Affiche la liste des contrats non signés avec les informations :
    - ID du contrat
    - Nom et email du client
    - Nom du commercial
    - Montant total
    - Montant restant
    - Date de création
    """
    contracts = (
        session.query(Contract, Client, User)
        .join(Client, Contract.client_id == Client.id)
        .join(User, Contract.sales_contact_id == User.id)
        .filter(Contract.signed.is_(False))
        .all()
    )

    for contract, client, commercial in contracts:
        click.echo(
            f"[{contract.id}] "
            f"Client: {client.name} ({client.email}) | "
            f"Commercial: {commercial.name} | "
            f"Montant total: {contract.amount_total} | "
            f"Restant: {contract.amount_remaining} | "
            f"Date création: {contract.created_date.strftime('%Y-%m-%d')} | "
            f"Signé: {'Oui' if contract.signed else 'Non'}"
        )
