from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, DECIMAL
from sqlalchemy.sql import func
from database import Base
import enum

# ENUM Types
class RoleEnum(str, enum.Enum):
    Patient = "Patient"
    Doctor = "Doctor"
    Admin = "Admin"

class StatusEnum(str, enum.Enum):
    Pending = "Pending"
    Confirmed = "Confirmed"
    Cancelled = "Cancelled"

class PaymentMethodEnum(str, enum.Enum):
    Card = "Card"
    Easypaisa = "Easypaisa"
    JazzCash = "JazzCash"

class PaymentStatusEnum(str, enum.Enum):
    Success = "Success"
    Failed = "Failed"
    Pending = "Pending"

class LabTestStatusEnum(str, enum.Enum):
    Pending = "Pending"
    Completed = "Completed"

# Tables
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
    patient_id = Column(Integer, ForeignKey("users.user_id", ondelete="RESTRICT"))
    doctor_id = Column(Integer, ForeignKey("users.user_id", ondelete="RESTRICT"))
    appointment_date = Column(DateTime, nullable=False)
    status = Column(Enum(StatusEnum), default="Pending")

class Prescription(Base):
    __tablename__ = "prescriptions"
    prescription_id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.appointment_id", ondelete="RESTRICT"))
    doctor_id = Column(Integer, ForeignKey("users.user_id", ondelete="RESTRICT"))
    patient_id = Column(Integer, ForeignKey("users.user_id", ondelete="RESTRICT"))
    prescribed_on = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)

class Inventory(Base):
    __tablename__ = "inventory"
    medicine_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)

class Payment(Base):
    __tablename__ = "payments"
    payment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="RESTRICT"))
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(Enum(PaymentMethodEnum), nullable=False)
    status = Column(Enum(PaymentStatusEnum), default="Pending")
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())

class LabTest(Base):
    __tablename__ = "lab_tests"
    test_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.user_id", ondelete="RESTRICT"))
    test_type = Column(String(100), nullable=False)
    date_requested = Column(DateTime(timezone=True), server_default=func.now())
    result = Column(Text)
    status = Column(Enum(LabTestStatusEnum), default="Pending")

class EMR(Base):
    __tablename__ = "emr"
    emr_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.user_id", ondelete="RESTRICT"))
    doctor_id = Column(Integer, ForeignKey("users.user_id", ondelete="RESTRICT"))
    summary = Column(Text)
    created_on = Column(DateTime(timezone=True), server_default=func.now())
