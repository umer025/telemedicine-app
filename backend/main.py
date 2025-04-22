
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import database, models, schemas, crud
from database import engine, Base, SessionLocal

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.get("/users/", response_model=list[schemas.UserOut])
def read_users(db: Session = Depends(get_db)):
    return crud.get_users(db)

@app.get("/users/{user_id}", response_model=schemas.UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.update_user(db, user_id, user)

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    crud.delete_user(db, user_id)
    return {"detail": "User deleted"}

@app.post("/appointments/", response_model=schemas.AppointmentOut)
def create_appointment(appt: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    return crud.create_appointment(db, appt)

@app.get("/appointments/", response_model=list[schemas.AppointmentOut])
def read_appointments(db: Session = Depends(get_db)):
    return crud.get_appointments(db)

@app.get("/appointments/{appointment_id}", response_model=schemas.AppointmentOut)
def read_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = crud.get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt

@app.put("/appointments/{appointment_id}", response_model=schemas.AppointmentOut)
def update_appointment(appointment_id: int, appt: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    return crud.update_appointment(db, appointment_id, appt)

@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    crud.delete_appointment(db, appointment_id)
    return {"detail": "Appointment deleted"}

@app.post("/prescriptions/", response_model=schemas.PrescriptionOut)
def create_prescription(pres: schemas.PrescriptionCreate, db: Session = Depends(get_db)):
    return crud.create_prescription(db, pres)

@app.get("/prescriptions/", response_model=list[schemas.PrescriptionOut])
def read_prescriptions(db: Session = Depends(get_db)):
    return crud.get_prescriptions(db)

@app.get("/prescriptions/{prescription_id}", response_model=schemas.PrescriptionOut)
def read_prescription(prescription_id: int, db: Session = Depends(get_db)):
    pres = crud.get_prescription(db, prescription_id)
    if not pres:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return pres

@app.put("/prescriptions/{prescription_id}", response_model=schemas.PrescriptionOut)
def update_prescription(prescription_id: int, pres: schemas.PrescriptionCreate, db: Session = Depends(get_db)):
    return crud.update_prescription(db, prescription_id, pres)

@app.delete("/prescriptions/{prescription_id}")
def delete_prescription(prescription_id: int, db: Session = Depends(get_db)):
    crud.delete_prescription(db, prescription_id)
    return {"detail": "Prescription deleted"}
