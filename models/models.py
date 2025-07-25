from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    department = Column(String)
    role = Column(String)

class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    company = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)  # Date de création
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Dernière maj
    sales_contact_id = Column(Integer, ForeignKey('users.id'))
    sales_contact = relationship("User")

class Contract(Base):
    __tablename__ = 'contracts'
    id = Column(Integer, primary_key=True)  # Identifiant unique
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)  # Lien client
    client = relationship("Client", backref="contracts")
    sales_contact_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Commercial
    sales_contact = relationship("User", backref="contracts")
    amount_total = Column(Float, nullable=False)         # Montant total
    amount_remaining = Column(Float, nullable=False)     # Montant restant
    signed = Column(Boolean, default=False)              # Statut signé ou non
    signed_date = Column(DateTime, nullable=True)        # Date de signature (optionnelle)
    created_date = Column(DateTime, default=datetime.utcnow)  # Date de création

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
