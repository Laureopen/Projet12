import getpass
import sentry_sdk
import click
from utils.auth_utils import require_role
from sqlalchemy.orm import sessionmaker
from models.department import Department
from models.user import User
from utils.auth import hash_password, get_current_user, get_user_role
from utils.connection import engine

session = sessionmaker(bind=engine)()

@require_role("gestion")
def create_user(name, email):
    password = getpass.getpass("Mot de passe : ")
    # Affiche les départements disponibles
    departments = session.query(Department).all()
    for dept in departments:
        print(f"{dept.id} - {dept.name}")

    # Demande à l'utilisateur de saisir l'ID
    dep_input = input("Département (id) : ").strip()

    # Vérifie que c’est bien un entier et qu’il existe
    try:
        dep_id = int(dep_input)
        department = session.query(Department).get(dep_id)
        if not department:
            print("Département introuvable.")
            return
    except ValueError:
        print("Entrée invalide, veuillez entrer un ID numérique.")
        return

    if session.query(User).filter_by(email=email).first():
        print("Utilisateur déjà existant.")
        return

    hashed = hash_password(password)
    user = User(name=name, email=email, password=hashed,
                department=department)
    session.add(user)
    session.commit()
    sentry_sdk.capture_message(f"Utilisateur créé : {email} par {get_current_user().email}")
    print("Utilisateur créé avec succès.")

@require_role("gestion")
def update_user(email, name, password, department_id):
    """
    Met à jour un utilisateur identifié par son email.
    """
    user = session.query(User).filter_by(email=email).first()
    if not user:
        click.echo("Utilisateur introuvable.")
        return

    current_user = get_current_user()
    if get_user_role(current_user) != "gestion":
        click.echo("Vous n'avez pas les droits pour modifier un utilisateur.")
        return

    if name is None:
        name = click.prompt("Nom complet", default=user.name)
    if password is None:
        password = click.prompt("Mot de passe", hide_input=True, confirmation_prompt=True, default="", show_default=False)
        if password.strip() == "":
            password = None
    if department_id is None:
        click.echo("Départements disponibles :")
        for dept in session.query(Department).all():
            click.echo(f"{dept.id} - {dept.name}")
        department_id = click.prompt("Département (id)", default=user.department_id, type=int)

    user.name = name
    if password:
        user.password = hash_password(password)

    department = session.query(Department).get(department_id)
    if not department:
        click.echo("Département introuvable.")
        return
    user.department = department

    session.commit()
    sentry_sdk.capture_message(f"Utilisateur modifié : {email} par {get_current_user().email}")
    click.echo("Utilisateur mis à jour avec succès.")

@require_role("gestion")
def delete_user(email):
    """
    Supprime un utilisateur identifié par son email.
    """
    current_user = get_current_user()
    if get_user_role(current_user) != "gestion":
        click.echo("Vous n'avez pas les droits pour supprimer un utilisateur.")
        return

    user = session.query(User).filter_by(email=email).first()
    if not user:
        click.echo("Utilisateur introuvable.")
        return

    session.delete(user)
    session.commit()
    click.echo(f"Utilisateur avec l'email '{email}' supprimé avec succès.")