from sqlalchemy.orm import Session
import models, schemas

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def get_users(db: Session):
    return db.query(models.User).all()

def update_user(db: Session, user_id: int, user: schemas.UserCreate):
    db_user = get_user(db, user_id)
    for key, value in user.dict().items():
        setattr(db_user, key, value)
    db.commit()
    return db_user

def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    db.delete(user)
    db.commit()

def create_appointment(db: Session, appt: schemas.AppointmentCreate):
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
    for key, value in appt.dict().items():
        setattr(db_appt, key, value)
    db.commit()
    return db_appt

def delete_appointment(db: Session, appt_id: int):
    appt = get_appointment(db, appt_id)
    db.delete(appt)
    db.commit()

def create_prescription(db: Session, pres: schemas.PrescriptionCreate):
    db_pres = models.Prescription(**pres.dict())
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
    for key, value in pres.dict().items():
        setattr(db_pres, key, value)
    db.commit()
    return db_pres

def delete_prescription(db: Session, pres_id: int):
    pres = get_prescription(db, pres_id)
    db.delete(pres)
    db.commit()
