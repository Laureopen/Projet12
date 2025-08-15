from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base


class Department(Base):
    """
        Représente un département au sein de l'organisation.

        Attributs:
            id (int): Identifiant unique du département.
            name (str): Nom unique du département.
            users (list[User]): Liste des utilisateurs associés à ce département.
        """
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="department")

    def __repr__(self):
        return f"<Department(name={self.name})>"
