# Commandes utilisateur
import click

from controllers.user_controller import (
    create_user,
    update_user,
    delete_user
)


@click.group()
def user_cli():
    """
    Commandes liées aux utilisateurs.

    Ce groupe permet :
    - la création d'un utilisateur
    - la mise à jour d'un utilisateur existant
    - la suppression d'un utilisateur
    """
    pass


@click.command("create-user")
@click.option("--name", prompt="Nom complet", help="Nom complet de l'utilisateur")
@click.option("--email", prompt="Email", help="Adresse email")
def create_user_cmd(name, email):
    """
    Commande pour créer un nouvel utilisateur.

    Args:
        name (str): Nom complet de l'utilisateur.
        email (str): Adresse email de l'utilisateur.
    """
    create_user(name, email)


@click.command("update-user")
@click.option('--email', type=str, prompt="Email de l'utilisateur à modifier",
              help="Adresse email de l'utilisateur à mettre à jour")
@click.option("--name", help="Nouveau nom complet de l'utilisateur")
@click.option("--password", help="Nouveau mot de passe")
@click.option("--department-id", type=int, help="Nouvel identifiant du département")
def update_user_cmd(email, name, password, department_id):
    """
    Commande pour mettre à jour les informations d'un utilisateur existant.

    Args:
        email (str): Email de l'utilisateur à modifier.
        name (str, optional): Nouveau nom complet.
        password (str, optional): Nouveau mot de passe.
        department_id (int, optional): Nouvel identifiant de département.
    """
    update_user(email, name, password, department_id)


@click.command("delete-user")
@click.option('--email', type=str, prompt="Email de l'utilisateur à supprimer",
              help="Adresse email de l'utilisateur à supprimer")
@click.confirmation_option(prompt="Êtes-vous sûr de vouloir supprimer cet utilisateur ?")
def delete_user_cmd(email):
    """
    Commande pour supprimer un utilisateur.

    Args:
        email (str): Adresse email de l'utilisateur à supprimer.
    """
    delete_user(email)


# Enregistrement des commandes dans le groupe principal
user_cli.add_command(create_user_cmd)
user_cli.add_command(update_user_cmd)
user_cli.add_command(delete_user_cmd)