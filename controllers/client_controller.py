import click
from sqlalchemy.orm import sessionmaker
from models.models import Client
from utils.connection import engine
from utils.auth import get_current_user
from utils.auth_utils import require_role

session = sessionmaker(bind=engine)()

@click.command()
@click.option('--name', prompt="Nom du client")
@click.option('--email', prompt="Email")
@click.option('--phone', prompt="Téléphone")
@click.option('--company', prompt="Entreprise")
@require_role("commercial")
def create_client():
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
    print("Client créé avec succès.")


@require_role("commercial")
def list_clients():
    clients = session.query(Client).all()
    if not clients:
        print("Aucun client trouvé.")
        return
    print("Liste des clients :")
    for c in clients:
        print(f"ID: {c.id}, Nom: {c.name}, Email: {c.email}, Téléphone: {c.phone}, Entreprise: {c.company}")

@require_role("commercial")
def update_client():
    client_id = input("ID du client à modifier : ")
    client = session.query(Client).filter_by(id=client_id).first()

    if not client:
        print("Client non trouvé.")
        return

    print(f"Modification du client {client.name} (ID: {client.id})")
    name = input(f"Nom [{client.name}]: ") or client.name
    email = input(f"Email [{client.email}]: ") or client.email
    phone = input(f"Téléphone [{client.phone}]: ") or client.phone
    company = input(f"Entreprise [{client.company}]: ") or client.company

    client.name = name
    client.email = email
    client.phone = phone
    client.company = company

    session.commit()
    print("Client mis à jour avec succès.")