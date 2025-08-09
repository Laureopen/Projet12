from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base

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


