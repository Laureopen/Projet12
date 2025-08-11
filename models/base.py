# models/base.py
from sqlalchemy.orm import declarative_base
Base = declarative_base()

# Importer ici tous les modèles pour qu’ils soient chargés dès qu’on importe Base
from . import client, contract, department, event, user
