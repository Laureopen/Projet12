import getpass
import sentry_sdk
import click
from utils.auth_utils import require_role
from sqlalchemy.orm import sessionmaker
from models.department import Department
from models.user import User
from utils.auth import hash_password, get_current_user, get_user_role
from utils.connection import engine

# Création d'une session SQLAlchemy pour interagir avec la base de données
session = sessionmaker(bind=engine)()


@require_role("gestion")
def create_user(name, email):
    """
    Crée un nouvel utilisateur en demandant le mot de passe et le département.

    Args:
        name (str): Nom complet de l'utilisateur.
        email (str): Adresse email unique de l'utilisateur.

    Processus :
        - Demande le mot de passe via getpass (entrée cachée).
        - Affiche la liste des départements disponibles.
        - Demande à l'utilisateur de choisir un département par son ID.
        - Vérifie la validité du département choisi.
        - Vérifie qu'un utilisateur avec le même email n'existe pas.
        - Hache le mot de passe.
        - Crée l'utilisateur et l'ajoute en base.
        - Envoie un message à Sentry pour audit.
    """
    password = getpass.getpass("Mot de passe : ")

    # Récupération et affichage des départements existants
    departments = session.query(Department).all()
    for dept in departments:
        print(f"{dept.id} - {dept.name}")

    # Saisie interactive de l'ID de département
    dep_input = input("Département (id) : ").strip()

    # Vérification que l'entrée est un entier valide et que le département existe
    try:
        dep_id = int(dep_input)
        department = session.query(Department).get(dep_id)
        if not department:
            print("Département introuvable.")
            return
    except ValueError:
        print("Entrée invalide, veuillez entrer un ID numérique.")
        return

    # Vérification qu'aucun utilisateur n'existe déjà avec cet email
    if session.query(User).filter_by(email=email).first():
        print("Utilisateur déjà existant.")
        return

    # Hachage du mot de passe et création du nouvel utilisateur
    hashed = hash_password(password)
    user = User(name=name, email=email, password=hashed, department=department)
    session.add(user)
    session.commit()

    # Envoi d'un message d'audit à Sentry
    sentry_sdk.capture_message(f"Utilisateur créé : {email} par {get_current_user().email}")

    print("Utilisateur créé avec succès.")


@require_role("gestion")
def update_user(email, name, password, department_id):
    """
    Met à jour un utilisateur existant identifié par son email.

    Args:
        email (str): Email de l'utilisateur à modifier.
        name (str | None): Nouveau nom complet (optionnel).
        password (str | None): Nouveau mot de passe (optionnel).
        department_id (int | None): Nouvel ID de département (optionnel).

    Processus :
        - Recherche l'utilisateur via son email.
        - Vérifie que l'utilisateur a bien le rôle 'gestion'.
        - Pour les champs non fournis, demande leur saisie interactive.
        - Vérifie que le département choisi existe.
        - Hache le nouveau mot de passe si fourni.
        - Met à jour les informations et sauvegarde en base.
        - Envoie un message à Sentry pour audit.
    """
    user = session.query(User).filter_by(email=email).first()
    if not user:
        click.echo("Utilisateur introuvable.")
        return

    current_user = get_current_user()
    if get_user_role(current_user) != "gestion":
        click.echo("Vous n'avez pas les droits pour modifier un utilisateur.")
        return

    # Saisie interactive des données si elles ne sont pas fournies
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

    # Mise à jour des champs
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

    Args:
        email (str): Email de l'utilisateur à supprimer.

    Processus :
        - Vérifie que l'utilisateur actuel a le rôle 'gestion'.
        - Recherche l'utilisateur à supprimer.
        - Supprime l'utilisateur de la base de données.
        - Affiche une confirmation.
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
