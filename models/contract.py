from datetime import datetime
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import Base


# Contrat
class Contract(Base):
    """
        Représente un contrat commercial lié à un client et un commercial.

        Attributs:
            id (int): Identifiant unique du contrat.
            client_id (int): Clé étrangère vers le client associé.
            client (Client): Relation SQLAlchemy vers l'objet Client.
            sales_contact_id (int): Clé étrangère vers l'utilisateur commercial associé.
            sales_contact (User): Relation vers l'objet User représentant le commercial.
            amount_total (float): Montant total du contrat.
            amount_remaining (float): Montant restant à payer.
            signed (bool): Statut indiquant si le contrat est signé.
            signed_date (datetime): Date de signature du contrat (peut être None).
            created_date (datetime): Date de création du contrat.
            events (list[Event]): Liste des événements liés à ce contrat.
        """
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
