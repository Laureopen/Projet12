import click
from sqlalchemy.orm import sessionmaker
from models.models import Client
from utils.connection import engine
from utils.auth import get_current_user
from utils.auth_utils import require_role

session = sessionmaker(bind=engine)()


@click.command("create")
@click.option('--name', prompt="Nom du client")
@click.option('--email', prompt="Email")
@click.option('--phone', prompt="Téléphone")
@click.option('--company', prompt="Entreprise")
@require_role("commercial")
def create_client(name,email,phone,company):
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
    click.echo("Client créé avec succès.")


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

    client.name = name
    client.email = email
    client.phone = phone
    client.company = company

    session.commit()
    click.echo("Client mis à jour avec succès.")