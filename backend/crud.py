from sqlalchemy.orm import Session
from fastapi import HTTPException
import models, schemas
import bleach
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ------------------------ AUTH HELPERS ------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def verify_user_credentials(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
def authenticate_user(db: Session, email: str, password: str):
    return verify_user_credentials(db, email, password)

# ------------------------ USERS ------------------------
def create_user(db: Session, user: schemas.UserCreate):
    user_dict = user.dict()
    user_dict["password_hash"] = hash_password(user_dict.pop("password"))
    db_user = models.User(**user_dict)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_users(db: Session):
    return db.query(models.User).all()

def update_user(db: Session, user_id: int, user: schemas.UserCreate):
    user_dict = user.dict(exclude_unset=True)
    
    if "password" in user_dict:
        user_dict["password_hash"] = hash_password(user_dict.pop("password"))

    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user_dict.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if db.query(models.Appointment).filter((models.Appointment.patient_id == user_id) | (models.Appointment.doctor_id == user_id)).first():
        raise HTTPException(status_code=400, detail="User is referenced in appointments")
    if db.query(models.Prescription).filter((models.Prescription.patient_id == user_id) | (models.Prescription.doctor_id == user_id)).first():
        raise HTTPException(status_code=400, detail="User is referenced in prescriptions")
    if db.query(models.Payment).filter(models.Payment.user_id == user_id).first():
        raise HTTPException(status_code=400, detail="User is referenced in payments")
    if db.query(models.LabTest).filter(models.LabTest.patient_id == user_id).first():
        raise HTTPException(status_code=400, detail="User is referenced in lab tests")
    if db.query(models.EMR).filter((models.EMR.patient_id == user_id) | (models.EMR.doctor_id == user_id)).first():
        raise HTTPException(status_code=400, detail="User is referenced in EMRs")

    db.delete(user)
    db.commit()
# ------------------------ APPOINTMENTS ------------------------
def create_appointment(db: Session, appt: schemas.AppointmentCreate):
    if not get_user(db, appt.patient_id):
        raise HTTPException(status_code=400, detail="Invalid patient_id")
    if not get_user(db, appt.doctor_id):
        raise HTTPException(status_code=400, detail="Invalid doctor_id")
    db_appt = models.Appointment(**appt.dict())
    db.add(db_appt)
    db.commit()
    db.refresh(db_appt)
    return db_appt

def get_appointment(db: Session, appt_id: int):
    return db.query(models.Appointment).filter(models.Appointment.appointment_id == appt_id).first()

def get_appointments(db: Session):
    return db.query(models.Appointment).all()

def update_appointment(db: Session, appt_id: int, appt: schemas.AppointmentCreate):
    db_appt = get_appointment(db, appt_id)
    if not db_appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    for key, value in appt.dict().items():
        setattr(db_appt, key, value)
    db.commit()
    return db_appt

def delete_appointment(db: Session, appt_id: int):
    appt = get_appointment(db, appt_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if db.query(models.Prescription).filter(models.Prescription.appointment_id == appt_id).first():
        raise HTTPException(status_code=400, detail="Appointment is referenced in prescriptions")
    db.delete(appt)
    db.commit()

# ------------------------ PRESCRIPTIONS ------------------------
def create_prescription(db: Session, pres: schemas.PrescriptionCreate):
    if not get_appointment(db, pres.appointment_id):
        raise HTTPException(status_code=400, detail="Invalid appointment_id")
    if not get_user(db, pres.doctor_id):
        raise HTTPException(status_code=400, detail="Invalid doctor_id")
    if not get_user(db, pres.patient_id):
        raise HTTPException(status_code=400, detail="Invalid patient_id")

    clean_data = pres.dict()
    clean_data["notes"] = bleach.clean(clean_data["notes"]) if clean_data["notes"] else None
    db_pres = models.Prescription(**clean_data)
    db.add(db_pres)
    db.commit()
    db.refresh(db_pres)
    return db_pres

def get_prescription(db: Session, pres_id: int):
    return db.query(models.Prescription).filter(models.Prescription.prescription_id == pres_id).first()

def get_prescriptions(db: Session):
    return db.query(models.Prescription).all()

def update_prescription(db: Session, pres_id: int, pres: schemas.PrescriptionCreate):
    db_pres = get_prescription(db, pres_id)
    if not db_pres:
        raise HTTPException(status_code=404, detail="Prescription not found")
    for key, value in pres.dict().items():
        setattr(db_pres, key, bleach.clean(value) if key == "notes" and value else value)
    db.commit()
    return db_pres

def delete_prescription(db: Session, pres_id: int):
    pres = get_prescription(db, pres_id)
    if not pres:
        raise HTTPException(status_code=404, detail="Prescription not found")
    db.delete(pres)
    db.commit()

# ------------------------ INVENTORY ------------------------
def create_inventory(db: Session, item: schemas.InventoryCreate):
    clean_data = item.dict()
    clean_data["description"] = bleach.clean(clean_data["description"]) if clean_data["description"] else None
    db_item = models.Inventory(**clean_data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_inventory_item(db: Session, item_id: int):
    return db.query(models.Inventory).filter(models.Inventory.medicine_id == item_id).first()

def get_all_inventory(db: Session):
    return db.query(models.Inventory).all()

def update_inventory(db: Session, item_id: int, item: schemas.InventoryCreate):
    db_item = get_inventory_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.dict().items():
        setattr(db_item, key, bleach.clean(value) if key == "description" and value else value)
    db.commit()
    return db_item

def delete_inventory(db: Session, item_id: int):
    item = get_inventory_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()

# ------------------------ PAYMENTS ------------------------
def create_payment(db: Session, payment: schemas.PaymentCreate):
    if not get_user(db, payment.user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id")
    db_payment = models.Payment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def get_payment(db: Session, payment_id: int):
    return db.query(models.Payment).filter(models.Payment.payment_id == payment_id).first()

def get_all_payments(db: Session):
    return db.query(models.Payment).all()

def update_payment(db: Session, payment_id: int, payment: schemas.PaymentCreate):
    db_payment = get_payment(db, payment_id)
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    for key, value in payment.dict().items():
        setattr(db_payment, key, value)
    db.commit()
    return db_payment

def delete_payment(db: Session, payment_id: int):
    payment = get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    db.delete(payment)
    db.commit()

# ------------------------ LAB TESTS ------------------------
def create_lab_test(db: Session, test: schemas.LabTestCreate):
    if not get_user(db, test.patient_id):
        raise HTTPException(status_code=400, detail="Invalid patient_id")
    clean_data = test.dict()
    clean_data["result"] = bleach.clean(clean_data["result"]) if clean_data["result"] else None
    db_test = models.LabTest(**clean_data)
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

def get_lab_test(db: Session, test_id: int):
    return db.query(models.LabTest).filter(models.LabTest.test_id == test_id).first()

def get_all_lab_tests(db: Session):
    return db.query(models.LabTest).all()

def update_lab_test(db: Session, test_id: int, test: schemas.LabTestCreate):
    db_test = get_lab_test(db, test_id)
    if not db_test:
        raise HTTPException(status_code=404, detail="Lab test not found")
    for key, value in test.dict().items():
        setattr(db_test, key, bleach.clean(value) if key == "result" and value else value)
    db.commit()
    return db_test

def delete_lab_test(db: Session, test_id: int):
    test = get_lab_test(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Lab test not found")
    db.delete(test)
    db.commit()

# ------------------------ EMR ------------------------
def create_emr(db: Session, emr: schemas.EMRCreate):
    if not get_user(db, emr.patient_id):
        raise HTTPException(status_code=400, detail="Invalid patient_id")
    if not get_user(db, emr.doctor_id):
        raise HTTPException(status_code=400, detail="Invalid doctor_id")
    clean_data = emr.dict()
    clean_data["summary"] = bleach.clean(clean_data["summary"]) if clean_data["summary"] else None
    db_emr = models.EMR(**clean_data)
    db.add(db_emr)
    db.commit()
    db.refresh(db_emr)
    return db_emr

def get_emr(db: Session, emr_id: int):
    return db.query(models.EMR).filter(models.EMR.emr_id == emr_id).first()

def get_all_emrs(db: Session):
    return db.query(models.EMR).all()

def update_emr(db: Session, emr_id: int, emr: schemas.EMRCreate):
    db_emr = get_emr(db, emr_id)
    if not db_emr:
        raise HTTPException(status_code=404, detail="EMR not found")
    for key, value in emr.dict().items():
        setattr(db_emr, key, bleach.clean(value) if key == "summary" and value else value)
    db.commit()
    return db_emr

def delete_emr(db: Session, emr_id: int):
    emr = get_emr(db, emr_id)
    if not emr:
        raise HTTPException(status_code=404, detail="EMR not found")
    db.delete(emr)
    db.commit()
