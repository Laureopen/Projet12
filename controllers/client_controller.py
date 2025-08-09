import click
import re
from sqlalchemy.orm import sessionmaker
from models.client import Client
from utils.connection import engine
from utils.auth import get_current_user

session = sessionmaker(bind=engine)()


#  Validation simple d'email
def validate_email(ctx, param, value):
    """
       Valide le format d'une adresse email.

       Args:
           ctx (click.Context): Contexte Click.
           param (click.Parameter): Paramètre Click.
           value (str): Valeur de l'email à valider.

       Returns:
           str: Email validé.

       Raises:
           click.BadParameter: Si le format de l'email est invalide.
       """
    pattern = r"^[^@]+@[^@]+\.[^@]+$"
    if not re.match(pattern, value):
        raise click.BadParameter("Format d'email invalide.")
    return value


#  Validation simple de téléphone
def validate_phone(ctx, param, value):
    """
       Valide le format d'un numéro de téléphone.

       Args:
           ctx (click.Context): Contexte Click.
           param (click.Parameter): Paramètre Click.
           value (str): Numéro de téléphone à valider.

       Returns:
           str: Numéro validé.

       Raises:
           click.BadParameter: Si le numéro est invalide (non conforme à 10-15 chiffres avec ou sans '+').
       """
    pattern = r"^\+?\d{10,15}$"  # accepte + suivi de 10 à 15 chiffres
    if not re.match(pattern, value):
        raise click.BadParameter(
            "Numéro de téléphone invalide. Entrez entre 10 et 15 chiffres, avec éventuellement un '+'.")
    return value


def create_client(name, email, phone, company):
    """
      Crée un nouveau client dans la base de données.

      Args:
          name (str): Nom du client.
          email (str): Adresse email validée du client.
          phone (str): Numéro de téléphone validé du client.
          company (str): Nom de l'entreprise du client.

      Access:
          Rôle requis : commercial

      Effets:
          Ajoute un client à la base et affiche un message de confirmation.
      """
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


def list_clients():
    """
       Affiche la liste des clients enregistrés.

       Access:
           Rôle requis : commercial

       Effets:
           Affiche les détails de chaque client ou un message si aucun client n'est trouvé.
       """
    clients = session.query(Client).all()
    if not clients:
        click.echo("Aucun client trouvé.")
        return
    click.echo("Liste des clients :")
    for c in clients:
        click.echo(f"ID: {c.id}, Nom: {c.name}, Email: {c.email}, Téléphone: {c.phone}, Entreprise: {c.company}")


def update_client(client_id, name, email, phone, company):
    """
       Met à jour les informations d'un client existant.

       Args:
           client_id (int): ID du client à modifier.
           name (str, optional): Nouveau nom. Utilise l'actuel si non fourni.
           email (str, optional): Nouvelle adresse email.
           phone (str, optional): Nouveau téléphone.
           company (str, optional): Nouvelle entreprise.

       Access:
           Rôle requis : commercial

       Effets:
           Met à jour les champs modifiés et affiche un message de confirmation ou d'erreur.
       """
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
