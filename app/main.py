from fastapi import FastAPI
import uvicorn
from  motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["mynddatabase"]
collection = db["tenders"]

def id_to_string(mongo_obj):
    mongo_obj['_id'] = str(mongo_obj['_id'])
    return mongo_obj

@app.get("/")
async def home_page():
    return {"Hello again with no knowledge "}

@app.get("/all/objects")
async def show_all():
    items= await collection.find().to_list(None)
    return {"items": items} 

if __name__== "__main__":
    uvicorn.run(app, host="127.0.0.1",port=8080)