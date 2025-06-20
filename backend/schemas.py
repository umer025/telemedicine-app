from pydantic import BaseModel, ConfigDict, Field, EmailStr, constr
from typing import Optional
from datetime import datetime
from enum import Enum

# ------------------ ENUMS ------------------
class RoleEnum(str, Enum):
    Patient = "Patient"
    Doctor = "Doctor"
    Admin = "Admin"

class StatusEnum(str, Enum):
    Pending = "Pending"
    Confirmed = "Confirmed"
    Cancelled = "Cancelled"

class PaymentMethodEnum(str, Enum):
    Card = "Card"
    Easypaisa = "Easypaisa"
    JazzCash = "JazzCash"

class PaymentStatusEnum(str, Enum):
    Success = "Success"
    Failed = "Failed"
    Pending = "Pending"

class LabTestStatusEnum(str, Enum):
    Pending = "Pending"
    Completed = "Completed"

# ------------------ AUTH ------------------
class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=6)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[RoleEnum] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordUpdate(BaseModel):
    email: EmailStr
    new_password: constr(min_length=6)

# ------------------ USER ------------------
class UserBase(BaseModel):
    full_name: constr(min_length=2, max_length=100, pattern=r"^[a-zA-Z\s]+$")
    email: EmailStr
    password: constr(min_length=6)  # change from password_hash
    role: RoleEnum
    phone_number: constr(min_length=10, max_length=15)

class UserCreate(UserBase):
    pass

class UserOut(BaseModel):
    user_id: int
    full_name: str
    email: str
    role: RoleEnum
    phone_number: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserWithToken(BaseModel):
    user: UserOut
    token: TokenResponse

# ------------------ APPOINTMENT ------------------
class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    status: StatusEnum = StatusEnum.Pending

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentOut(AppointmentBase):
    appointment_id: int
    model_config = ConfigDict(from_attributes=True)

# ------------------ PRESCRIPTION ------------------
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

# ------------------ INVENTORY ------------------
class InventoryBase(BaseModel):
    name: constr(min_length=2)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)

class InventoryCreate(InventoryBase):
    pass

class InventoryOut(InventoryBase):
    medicine_id: int
    model_config = ConfigDict(from_attributes=True)

# ------------------ PAYMENT ------------------
class PaymentBase(BaseModel):
    user_id: int
    amount: float
    payment_method: PaymentMethodEnum
    status: PaymentStatusEnum = PaymentStatusEnum.Pending

class PaymentCreate(PaymentBase):
    pass

class PaymentOut(PaymentBase):
    payment_id: int
    transaction_date: datetime
    model_config = ConfigDict(from_attributes=True)

# ------------------ LAB TEST ------------------
class LabTestBase(BaseModel):
    patient_id: int
    test_type: str
    result: Optional[str] = None
    status: LabTestStatusEnum = LabTestStatusEnum.Pending

class LabTestCreate(LabTestBase):
    pass

class LabTestOut(LabTestBase):
    test_id: int
    date_requested: datetime
    model_config = ConfigDict(from_attributes=True)

# ------------------ EMR ------------------
class EMRBase(BaseModel):
    patient_id: int
    doctor_id: int
    summary: Optional[str] = None

class EMRCreate(EMRBase):
    pass

class EMROut(EMRBase):
    emr_id: int
    created_on: datetime
    model_config = ConfigDict(from_attributes=True)
