from sqlalchemy import Column, String, Float, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class PharmacyORM(Base):
    __tablename__ = "pharmacies"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    supports_delivery = Column(Boolean, default=False)
    supports_pickup = Column(Boolean, default=True)
    supports_controlled = Column(Boolean, default=False)

    avg_response_minutes = Column(Float)
    fill_success_rate = Column(Float)
    stock_probability = Column(Float)

    api_enabled = Column(Boolean, default=False)