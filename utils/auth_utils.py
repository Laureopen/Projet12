from utils.auth import get_current_user


def require_role(*allowed_roles):
    """
    Décorateur qui vérifie le rôle de l'utilisateur avant exécution.
    Lève une exception si l'accès est refusé.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                # Récupère l'utilisateur courant
                current_user = kwargs.get('current_user') or get_current_user()

                if not current_user:
                    raise PermissionError("Utilisateur non authentifié")

                # Vérifie si l'utilisateur a le département attendu
                if not hasattr(current_user, 'department') or not current_user.department:
                    raise PermissionError("L'utilisateur n'a pas de département défini")

                # Normalise les noms de rôles (enlève espaces et met en minuscule)
                user_role = current_user.department.name.strip().lower()
                allowed = {role.strip().lower() for role in allowed_roles}

                if user_role not in allowed:
                    required_roles = " ou ".join(allowed_roles)
                    raise PermissionError(f"Accès refusé. Rôle(s) requis : {required_roles}")

                return func(*args, **kwargs)

            except Exception as e:
                print(f"Erreur d'autorisation : {str(e)}")
                raise  # Relance l'exception pour les tests

        return wrapper

    return decorator
