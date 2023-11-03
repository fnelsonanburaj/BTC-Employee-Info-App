from fastapi import FastAPI, HTTPException
import databases
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from pydantic import BaseModel

DATABASE_URL = "postgresql://yourusername:yourpassword@localhost/yourdb"

database = databases.Database(DATABASE_URL)
metadata = MetaData()

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

app = FastAPI()

employee = Table(
    "employee",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String, index=True),
    Column("role", String),
)

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

@app.post("/employees/", response_model=Employee)
async def create_employee(employee: EmployeeCreate):
    query = employee.insert().values(**employee.dict())
    last_record_id = await database.execute(query)
    return {**employee.dict(), "id": last_record_id}

@app.get("/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: int):
    query = employee.select().where(employee.c.id == employee_id)
    result = await database.fetch_one(query)
    if result is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return result

@app.get("/employees/", response_model=list[Employee])
async def get_employees():
    query = employee.select()
    results = await database.fetch_all(query)
    return results

@app.put("/employees/{employee_id}", response_model=Employee)
async def update_employee(employee_id: int, updated_employee: EmployeeUpdate):
    query = employee.select().where(employee.c.id == employee_id)
    existing_employee = await database.fetch_one(query)
    if existing_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    updated_data = updated_employee.dict(exclude_unset=True)
    query = (
        employee
        .update()
        .where(employee.c.id == employee_id)
        .values(**updated_data)
        .returning(employee)
    )
    updated_record = await database.execute(query)
    return updated_record

@app.delete("/employees/{employee_id}", response_model=Employee)
async def delete_employee(employee_id: int):
    query = employee.select().where(employee.c.id == employee_id)
    existing_employee = await database.fetch_one(query)
    if existing_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    query = employee.delete().where(employee.c.id == employee_id)
    deleted_employee = await database.execute(query)
    return existing_employee
