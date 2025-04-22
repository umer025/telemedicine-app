from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class RoleEnum(str, Enum):
    Patient = "Patient"
    Doctor = "Doctor"
    Admin = "Admin"

class StatusEnum(str, Enum):
    Pending = "Pending"
    Confirmed = "Confirmed"
    Cancelled = "Cancelled"

class UserBase(BaseModel):
    full_name: str
    email: str
    password_hash: str
    role: RoleEnum
    phone_number: str

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)  

class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    status: StatusEnum = "Pending"

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentOut(AppointmentBase):
    appointment_id: int
    model_config = ConfigDict(from_attributes=True)  

class PrescriptionBase(BaseModel):
    appointment_id: int
    doctor_id: int
    patient_id: int
    notes: Optional[str] = None

class PrescriptionCreate(PrescriptionBase):
    pass

class PrescriptionOut(PrescriptionBase):
    prescription_id: int
    prescribed_on: datetime
    model_config = ConfigDict(from_attributes=True)  
