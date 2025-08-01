from utils.auth import get_current_user, get_user_role

def require_role(*allowed_roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = get_current_user()
            role = get_user_role(user)
            if role not in allowed_roles:
                print(f"Accès refusé. Rôle requis : {', '.join(allowed_roles)}")
                return
            return func(*args, **kwargs)
        return wrapper
    return decorator
