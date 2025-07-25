from sqlalchemy.orm import sessionmaker
from models.models import Contract
from utils.connection import engine
from utils.auth import get_current_user
from utils.auth_utils import require_role
import datetime
import click

session = sessionmaker(bind=engine)()

def create_contract(client_id, amount_total, amount_remaining):
    """Créer un contrat"""
    user = get_current_user()

    contract = Contract(
        client_id=client_id,
        sales_contact_id=user.id,
        amount_total=amount_total,
        amount_remaining=amount_remaining,
        signed=False
    )
    session.add(contract)
    session.commit()
    click.echo("Contrat créé avec succès.")

@require_role("commercial", "gestion")
@click.option('--contract-id', required=True, type=int, help="ID du contrat")
@click.option('--amount-total', type=float, help="Montant total (optionnel)")
@click.option('--amount-remaining', type=float, help="Montant restant (optionnel)")
@click.option('--signed', type=click.Choice(['oui', 'non'], case_sensitive=False), help="Contrat signé ? (oui/non)")
def update_contract(contract_id, amount_total, amount_remaining, signed):
    """Mettre à jour un contrat"""
    contract = session.query(Contract).filter_by(id=contract_id).first()

    if not contract:
        click.echo("Contrat introuvable.")
        return

    current_user = get_current_user()
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
    click.echo("Contrat mis à jour.")

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
