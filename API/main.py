from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
import psutil
import os
from utils.main import Burp
from typing import Optional, Dict

app = FastAPI()
DB = None
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield 
    
@app.get("/")
async def home():
    res = {}
    res["total CPU cores"] = psutil.cpu_count(logical=False)
    res["Total cpu threads"] = psutil.cpu_count()
    return res

@app.get("/createDatabase")
async def create(database_name: str, encoding : str = None, save: str = "auto"):
    global DB
    if DB is not None:
        return f"Database with name : {DB.db_name} already exists"
    DB = Burp()
    try:
        DB.create_database(database_name, encoding, save)
        return f"Database created with name: {database_name}"
    except Exception as e:
        return e

@app.get("/createTable")
async def createTable(table_name: str, extension: str = None, auto_increment=True, encrypt=False):
    if DB is None:
        return "First create a database"
    try:
        DB.create_table(table_name, extension, auto_increment, encrypt)
    except Exception as e:
        return e
    return f"The table with name : {table_name} is created."

@app.post("/addData")
async def setVal(data: dict):
    if DB is None: return "Create a Database first"
    uid = DB.add_one(data)
    return uid

@app.get("/getSingle")
async def getSingle(id: int):
    if DB is None: return "Create a Database first"
    data = DB.get_one(id)
    return data 

@app.get("/getAll")
async def getAll():
    if DB is None: return "Create a Database first"
    data = DB.get_all()
    return data

@app.get("/saveSnapshot")
async def saveSnapshot():
    if DB is None: return "Create a Database first"
    status = DB.save_snapshot()
    return status

@app.post("/updateData")
async def updateData(id: int, data: dict):
    if DB is None: return "Create a Database first"
    data = DB.update(id, data)
    return data 

@app.delete("/deleteData")
async def deleteData(id: int):
    if DB is None: return "Create a Database first"
    status = DB.delete(id)
    return status

@app.get("/loadData")
async def load_data(database_name: str, table_name: str, encrypt: bool = None, key: str = ""):
    global DB
    if DB is not None: return f"Database with name {DB.db_name} already exists"
    if DB is None:
        DB = Burp()
    status = DB.load_data(database_name, table_name, encrypt, key)
    return status

@app.delete("/deleteTable")
async def deleteTable():
    if DB is None: return "Create a Database first"
    return DB.delete_table()

@app.get("/getKey")
async def getKey():
    if DB is None: return "Create a Database first"
    return DB.encryption_key

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)