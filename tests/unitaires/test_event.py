from datetime import datetime, timedelta
from models.contract import Contract
from models.event import Event


def test_create_event(test_session):
    # récupérer ou créer un contrat
    contract = test_session.query(Contract).first()
    if not contract:
        # créer un contrat test
        contract = Contract(
            client_id=1,  # client test
            sales_contact_id=1,
            amount_total=1000,
            amount_remaining=1000
        )
        test_session.add(contract)
        test_session.commit()

    # créer un événement
    event = Event(
        name="Meeting Test",
        contract_id=contract.id,
        date_start=datetime.utcnow(),
        date_end=datetime.utcnow() + timedelta(hours=2),
        location="Salle 1",
        attendees=10,
        notes="Test event"
    )
    test_session.add(event)
    test_session.commit()

    # vérifier que l'événement est bien créé
    fetched = test_session.get(Event, event.id)
    assert fetched.name == "Meeting Test"
