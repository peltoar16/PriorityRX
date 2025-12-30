from sqlalchemy import Column, String, Float, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True)

    latitude = Column(Float)
    longitude = Column(Float)

    prefers_delivery = Column(Boolean, default=False)

    # optional
    address_line = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)