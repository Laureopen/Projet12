from models.user import User
from models.department import Department
from utils.auth import hash_password


def test_create_first_user(test_session):
    dep = test_session.query(Department).filter_by(name="commercial").first()
    if not dep:
        dep = Department(name="commercial")
        test_session.add(dep)
        test_session.commit()

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
