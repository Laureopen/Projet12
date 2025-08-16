import uuid
from datetime import datetime, timedelta

from controllers.client_controller import update_client
from controllers.contract_controller import update_contract
from models.department import Department
from models.user import User
from models.client import Client
from models.contract import Contract
from models.event import Event
from utils.auth import hash_password


def test_full_integration_flow(test_session, monkeypatch):
    """
    Test d'intégration complet étape par étape :
    1. Création du premier admin
    2. Création d’un commercial
    3. Création d’un client
    4. Mise à jour du client
    5. Création d’un contrat
    6. Mise à jour du contrat
    7. Création d’un événement
    """

    # 1. Création du département
    dep = test_session.query(Department).filter_by(name="commercial").first()
    if not dep:
        dep = Department(name="commercial")
        test_session.add(dep)
        test_session.commit()

    # 2. Création du premier admin
    admin = test_session.query(User).filter_by(email="admin@epicevents.com").first()
    if not admin:
        admin = User(
            name="Epic admin",
            email="admin@epicevents.com",
            password=hash_password("1234"),
            department_id=dep.id
        )
        test_session.add(admin)
        test_session.commit()
    assert admin.id is not None

    # 3. Création d’un commercial
    unique_suffix = str(uuid.uuid4())[:8]
    sales_user = User(
        name="Sales Person",
        email=f"sales_{unique_suffix}@example.com",
        password=hash_password("1234"),
        department_id=dep.id
    )
    test_session.add(sales_user)
    test_session.commit()
    assert sales_user.id is not None

    # 4. Création d’un client
    client = Client(
        name="Old Name",
        email=f"old_{unique_suffix}@example.com",
        phone="0101010101",
        company="Old Co",
        sales_contact_id=sales_user.id
    )
    test_session.add(client)
    test_session.commit()
    assert client.id is not None

    # 5. Mise à jour du client
    update_client(
        client_id=client.id,
        name="New Name",
        email=client.email,
        phone=client.phone,
        company=client.company,
        db_session=test_session,
        current_user=sales_user
    )
    updated_client = test_session.get(Client, client.id)
    assert updated_client.name == "New Name"

    # 6. Création d’un contrat
    contract = Contract(
        client_id=client.id,
        sales_contact_id=sales_user.id,
        amount_total=5000.0,
        amount_remaining=5000.0,
        signed=False
    )
    test_session.add(contract)
    test_session.commit()
    assert contract.id is not None

    # 7. Mise à jour du contrat
    monkeypatch.setattr("utils.auth.get_current_user", lambda: sales_user)
    update_contract(
        contract_id=contract.id,
        amount_total=6000.0,
        amount_remaining=5500.0,
        signed="oui",
        db_session=test_session,
        current_user=sales_user
    )
    updated_contract = test_session.get(Contract, contract.id)
    assert updated_contract.amount_total == 6000.0
    assert updated_contract.amount_remaining == 5500.0
    assert updated_contract.signed is True
    assert updated_contract.signed_date is not None

    # 8. Création d’un événement
    start = datetime.utcnow()
    end = start + timedelta(hours=2)
    event = Event(
        name="Kickoff Meeting",
        contract_id=contract.id,
        date_start=start,
        date_end=end,
        location="Salle A",
        attendees=15,
        notes="Kickoff project"
    )
    test_session.add(event)
    test_session.commit()
    event_in_db = test_session.query(Event).filter_by(name="Kickoff Meeting").first()
    assert event_in_db is not None
    assert event_in_db.contract_id == contract.id
