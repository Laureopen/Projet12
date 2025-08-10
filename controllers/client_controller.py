import click
import re
from sqlalchemy.orm import sessionmaker
from models.client import Client
from utils.connection import engine
from utils.auth import get_current_user
from utils.auth_utils import require_role
session = sessionmaker(bind=engine)()


#  Validation simple d'email
def validate_email(ctx, param, value):
    """Valide le format d'une adresse email."""
    pattern = r"^[^@]+@[^@]+\.[^@]+$"
    if not re.match(pattern, value):
        raise click.BadParameter("Format d'email invalide.")
    return value


#  Validation simple de téléphone
def validate_phone(ctx, param, value):
    """Valide le format d'un numéro de téléphone."""
    pattern = r"^\+?\d{10,15}$"  # accepte + suivi de 10 à 15 chiffres
    if not re.match(pattern, value):
        raise click.BadParameter(
            "Numéro de téléphone invalide. Entrez entre 10 et 15 chiffres, avec éventuellement un '+'.")
    return value

@require_role("commercial")
def create_client(name, email, phone, company):
    """Crée un nouveau client dans la base de données."""
    user = get_current_user()
    client = Client(
        name=name,
        email=email,
        phone=phone,
        company=company,
        sales_contact_id=user.id
    )
    session.add(client)
    session.commit()
    click.echo(" Client créé avec succès.")

@require_role("commercial","gestion","support")
def list_clients():
    """Affiche la liste des clients enregistrés."""
    clients = session.query(Client).all()
    if not clients:
        click.echo("Aucun client trouvé.")
        return

    click.echo("Liste des clients :\n")
    for c in clients:
        created_at_str = c.created_date.strftime("%d %B %Y") if c.created_date else "Date inconnue"
        updated_at_str = c.updated_date.strftime("%d %B %Y") if c.updated_date else "Date inconnue"
        sales_contact_name = c.sales_contact.name if c.sales_contact else "Aucun commercial assigné"

        click.echo(
            f"[{c.id}] Nom: {c.name} ({c.email}) | Téléphone: {c.phone} | "
            f"Entreprise: {c.company} | Commercial: {sales_contact_name} | "
            f"Créé le: {created_at_str} | Dernière MAJ: {updated_at_str}"
        )

@require_role("commercial")
def update_client(client_id, name, email, phone, company):
    """Met à jour les informations d'un client existant."""
    client = session.query(Client).filter_by(id=client_id).first()

    if not client:
        click.echo("Client non trouvé.")
        return

    name = name or click.prompt("Nom", default=client.name)
    email = email or click.prompt("Email", default=client.email)
    phone = phone or click.prompt("Téléphone", default=client.phone)
    company = company or click.prompt("Entreprise", default=client.company)

    current_user = get_current_user()

    if client.sales_contact_id != current_user.id:
        click.echo("Vous ne pouvez modifier que vos propres clients.")
        return

    try:
        email = validate_email(None, None, email)
        phone = validate_phone(None, None, phone)
    except click.BadParameter as e:
        click.echo(f"Erreur : {e}")
        return

    client.name = name
    client.email = email
    client.phone = phone
    client.company = company

    session.commit()
    click.echo("Client mis à jour avec succès.")