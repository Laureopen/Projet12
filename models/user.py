
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


# Utilisateur
class User(Base):
    """
        Représente un utilisateur du système, lié à un département et pouvant être
        un commercial ou un support.

        Attributs:
            id (int): Identifiant unique de l'utilisateur.
            name (str): Nom complet de l'utilisateur.
            email (str): Adresse email unique de l'utilisateur.
            password (str): Mot de passe hashé de l'utilisateur.
            department_id (int): Identifiant du département auquel appartient l'utilisateur.
            department (Department): Relation vers le département.
            clients (list[Client]): Liste des clients associés à l'utilisateur (en tant que commercial).
            contracts (list[Contract]): Liste des contrats associés à l'utilisateur (en tant que commercial).
            supported_events (list[Event]): Liste des événements supportés par l'utilisateur (en tant que support).
        """
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
        return f"<User(name={self.name}, role={self.department.name})>"
