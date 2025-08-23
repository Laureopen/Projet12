# Commandes utilisateur
import click

from controllers.user_controller import (
    create_user,
    update_user,
    delete_user, list_departments, list_users
)
from models.department import Department
from utils.auth import session


@click.group()
def user_cli():
    """
    Commandes liées aux utilisateurs.

    Ce groupe permet :
    - la création d'un utilisateur
    - la mise à jour d'un utilisateur existant
    - la suppression d'un utilisateur
    - la liste des utilisateurs
    """
    pass


@click.command("create-user")
@click.option("--name", type=str, prompt="Nom complet", help="Nom complet de l'utilisateur")
@click.option("--email", type=str, prompt="Email", help="Adresse email")
def create_user_cmd(name, email):
    """
    Commande CLI pour créer un nouvel utilisateur.
    """
    try:
        # Affiche la liste des départements
        departments = list_departments()
        click.echo(departments)

        dep_id = click.prompt("\nDépartement (ID)", type=int)
        password = click.prompt("Mot de passe", type=str, hide_input=True, confirmation_prompt=True)

        user = create_user(name, email, dep_id, password)
        click.echo(user)
    except Exception as e:
        click.echo(f"Erreur lors de la création : {e}")


@click.command("update-user")
@click.option("--name", type=str, default=None, help="Nouveau nom complet de l'utilisateur")
@click.option("--password", type=str, default=None, help="Nouveau mot de passe de l'utilisateur")
@click.option("--department-id", type=int, default=None, help="Nouvel identifiant du département")
def update_user_cmd(name, password, department_id):
    try:
        # Affiche la liste des utilisateurs
        users_data = list_users()

        lines = [f"{u['id']} | {u['name']} | {u['email']} | Département : {u['department_name']}"
                 for u in users_data.values()]
        message = "\n".join(lines)
        click.echo(message)

        # Demande l'email après affichage
        email = click.prompt("Email de l'utilisateur à modifier", type=str)

        if email not in users_data:
            click.echo("Utilisateur non trouvé.")
            return

        user_defaults = users_data[email]

        if name is None:
            name = click.prompt("Nom complet", type=str, default=user_defaults["name"])

        if password is None:
            password = click.prompt(
                "Mot de passe",
                type=str,
                hide_input=True,
                confirmation_prompt=True,
                default="",
                show_default=False
            )

            if password.strip() == "":
                password = None

        if department_id is None:
            click.echo("Départements disponibles :")
            for dept in session.query(Department).all():
                click.echo(f"{dept.id} - {dept.name}")
            default_dep_id = next((d.id for d in session.query(Department).all()
                                   if d.name == user_defaults["department_name"]), None)
            department_id = click.prompt("Département (id)", type=int, default=default_dep_id)

        user = update_user(email, name, password, department_id)
        click.echo(user)
    except Exception as e:
        click.echo(f"Erreur lors de la mise à jour : {e}")


@click.command("delete-user")
def delete_user_cmd():
    """
    Commande pour supprimer un utilisateur.
    """
    try:
        # Affiche la liste des utilisateurs
        users_data = list_users()

        lines = [f"{u['id']} | {u['name']} | {u['email']} | Département : {u['department_name']}"
                 for u in users_data.values()]
        message = "\n".join(lines)
        click.echo(message)

        # Demande l'email après affichage
        email = click.prompt("Email de l'utilisateur à supprimer", type=str)

        if not click.confirm(
                f"Êtes-vous sûr de vouloir supprimer l'utilisateur '{email}' ? Cette action est irréversible."
        ):
            click.echo("Suppression annulée.")
            return

        delete_user(email)
    except Exception as e:
        click.echo(f"Erreur lors de la suppression : {e}")

@click.command("list")
def list_users_cmd():
    """
    Commande pour afficher tous les utilisateurs existants.
    """
    try:
        users_data = list_users()

        lines = [f"[{u['id']}] Nom: {u['name']} | Email: {u['email']} | "
                 f"Département: {u['department_name']}"
                 for u in users_data.values()]
        message = "\n".join(lines)
        click.echo(message)

    except Exception as e:
        click.echo(f"Erreur : {e}")


# Enregistrement des commandes dans le groupe principal
user_cli.add_command(create_user_cmd)
user_cli.add_command(update_user_cmd)
user_cli.add_command(delete_user_cmd)
user_cli.add_command(list_users_cmd)
