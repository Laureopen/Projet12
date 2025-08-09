from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base



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
