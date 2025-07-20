from sqlalchemy.orm import sessionmaker
from models import Contract, Client
from connection import engine
from auth import get_current_user
from auth_utils import require_role

session = sessionmaker(bind=engine)()

@require_role("commercial", "gestion")
def create_contract():
    user = get_current_user()

    client_id = input("ID du client : ")
    amount_total = float(input("Montant total : "))
    amount_remaining = float(input("Montant restant : "))

    contract = Contract(
        client_id=client_id,
        sales_contact_id=user.id,
        amount_total=amount_total,
        amount_remaining=amount_remaining,
        signed=False
    )
    session.add(contract)
    session.commit()
    print("Contrat créé avec succès.")

@require_role("commercial", "gestion")
def update_contract():
    contract_id = input("ID du contrat : ")
    contract = session.query(Contract).filter_by(id=contract_id).first()

    if not contract:
        print("Contrat introuvable.")
        return

    current_user = get_current_user()
    if current_user.role == "commercial" and contract.sales_contact_id != current_user.id:
        print("Vous ne pouvez modifier que vos propres contrats.")
        return

    contract.amount_total = float(input(f"Montant total [{contract.amount_total}] : ") or contract.amount_total)
    contract.amount_remaining = float(input(f"Montant restant [{contract.amount_remaining}] : ") or contract.amount_remaining)
    signed_input = input("Contrat signé ? (oui/non) : ").strip().lower()
    if signed_input in ["oui", "yes"]:
        contract.signed = True
    elif signed_input in ["non", "no"]:
        contract.signed = False

    session.commit()
    print("Contrat mis à jour.")

@require_role("commercial", "gestion", "support")
def list_contracts():
    current_user = get_current_user()
    contracts = session.query(Contract).all()

    for c in contracts:
        print(f"[{c.id}] Client ID: {c.client_id}, Montant: {c.amount_total}, Restant: {c.amount_remaining}, Signé: {c.signed}")

@require_role("commercial")
def list_unsigned_contracts():
    contracts = session.query(Contract).filter_by(signed=False).all()
    for c in contracts:
        print(f"[{c.id}] Client ID: {c.client_id}, Montant: {c.amount_total}, Restant: {c.amount_remaining}")
