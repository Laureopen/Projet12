from sqlalchemy.orm import sessionmaker
from models.models import Contract
from utils.connection import engine
from utils.auth import get_current_user
from utils.auth_utils import require_role
import datetime
import click

session = sessionmaker(bind=engine)()

@click.command("create")
@click.option('--client-id', type=int, prompt="ID du client", help="ID du client")
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
def create_contract(client_id, amount_total, amount_remaining, signed):
    """Créer un contrat (mode interactif avec Click)"""
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

@click.command("update")
@click.option('--contract-id', type=int, prompt="ID du contrat à modifier", help="ID du contrat")
@click.option('--amount-total', type=float, default=None, help="Montant total (optionnel)")
@click.option('--amount-remaining', type=float, default=None, help="Montant restant (optionnel)")
@click.option('--signed', type=click.Choice(['oui', 'non'], case_sensitive=False), default=None, help="Contrat signé ? (oui/non)")
@require_role("commercial", "gestion")
def update_contract(contract_id, amount_total, amount_remaining, signed):
    """Mettre à jour un contrat"""
    contract = session.query(Contract).filter_by(id=contract_id).first()

    if not contract:
        click.echo("Contrat introuvable.")
        return

    current_user = get_current_user()

    # Sécurité : vérifier que current_user a bien les attributs nécessaires
    if not hasattr(current_user, "role") or not hasattr(current_user, "id"):
        click.echo("Erreur : utilisateur invalide (role ou id manquant).")
        return

    if current_user.role == "commercial" and contract.sales_contact_id != current_user.id:
        click.echo("Vous ne pouvez modifier que vos propres contrats.")
        return

    if amount_total is not None:
        contract.amount_total = amount_total
    if amount_remaining is not None:
        contract.amount_remaining = amount_remaining
    if signed:
        if signed.lower() == "oui":
            contract.signed = True
            contract.signed_date = datetime.datetime.now()
        elif signed.lower() == "non":
            contract.signed = False
            contract.signed_date = None

    session.commit()
    click.echo(" Contrat mis à jour.")

@require_role("commercial", "gestion", "support")
def list_contracts():
    """Lister les contrats"""
    contracts = session.query(Contract).all()

    for c in contracts:
        click.echo(f"[{c.id}] Client ID: {c.client_id}, Montant: {c.amount_total}, Restant: {c.amount_remaining}, Signé: {c.signed}")

@require_role("commercial")
def list_unsigned_contracts():
    """Lister les contrats non signés"""
    contracts = session.query(Contract).filter_by(signed=False).all()
    for c in contracts:
        click.echo(f"[{c.id}] Client ID: {c.client_id}, Montant: {c.amount_total}, Restant: {c.amount_remaining}")
