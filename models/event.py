from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base

# Événement
class Event(Base):
    """
       Représente un événement lié à un contrat, pouvant être supporté par un utilisateur du support.

       Attributs:
           id (int): Identifiant unique de l'événement.
           name (str): Nom de l'événement.
           contract_id (int): Identifiant du contrat associé.
           contract (Contract): Relation vers le contrat associé.
           support_contact_id (int, optionnel): Identifiant de l'utilisateur support assigné.
           support_contact (User, optionnel): Relation vers l'utilisateur support assigné.
           date_start (datetime): Date et heure de début de l'événement.
           date_end (datetime): Date et heure de fin de l'événement.
           location (str): Lieu où se déroule l'événement.
           attendees (int): Nombre de participants attendus.
           notes (str, optionnel): Notes complémentaires concernant l'événement.
       """
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
