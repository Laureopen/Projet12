from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .user import User
from .base import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="department")

    def __repr__(self):
        return f"<Department(name={self.name})>"
