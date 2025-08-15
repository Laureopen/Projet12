import click
import re
from sqlalchemy.orm import sessionmaker
from models.client import Client
from utils import auth
from utils.connection import engine
from utils.auth import get_current_user
from utils.auth_utils import require_role

# Création d'une session SQLAlchemy pour interagir avec la base de données
session = sessionmaker(bind=engine)()


def validate_email(ctx, param, value):
    """
    Valide le format d'une adresse email.

    Args:
        ctx: Contexte Click (non utilisé directement, mais requis par Click).
        param: Paramètre CLI lié (non utilisé directement).
        value (str): Adresse email à valider.

    Returns:
        str: L'adresse email validée.

    Raises:
        click.BadParameter: Si le format de l'email est invalide.
    """
    pattern = r"^[^@]+@[^@]+\.[^@]+$"  # Expression régulière simple pour un email basique
    if not re.match(pattern, value):
        raise click.BadParameter("Format d'email invalide.")
    return value


def validate_phone(ctx, param, value):
    """
    Valide le format d'un numéro de téléphone.

    Args:
        ctx: Contexte Click (non utilisé directement).
        param: Paramètre CLI lié (non utilisé directement).
        value (str): Numéro de téléphone à valider.

    Returns:
        str: Le numéro de téléphone validé.

    Raises:
        click.BadParameter: Si le format du téléphone est invalide.
    """
    pattern = r"^\+?\d{10,15}$"  # Accepte un '+' optionnel suivi de 10 à 15 chiffres
    if not re.match(pattern, value):
        raise click.BadParameter(
            "Numéro de téléphone invalide. Entrez entre 10 et 15 chiffres, avec éventuellement un '+'."
        )
    return value


@require_role("commercial")
def create_client(name, email, phone, company):
    """
    Crée un nouveau client et l'associe au commercial connecté.

    Args:
        name (str): Nom du client.
        email (str): Adresse email.
        phone (str): Numéro de téléphone.
        company (str): Nom de l'entreprise.

    Notes:
        - Le client est automatiquement assigné au commercial actuellement connecté.
    """
    user = get_current_user()  # Récupération du commercial connecté

    # Création de l'objet Client
    client = Client(
        name=name,
        email=email,
        phone=phone,
        company=company,
        sales_contact_id=user.id
    )

    # Enregistrement en base
    session.add(client)
    session.commit()
    click.echo("Client créé avec succès.")


@require_role("commercial", "gestion", "support")
def list_clients():
    """
    Affiche la liste des clients enregistrés avec leurs informations :
    - ID
    - Nom
    - Email
    - Téléphone
    - Entreprise
    - Commercial assigné
    - Dates de création et de mise à jour
    """
    clients = session.query(Client).all()

    if not clients:
        click.echo("Aucun client trouvé.")
        return

    click.echo("Liste des clients :\n")

    for c in clients:
        # Formatage des dates ou affichage "Date inconnue"
        created_at_str = c.created_date.strftime("%d %B %Y") if c.created_date else "Date inconnue"
        updated_at_str = c.updated_date.strftime("%d %B %Y") if c.updated_date else "Date inconnue"
        sales_contact_name = c.sales_contact.name if c.sales_contact else "Aucun commercial assigné"

        click.echo(
            f"[{c.id}] Nom: {c.name} ({c.email}) | Téléphone: {c.phone} | "
            f"Entreprise: {c.company} | Commercial: {sales_contact_name} | "
            f"Créé le: {created_at_str} | Dernière MAJ: {updated_at_str}"
        )


@require_role("commercial")
def update_client(client_id, name, email, phone, company, db_session=None, current_user=None):
    """
    Met à jour les informations d'un client existant.

    Args:
        client_id (int): ID du client à mettre à jour.
        name (str | None): Nouveau nom (ou None pour garder l'existant).
        email (str | None): Nouvel email (ou None pour garder l'existant).
        phone (str | None): Nouveau téléphone (ou None pour garder l'existant).
        company (str | None): Nouvelle entreprise (ou None pour garder l'existant).
        session (Session | None): Session SQLAlchemy à utiliser pour la mise à jour.
            Si None, la session globale (prod) sera utilisée.

    Notes:
        - Un commercial ne peut mettre à jour que ses propres clients.
        - Les champs non fournis sont demandés en mode interactif avec Click.
    """

    session = db_session if db_session is not None else auth.session

    client = session.query(Client).filter_by(id=client_id).first()

    if not client:
        click.echo("Client non trouvé.")
        return

    # Saisie interactive si valeurs non fournies
    name = name or click.prompt("Nom", default=client.name)
    email = email or click.prompt("Email", default=client.email)
    phone = phone or click.prompt("Téléphone", default=client.phone)
    company = company or click.prompt("Entreprise", default=client.company)

    current_user = current_user or get_current_user()

    # Vérification : un commercial ne peut modifier que ses propres clients
    if client.sales_contact_id != current_user.id:
        click.echo("Vous ne pouvez modifier que vos propres clients.")
        return

    # Validation email et téléphone
    try:
        email = validate_email(None, None, email)
        phone = validate_phone(None, None, phone)
    except click.BadParameter as e:
        click.echo(f"Erreur : {e}")
        return

    # Mise à jour des champs
    client.name = name
    client.email = email
    client.phone = phone
    client.company = company

    session.commit()
    click.echo("Client mis à jour avec succès.")
