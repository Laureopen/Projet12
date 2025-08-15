import uuid
from controllers.client_controller import update_client
from models.user import User
from models.department import Department
from models.client import Client
from utils.auth import hash_password


def test_update_client(test_session):
    # --- Créer département ---
    dep = test_session.query(Department).filter_by(name="commercial").first()
    if not dep:
        dep = Department(name="commercial")
        test_session.add(dep)
        test_session.commit()

    # --- Générer un suffixe unique pour éviter les collisions ---
    unique_suffix = str(uuid.uuid4())[:8]

    # --- Créer utilisateur commercial unique ---
    user = User(
        name="Sales Person",
        email=f"sales_{unique_suffix}@example.com",
        password=hash_password("1234"),
        department_id=dep.id
    )
    try:
        test_session.add(user)
        test_session.commit()
    except Exception as e:
        test_session.rollback()
        raise RuntimeError(f"Erreur lors de la création de l'utilisateur: {e}")

    # --- Créer client unique ---
    client = Client(
        name="Old Name",
        email=f"old_{unique_suffix}@example.com",
        phone="0101010101",
        company="Old Co",
        sales_contact_id=user.id
    )
    try:
        test_session.add(client)
        test_session.commit()
    except Exception as e:
        test_session.rollback()
        raise RuntimeError(f"Erreur lors de la création du client: {e}")

    # --- Appeler update_client directement ---
    update_client(
        client_id=client.id,
        name="New Name",
        email=client.email,
        phone=client.phone,
        company=client.company,
        db_session=test_session,
        current_user=user
    )

    # --- Vérifier que le nom a été mis à jour ---
    updated_client = test_session.get(Client, client.id)
    assert updated_client.name == "New Name"

    print("Test passé avec succès, client mis à jour:", updated_client.name)
