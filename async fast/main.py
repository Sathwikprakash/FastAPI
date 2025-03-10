import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
import uvicorn

uri = "mongodb+srv://sathwikprakash29:Sathwik%401329@cluster0.zrjzw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncIOMotorClient(uri)
db = client['my_database']
collection = db['users']

class User(BaseModel):
    name: str
    phone: str
    age: int
    designation: str

def serialize_user(user):
    if not user:
        return None
    
    
    serialized = user.copy()
    
    
    if '_id' in serialized:
        serialized['_id'] = str(serialized['_id'])
    
    
    if 'created_at' in serialized:
        serialized['created_at'] = serialized['created_at'].isoformat()
    
    return serialized

@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("index.html") as f:
            return f.read()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to load page: {str(e)}"}
        )

@app.post("/api/users/")
async def create_user(user: User):
    try:
        user_dict = user.dict()
        user_dict["created_at"] = datetime.now()
        result = await collection.insert_one(user_dict)
        return JSONResponse(
            status_code=201,
            content={"message": "User created successfully", "id": str(result.inserted_id)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to create user: {str(e)}"}
        )

@app.get("/api/users/search/")
async def search_users(name: Optional[str] = None):
    try:
        query = {"name": {"$regex": name, "$options": "i"}} if name else {}
        cursor = collection.find(query)
        users = await cursor.to_list(length=None)
    
        serialized_users = [serialize_user(user) for user in users]
        return JSONResponse(
            status_code=200,
            content={"users": serialized_users}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to search users: {str(e)}"}
        )

if __name__ == "__main__":
    print("\nStarting the User Management System...")
    print("Access the application at: http://localhost:8080")
    print("Press CTRL+C to stop the server\n")
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)