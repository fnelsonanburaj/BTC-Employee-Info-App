from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, MetaData
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_, update, delete


DATABASE_URL = "postgresql://<username>:<password>@localhost:5432/<db>"

metadata = MetaData()

engine = create_engine(DATABASE_URL)
SessionMaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class EmployeeModel(Base):
    __tablename__ = "employee"

    id = Column("id", Integer, primary_key=True, index=True, autoincrement=True)
    name = Column("name", String)
    role = Column("role", String)
    
def get_db():
    """
    Function to yield instance of the SessionLocal class will be an Application database session
    """
    db = SessionMaker()
    try:
        yield db
    finally:
        db.close()
        
Base.metadata.create_all(engine)
app = FastAPI()


class EmployeeCreate(BaseModel):
    name: str
    role: str

class EmployeeUpdate(BaseModel):
    name: str
    role: str

class Employee(BaseModel):
    id: int
    name: str
    role: str

@app.get("/health")
async def health():
    return {"message":"Hello from  BTC employee app"}
    
@app.post("/employees")
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    employee_db = EmployeeModel(**employee.dict())
    db.add(employee_db)
    db.commit()
    db.refresh(employee_db)
    return {"data":employee_db, "message":"Created successfully"}

@app.get("/employees/{employee_id}")
async def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee_db = db.query(EmployeeModel).filter(EmployeeModel.id==employee_id).first()
    if employee_db is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee_db

@app.get("/employees")
async def get_employees(db: Session = Depends(get_db)):
    result = db.query(EmployeeModel).all()
    return result

@app.put("/employees/{employee_id}")
async def update_employee(employee_id: int, updated_employee: EmployeeUpdate, db: Session = Depends(get_db)):
    employee_db = db.query(EmployeeModel).filter(EmployeeModel.id==employee_id).first()
    if employee_db is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    employee_db.name = updated_employee.name 
    employee_db.role = updated_employee.role 

    db.commit()
    db.refresh(employee_db)
    return {"data":employee_db, "message":"Updated successfully"}

@app.delete("/employees/{employee_id}")
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee_db = db.get(EmployeeModel, employee_id)
    if employee_db is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.execute(delete(EmployeeModel).where(EmployeeModel.id == employee_id))
    db.commit()
    return {"data":employee_db, "message":"Deleted successfully"}
