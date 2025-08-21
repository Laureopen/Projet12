from sqlalchemy.orm import sessionmaker
from models.contract import Contract
from models.client import Client
from models.event import Event
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
    return "Contrat créé avec succès."


@require_role("commercial", "gestion")
def update_contract(contract_id, amount_total, amount_remaining, signed, db_session=None, current_user=None):
    """
    Met à jour les informations d'un contrat existant.

    Args:
        contract_id (int): ID du contrat à mettre à jour.
        amount_total (float | None): Nouveau montant total (ou None pour conserver l'existant).
        amount_remaining (float | None): Nouveau montant restant (ou None pour conserver l'existant).
        signed (str | None): "oui" ou "non" (ou None pour conserver l'existant).
        db_session (Session | None): auth.session ou session de test
        current_user (User | None): utilisateur de la session ou de test

    Notes:
        - Un commercial ne peut mettre à jour que ses propres contrats.
    """
    session = db_session or auth.session
    contract = session.query(Contract).filter_by(id=contract_id).first()
    if not contract:
        raise Exception("Contrat introuvable.")

    current_user = current_user or get_current_user()

    # Vérification que l'utilisateur a bien les attributs nécessaires
    if not hasattr(current_user, "department") or not hasattr(current_user, "id"):
        raise Exception("Erreur : utilisateur invalide (rôle ou ID manquant).")

    # Un commercial ne peut modifier que ses propres contrats
    if get_user_role(current_user) == "commercial" and contract.sales_contact_id != current_user.id:
        raise Exception("Vous ne pouvez modifier que vos propres contrats.")

    # Mise à jour des champs
    if amount_total is not None:
        contract.amount_total = amount_total
    if amount_remaining is not None:
        contract.amount_remaining = amount_remaining
    if signed is not None:
        if signed.lower() == "oui":
            contract.signed = True
            contract.signed_date = datetime.datetime.now()
        else:
            contract.signed = False
            contract.signed_date = None

    session.commit()
    return "Contrat mis à jour avec succès."


@require_role("commercial", "gestion", "support")
def list_contracts():
    """
    Retourne la liste de tous les contrats sous forme de dictionnaire.
    """
    try:
        contracts = (
            session.query(Contract, Client, User)
            .join(Client, Contract.client_id == Client.id)
            .join(User, Contract.sales_contact_id == User.id)
            .all()
        )

        if not contracts:
            raise Exception("Aucun contrat trouvé.")

        contracts_dict = {}
        for contract, client, commercial in contracts:
            contracts_dict[contract.id] = {
                "id": contract.id,
                "client_name": client.name,
                "client_email": client.email,
                "commercial_name": commercial.name,
                "amount_total": contract.amount_total,
                "amount_remaining": contract.amount_remaining,
                "created_date": contract.created_date.strftime('%Y-%m-%d'),
                "signed": contract.signed
            }

        return contracts_dict

    except Exception as e:
        raise Exception(f"Erreur lors de la récupération des contrats : {e}")


@require_role("commercial", "gestion")
def list_unsigned_contracts():
    """
    Retourne la liste des contrats non signés sous forme de dictionnaire.
    """
    try:
        contracts = (
            session.query(Contract, Client, User)
            .join(Client, Contract.client_id == Client.id)
            .join(User, Contract.sales_contact_id == User.id)
            .filter(Contract.signed.is_(False))
            .all()
        )

        if not contracts:
            raise Exception("Aucun contrat non signé trouvé.")

        contracts_dict = {}
        for contract, client, commercial in contracts:
            contracts_dict[contract.id] = {
                "id": contract.id,
                "client_name": client.name,
                "client_email": client.email,
                "commercial_name": commercial.name,
                "amount_total": contract.amount_total,
                "amount_remaining": contract.amount_remaining,
                "created_date": contract.created_date.strftime('%Y-%m-%d'),
                "signed": contract.signed
            }

        return contracts_dict

    except Exception as e:
        raise Exception(f"Erreur lors de la récupération des contrats non signés : {e}")


@require_role("commercial", "gestion")
def delete_contract(contract_id, db_session=None):
    """
    Supprime un contrat uniquement si aucun événement n'y est lié.

    Args:
        contract_id (int): ID du contrat à supprimer.
        db_session: Session SQLAlchemy optionnelle (sinon session globale utilisée).

    Returns:
        dict: Message de succès.

    Raises:
        Exception: Si le contrat n'existe pas ou si des événements y sont liés.
    """
    session = db_session or auth.session

    contract = session.query(Contract).filter_by(id=contract_id).first()
    if not contract:
        raise Exception("Contrat introuvable.")

    # Vérifier si un événement est lié à ce contrat
    event_linked = session.query(Event).filter_by(contract_id=contract_id).first()
    if event_linked:
        raise Exception("Impossible de supprimer ce contrat car des événements y sont liés.")

    session.delete(contract)
    session.commit()
    return "Contrat supprimé avec succès."
