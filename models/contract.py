from datetime import datetime
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import Base


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
