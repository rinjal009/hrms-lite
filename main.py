from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date

app = FastAPI(title="HRMS Lite API")

# ---------- DATABASE ----------

engine = create_engine("sqlite:///hrms.db", echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# ---------- MODELS ----------

class Employee(Base):
    __tablename__ = "employees"
    employee_id = Column(String, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    department = Column(String, nullable=False)

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(String, primary_key=True)
    employee_id = Column(String)
    date = Column(String)
    status = Column(String)

Base.metadata.create_all(engine)

# ---------- SCHEMAS ----------

class EmployeeCreate(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    department: str

class AttendanceCreate(BaseModel):
    employee_id: str
    status: str  # Present / Absent


# ---------- EMPLOYEE APIs ----------

@app.post("/employees", status_code=201)
def add_employee(emp: EmployeeCreate):
    db = Session()

    if db.query(Employee).filter_by(employee_id=emp.employee_id).first():
        raise HTTPException(400, "Employee ID already exists")

    new_emp = Employee(**emp.dict())
    db.add(new_emp)
    db.commit()
    return {"message": "Employee added successfully"}


@app.get("/employees")
def list_employees():
    db = Session()
    return db.query(Employee).all()


@app.delete("/employees/{emp_id}")
def delete_employee(emp_id: str):
    db = Session()
    emp = db.query(Employee).filter_by(employee_id=emp_id).first()

    if not emp:
        raise HTTPException(404, "Employee not found")

    db.delete(emp)
    db.commit()
    return {"message": "Employee deleted"}


# ---------- ATTENDANCE APIs ----------

@app.post("/attendance", status_code=201)
def mark_attendance(att: AttendanceCreate):
    db = Session()

    emp = db.query(Employee).filter_by(employee_id=att.employee_id).first()
    if not emp:
        raise HTTPException(404, "Employee does not exist")

    today = str(date.today())
    rec_id = att.employee_id + today

    if db.query(Attendance).filter_by(id=rec_id).first():
        raise HTTPException(400, "Attendance already marked today")

    rec = Attendance(
        id=rec_id,
        employee_id=att.employee_id,
        date=today,
        status=att.status
    )

    db.add(rec)
    db.commit()
    return {"message": "Attendance marked"}


@app.get("/attendance/{emp_id}")
def get_attendance(emp_id: str):
    db = Session()
    return db.query(Attendance).filter_by(employee_id=emp_id).all()


@app.get("/")
def root():
    return {"msg": "HRMS Lite API running"}
