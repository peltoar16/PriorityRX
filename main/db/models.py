import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

def gen_uuid():
    return str(uuid.uuid4())

class Patient(Base):
    __tablename__ = "patients"
    id = Column(String, primary_key=True, index=True)  # using string for demo (UUID)
    first_name = Column(String(100))
    last_name = Column(String(100))
    date_of_birth = Column(String, nullable=True)
    phone = Column(String(32), nullable=True)
    email = Column(String(255), nullable=True)
    terminal_illness = Column(Boolean, default=False)
    icd10_primary_code = Column(String(20), nullable=True)
    icd10_additional_codes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Medication(Base):
    __tablename__ = "medications"
    id = Column(String, primary_key=True, index=True)
    generic_name = Column(String(200))
    brand_name = Column(String(200), nullable=True)
    ndc_number = Column(String(20), nullable=True)
    dosage_form = Column(String(50), nullable=True)
    strength = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)

class Prescription(Base):
    __tablename__ = "prescriptions"
    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"))
    medication_id = Column(String, ForeignKey("medications.id"))
    prescriber_id = Column(String, nullable=True)
    date_prescribed = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True)
    days_supply = Column(Integer, nullable=True)
    dosage_instructions = Column(Text, nullable=True)
    refills_allowed = Column(Integer, default=0)
    refills_remaining = Column(Integer, default=0)
    status = Column(String(50), default="active")
    pa_required = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Pharmacy(Base):
    __tablename__ = "pharmacies"
    id = Column(String, primary_key=True, index=True)
    name = Column(String(255))
    type = Column(String(50))
    street_address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(20), nullable=True)
    phone = Column(String(32), nullable=True)
    api_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class InventorySnapshot(Base):
    __tablename__ = "inventory_snapshots"
    id = Column(String, primary_key=True, index=True)
    pharmacy_id = Column(String, ForeignKey("pharmacies.id"))
    medication_id = Column(String, ForeignKey("medications.id"))
    quantity_on_hand = Column(Integer, default=0)
    eta_timestamp = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    price_currency = Column(String(10), default="USD")
    snapshot_time = Column(DateTime, default=datetime.utcnow)

class RefillRequest(Base):
    __tablename__ = "refill_requests"
    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.id"))
    prescription_id = Column(String, ForeignKey("prescriptions.id"))
    status = Column(String(50), default="pending")
    severity_score = Column(Float, default=0.0)
    routed_pharmacy_id = Column(String, ForeignKey("pharmacies.id"), nullable=True)
    api_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class RoutingDecision(Base):
    __tablename__ = "routing_decisions"
    id = Column(String, primary_key=True, index=True)
    prescription_id = Column(String, ForeignKey("prescriptions.id"))
    chosen_pharmacy_id = Column(String, ForeignKey("pharmacies.id"))
    reason = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
