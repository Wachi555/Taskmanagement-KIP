from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.orm_models import Base

engine = create_engine('sqlite:///erp_simulation.db', echo=True)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
