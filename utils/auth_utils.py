from utils.auth import get_current_user, get_user_role


def require_role(*allowed_roles):
    """
    Décorateur qui restreint l'accès à une fonction aux utilisateurs ayant un rôle spécifique.

    Args:
        *allowed_roles (str): Liste des rôles autorisés à exécuter la fonction décorée.

    Returns:
        function: La fonction décorée qui vérifie le rôle avant exécution.

    Exemple:
        @require_role("admin", "gestion")
        def ma_fonction():
            pass
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Récupère l'utilisateur courant à partir du token stocké
            user = get_current_user()
            # Obtient le rôle (nom du département) de l'utilisateur
            role = get_user_role(user)

            # Vérifie si le rôle de l'utilisateur est autorisé
            if role not in allowed_roles:
                print(f"Accès refusé. Rôle requis : {', '.join(allowed_roles)}")
                return

            # Exécute la fonction d'origine si l'accès est autorisé
            return func(*args, **kwargs)

        return wrapper

    return decorator
