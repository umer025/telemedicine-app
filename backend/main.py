from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base, get_db
import models, schemas, crud
from auth import router as auth_router, get_current_user, require_role
from schemas import RoleEnum
from prometheus_fastapi_instrumentator import Instrumentator

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Telemedicine Secure API")
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# Mount Auth Router
app.include_router(auth_router)

# ---------------- USERS ----------------

@app.get("/users/", response_model=list[schemas.UserOut])
def read_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # ✅ Allow all roles initially
):
    if current_user.role not in [RoleEnum.Admin, RoleEnum.Doctor]:
        raise HTTPException(status_code=403, detail="Access denied")
    return crud.get_users(db)

@app.get("/users/{user_id}", response_model=schemas.UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users/", response_model=schemas.UserOut, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int, 
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Admin))
):
    return crud.update_user(db, user_id, user)

@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Admin))
):
    crud.delete_user(db, user_id)
    return {"detail": "User deleted"}

# ---------------- APPOINTMENTS ----------------
@app.get("/appointments/", response_model=list[schemas.AppointmentOut])
def read_appointments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role == RoleEnum.Patient:
        return db.query(models.Appointment).filter(models.Appointment.patient_id == current_user.user_id).all()
    return crud.get_appointments(db)

@app.get("/appointments/{appointment_id}", response_model=schemas.AppointmentOut)
def read_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = crud.get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt

@app.post("/appointments/", response_model=schemas.AppointmentOut, status_code=201)
def create_appointment(
    appt: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in [RoleEnum.Admin, RoleEnum.Doctor]:
        raise HTTPException(status_code=403, detail="Access denied")
    return crud.create_appointment(db, appt)

@app.put("/appointments/{appointment_id}", response_model=schemas.AppointmentOut)
def update_appointment(
    appointment_id: int,
    appt: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in [RoleEnum.Admin, RoleEnum.Doctor]:
        raise HTTPException(status_code=403, detail="Access denied")
    return crud.update_appointment(db, appointment_id, appt)

@app.delete("/appointments/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in [RoleEnum.Admin, RoleEnum.Doctor]:
        raise HTTPException(status_code=403, detail="Access denied")
    crud.delete_appointment(db, appointment_id)
    return {"detail": "Appointment deleted"}


# ---------------- PRESCRIPTIONS ----------------
@app.get("/prescriptions/", response_model=list[schemas.PrescriptionOut])
def read_prescriptions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role == RoleEnum.Patient:
        return db.query(models.Prescription).filter(models.Prescription.patient_id == current_user.user_id).all()
    return crud.get_prescriptions(db)

@app.get("/prescriptions/{prescription_id}", response_model=schemas.PrescriptionOut)
def read_prescription(prescription_id: int, db: Session = Depends(get_db)):
    pres = crud.get_prescription(db, prescription_id)
    if not pres:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return pres

@app.post("/prescriptions/", response_model=schemas.PrescriptionOut, status_code=201)
def create_prescription(
    pres: schemas.PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Doctor))
):
    return crud.create_prescription(db, pres)

@app.put("/prescriptions/{prescription_id}", response_model=schemas.PrescriptionOut)
def update_prescription(
    prescription_id: int,
    pres: schemas.PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Doctor))
):
    return crud.update_prescription(db, prescription_id, pres)

@app.delete("/prescriptions/{prescription_id}")
def delete_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Doctor))
):
    crud.delete_prescription(db, prescription_id)
    return {"detail": "Prescription deleted"}

# ---------------- LAB TESTS ----------------
@app.get("/lab-tests/", response_model=list[schemas.LabTestOut])
def read_lab_tests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role == RoleEnum.Patient:
        return db.query(models.LabTest).filter(models.LabTest.patient_id == current_user.user_id).all()
    return crud.get_all_lab_tests(db)

@app.get("/lab-tests/{test_id}", response_model=schemas.LabTestOut)
def read_lab_test(test_id: int, db: Session = Depends(get_db)):
    test = crud.get_lab_test(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Lab test not found")
    return test

@app.post("/lab-tests/", response_model=schemas.LabTestOut, status_code=201)
def create_lab_test(
    test: schemas.LabTestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Doctor))
):
    return crud.create_lab_test(db, test)

@app.put("/lab-tests/{test_id}", response_model=schemas.LabTestOut)
def update_lab_test(
    test_id: int,
    test: schemas.LabTestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Doctor))
):
    return crud.update_lab_test(db, test_id, test)

@app.delete("/lab-tests/{test_id}")
def delete_lab_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Doctor))
):
    crud.delete_lab_test(db, test_id)
    return {"detail": "Lab test deleted"}

# ---------------- EMR ----------------
@app.get("/emr/", response_model=list[schemas.EMROut])
def read_emrs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role == RoleEnum.Patient:
        return db.query(models.EMR).filter(models.EMR.patient_id == current_user.user_id).all()
    return crud.get_all_emrs(db)

@app.get("/emr/{emr_id}", response_model=schemas.EMROut)
def read_emr(emr_id: int, db: Session = Depends(get_db)):
    emr = crud.get_emr(db, emr_id)
    if not emr:
        raise HTTPException(status_code=404, detail="EMR not found")
    return emr

@app.post("/emr/", response_model=schemas.EMROut, status_code=201)
def create_emr(
    emr: schemas.EMRCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Doctor))
):
    return crud.create_emr(db, emr)

@app.put("/emr/{emr_id}", response_model=schemas.EMROut)
def update_emr(
    emr_id: int,
    emr: schemas.EMRCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Doctor))
):
    return crud.update_emr(db, emr_id, emr)

@app.delete("/emr/{emr_id}")
def delete_emr(
    emr_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Doctor))
):
    crud.delete_emr(db, emr_id)
    return {"detail": "EMR deleted"}

# ---------------- INVENTORY ----------------
@app.get("/inventory/", response_model=list[schemas.InventoryOut])
def read_inventory(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Admin))
):
    return crud.get_all_inventory(db)

@app.get("/inventory/{item_id}", response_model=schemas.InventoryOut)
def read_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Admin))
):
    item = crud.get_inventory_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item

@app.post("/inventory/", response_model=schemas.InventoryOut, status_code=201)
def create_inventory(
    item: schemas.InventoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Admin))
):
    return crud.create_inventory(db, item)

@app.put("/inventory/{item_id}", response_model=schemas.InventoryOut)
def update_inventory(
    item_id: int,
    item: schemas.InventoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Admin))
):
    return crud.update_inventory(db, item_id, item)

@app.delete("/inventory/{item_id}")
def delete_inventory(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Admin))
):
    crud.delete_inventory(db, item_id)
    return {"detail": "Inventory item deleted"}

# ---------------- PAYMENTS ----------------
@app.get("/payments/", response_model=list[schemas.PaymentOut])
def read_payments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Admin))
):
    return crud.get_all_payments(db)

@app.get("/payments/{payment_id}", response_model=schemas.PaymentOut)
def read_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Admin))
):
    payment = crud.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@app.post("/payments/", response_model=schemas.PaymentOut, status_code=201)
def create_payment(
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Admin))
):
    return crud.create_payment(db, payment)

@app.put("/payments/{payment_id}", response_model=schemas.PaymentOut)
def update_payment(
    payment_id: int,
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Admin))
):
    return crud.update_payment(db, payment_id, payment)

@app.delete("/payments/{payment_id}")
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.Admin))
):
    crud.delete_payment(db, payment_id)
    return {"detail": "Payment deleted"}
