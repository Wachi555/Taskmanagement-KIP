from database.orm_models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import logging

"""Database initialization and session management for the simulated ERP system."""

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

engine = create_engine("sqlite:///erp_simulation.db", echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
