from sqlalchemy import create_engine
import os

from models import Base

db_user ="crm"
db_password = os.getenv("EPIC_DB_PASSWORD")
db_host ="localhost"
db_port ="5432"
db_name ="epic_crm"


db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(db_url)

try:
    conn = engine.connect()
    print("Sucess!")
    Base.metadata.create_all(bind=engine)
except Exception as ex:
    print(ex)

