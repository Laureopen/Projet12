from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base


# Client
class Client(Base):
    """
       Représente un client dans la base de données.

       Attributs :
           id (int): Identifiant unique du client.
           name (str): Nom du client (obligatoire).
           email (str): Adresse email du client (obligatoire).
           phone (str): Numéro de téléphone du client.
           company (str): Nom de la société du client.
           created_date (datetime): Date de création de l'enregistrement, valeur par défaut à la création.
           updated_date (datetime): Date de la dernière mise à jour, mise à jour automatique à chaque modification.
           sales_contact_id (int): ID du commercial associé (clé étrangère vers la table users).
           sales_contact (User): Objet relationnel du commercial associé.
           contracts (list[Contract]): Liste des contrats associés à ce client.
       """
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
