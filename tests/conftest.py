# conftest.py
import pytest
from click.testing import CliRunner
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.department import Department


@pytest.fixture(scope='session')
def engine():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)  # Crée toutes les tables
    yield engine
    engine.dispose()


@pytest.fixture
def test_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def setup_department(test_session):
    dep = Department(name="gestion")
    test_session.add(dep)
    test_session.commit()
    return dep


@pytest.fixture
def runner():
    return CliRunner()
