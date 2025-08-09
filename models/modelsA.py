from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Enum
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


# Département (commercial, support, gestion)
class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="department")

    def __repr__(self):
        return f"<Department(name={self.name})>"


# Utilisateur
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # à hasher en pratique

    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    department = relationship("Department", back_populates="users")

    # Relations : cascade via `backref` ou manuellement si nécessaire
    clients = relationship("Client", back_populates="sales_contact", foreign_keys="Client.sales_contact_id")
    contracts = relationship("Contract", back_populates="sales_contact", foreign_keys="Contract.sales_contact_id")
    supported_events = relationship("Event", back_populates="support_contact", foreign_keys="Event.support_contact_id")

    def __repr__(self):
        return f"<User(name={self.name}, role={self.department.name.value})>"


# Client
class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    company = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Commercial associé
    sales_contact_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sales_contact = relationship("User", back_populates="clients")

    contracts = relationship("Contract", back_populates="client")

    def __repr__(self):
        return f"<Client(name={self.name}, sales_contact={self.sales_contact.name})>"


# Contrat
class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="contracts")

    sales_contact_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sales_contact = relationship("User", back_populates="contracts")

    amount_total = Column(Float, nullable=False)
    amount_remaining = Column(Float, nullable=False)
    signed = Column(Boolean, default=False)
    signed_date = Column(DateTime, nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)

    events = relationship("Event", back_populates="contract")

    def __repr__(self):
        return f"<Contract(client={self.client.name}, signed={self.signed})>"


# Événement
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    contract = relationship("Contract", back_populates="events")

    support_contact_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    support_contact = relationship("User", back_populates="supported_events")

    date_start = Column(DateTime, nullable=False)
    date_end = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    attendees = Column(Integer, nullable=False)
    notes = Column(String)

    def __repr__(self):
        return f"<Event(name={self.name}, contract_id={self.contract_id})>"
