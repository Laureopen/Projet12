from models.contract import Contract
from models.client import Client
from models.user import User
from models.department import Department
from utils.auth import hash_password


def test_update_contract(test_session, monkeypatch):
    # 1. Créer département spécifique au test
    dep = test_session.query(Department).filter_by(name="commercial").first()
    if not dep:
        dep = Department(name="commercial")
        test_session.add(dep)
        test_session.commit()

    # 2. Créer utilisateur commercial
    user = test_session.query(User).filter_by(email="contract_commercial@example.com").first()
    if not user:
        user = User(
            name="Contract Commercial",
            email="contract_commercial@example.com",
            password=hash_password("abcd"),
            department_id=dep.id
        )
        test_session.add(user)
        test_session.commit()

    # Patch get_current_user pour retourner notre commercial
    monkeypatch.setattr("utils.auth.get_current_user", lambda: user)

    # 3. Créer client spécifique au test
    client = Client(
        name="Contract Client",
        email="contract_client@example.com",
        phone="0303030303",
        company="ContractCo",
        sales_contact_id=user.id
    )
    test_session.add(client)
    test_session.commit()

    # 4. Créer contrat
    contract = Contract(
        client_id=client.id,
        sales_contact_id=user.id,
        amount_total=5000.0,
        amount_remaining=5000.0,
        signed=False
    )
    test_session.add(contract)
    test_session.commit()

    # 5. Appeler update_contract avec de nouvelles valeurs
    from controllers.contract_controller import update_contract
    update_contract(
        contract_id=contract.id,
        amount_total=6000.0,
        amount_remaining=5500.0,
        signed="oui",
        db_session=test_session,
        current_user=user
    )

    # 6. Vérifier que les modifications ont été appliquées
    updated_contract = test_session.get(Contract, contract.id)
    assert updated_contract.amount_total == 6000.0
    assert updated_contract.amount_remaining == 5500.0
    assert updated_contract.signed is True
    assert updated_contract.signed_date is not None
