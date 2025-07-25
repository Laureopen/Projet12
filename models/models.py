from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Nouvelle table Département
class Departement(Base):
    __tablename__ = 'departements'
    id = Column(Integer, primary_key=True)
    code = Column(String(3), unique=True, nullable=False)  # Exemple : '75', '92', '93'
    name = Column(String, nullable=False)  # Exemple : 'Paris', 'Hauts-de-Seine', 'Seine-Saint-Denis'

    users = relationship("User", back_populates="departement")

# User avec clé étrangère vers departement
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=True)

    departement_id = Column(Integer, ForeignKey('departements.id'), nullable=False)
    departement = relationship("Departement", back_populates="users")

# Client
class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    company = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sales_contact_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    sales_contact = relationship("User")

# Contract
class Contract(Base):
    __tablename__ = 'contracts'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    client = relationship("Client", backref="contracts")

    sales_contact_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    sales_contact = relationship("User", backref="contracts")

    amount_total = Column(Float, nullable=False)
    amount_remaining = Column(Float, nullable=False)
    signed = Column(Boolean, default=False)
    signed_date = Column(DateTime, nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)

# Event
class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    contract_id = Column(Integer, ForeignKey('contracts.id'))
    contract = relationship("Contract")

    support_contact_id = Column(Integer, ForeignKey('users.id'))
    support_contact = relationship("User")

    date = Column(DateTime)
    location = Column(String)
    attendees = Column(Integer)
    notes = Column(String)
