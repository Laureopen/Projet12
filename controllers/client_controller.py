import click
import re
from sqlalchemy.orm import sessionmaker
from models.models import Client
from utils.connection import engine
from utils.auth import get_current_user
from utils.auth_utils import require_role

session = sessionmaker(bind=engine)()

#  Validation simple d'email
def validate_email(ctx, param, value):
    pattern = r"^[^@]+@[^@]+\.[^@]+$"
    if not re.match(pattern, value):
        raise click.BadParameter("Format d'email invalide.")
    return value

#  Validation simple de téléphone
def validate_phone(ctx, param, value):
    pattern = r"^\+?\d{10,15}$"  # accepte + suivi de 10 à 15 chiffres
    if not re.match(pattern, value):
        raise click.BadParameter("Numéro de téléphone invalide. Entrez entre 10 et 15 chiffres, avec éventuellement un '+'.")
    return value


@click.command("create")
@click.option('--name', prompt="Nom du client")
@click.option('--email', prompt="Email", callback=validate_email)
@click.option('--phone', prompt="Téléphone", callback=validate_phone)
@click.option('--company', prompt="Entreprise")
@require_role("commercial")
def create_client(name, email, phone, company):
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


@click.command("list")
@require_role("commercial")
def list_clients():
    clients = session.query(Client).all()
    if not clients:
        click.echo("Aucun client trouvé.")
        return
    click.echo("Liste des clients :")
    for c in clients:
        click.echo(f"ID: {c.id}, Nom: {c.name}, Email: {c.email}, Téléphone: {c.phone}, Entreprise: {c.company}")


@click.command("update")
@click.option('--client-id', prompt="ID du client à modifier")
@click.option('--name', default=None, help="Nom du client (laisser vide pour conserver l'actuel)")
@click.option('--email', default=None, help="Email du client")
@click.option('--phone', default=None, help="Téléphone du client")
@click.option('--company', default=None, help="Entreprise du client")
@require_role("commercial")
def update_client(client_id, name, email, phone, company):
    client = session.query(Client).filter_by(id=client_id).first()

    if not client:
        click.echo("Client non trouvé.")
        return

    name = name or click.prompt("Nom", default=client.name)
    email = email or click.prompt("Email", default=client.email)
    phone = phone or click.prompt("Téléphone", default=client.phone)
    company = company or click.prompt("Entreprise", default=client.company)

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
