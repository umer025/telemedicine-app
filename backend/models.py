from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.sql import func
import enum
from database import Base

class RoleEnum(str, enum.Enum):
    Patient = "Patient"
    Doctor = "Doctor"
    Admin = "Admin"

class StatusEnum(str, enum.Enum):
    Pending = "Pending"
    Confirmed = "Confirmed"
    Cancelled = "Cancelled"

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    phone_number = Column(String(15), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Appointment(Base):
    __tablename__ = "appointments"
    appointment_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.user_id"))
    doctor_id = Column(Integer, ForeignKey("users.user_id"))
    appointment_date = Column(DateTime, nullable=False)
    status = Column(Enum(StatusEnum), default="Pending")

class Prescription(Base):
    __tablename__ = "prescriptions"
    prescription_id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.appointment_id"))
    doctor_id = Column(Integer, ForeignKey("users.user_id"))
    patient_id = Column(Integer, ForeignKey("users.user_id"))
    prescribed_on = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)
