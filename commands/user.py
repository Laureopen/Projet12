# Commandes utilisateur
import click

from controllers.user_controller import (
    create_user,
    update_user,
    delete_user
)


@click.group()
def user_cli():
    """Commandes liées aux utilisateurs"""
    pass


@click.command("create-user")
@click.option("--name", prompt="Nom complet", help="Nom complet de l'utilisateur")
@click.option("--email", prompt="Email", help="Adresse email")
def create_user_cmd(name, email):
    """Création d'un utilisateur"""
    create_user(name, email)

@click.command("update-user")
@click.option('--email', type=str, prompt="Email de l'utilisateur à modifier", help="ID de l'utilisateur")
@click.option("--name", help="Nouveau nom complet")
@click.option("--password", help="Nouveau mot de passe")
@click.option("--department-id", type=int, help="Nouvel ID du département")
def update_user_cmd(email, name, password, department_id):
    """Mise à jour d'un utilisateur"""
    update_user(email, name, password, department_id)


@click.command("delete-user")
@click.option('--email', type=str, prompt="Email de l'utilisateur à supprimer", help="ID de l'utilisateur")
@click.confirmation_option(prompt="Êtes-vous sûr de vouloir supprimer cet utilisateur ?")
def delete_user_cmd(email):
    """Suppression d'un utilisateur"""
    delete_user(email)


user_cli.add_command(create_user_cmd)
user_cli.add_command(update_user_cmd)
user_cli.add_command(delete_user_cmd)