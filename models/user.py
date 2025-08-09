
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


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

