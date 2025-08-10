from utils import auth
from models.user import User
from models.department import Department
from models.client import Client


def test_create_client_command(runner, test_session, monkeypatch):
    # 1. Nettoyage complet des tables concernées
    test_session.query(Client).delete()
    test_session.query(User).delete()
    test_session.query(Department).delete()
    test_session.commit()

    # 2. Création d'un département et d'un utilisateur (commercial) dans test_session
    dep = Department(name="Sales")
    test_session.add(dep)
    test_session.commit()

    sales_contact = User(
        name="Sales Person",
        email="sales@example.com",
        password="password123",
        department_id=dep.id
    )
    test_session.add(sales_contact)
    test_session.commit()

    # 3. Patch de la session dans auth.py pour qu'il utilise la session de test
    monkeypatch.setattr(auth, "session", test_session)

    # 4. Patch de get_current_user pour retourner un objet User attaché à test_session
    monkeypatch.setattr(auth, "get_current_user", lambda: test_session.query(User).get(sales_contact.id))