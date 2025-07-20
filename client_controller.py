from sqlalchemy.orm import sessionmaker
from models import Client
from connection import engine
from auth import get_current_user
from auth_utils import require_role

session = sessionmaker(bind=engine)()

@require_role("commercial")
def create_client():
    user = get_current_user()

    name = input("Nom du client : ")
    email = input("Email : ")
    phone = input("Téléphone : ")
    company = input("Entreprise : ")

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
