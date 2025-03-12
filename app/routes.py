from fastapi import APIRouter
from  motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId


router=APIRouter() 

client = AsyncIOMotorClient("mongodb://mongotest:mongotest@localhost:27017/")
db = client["mynddatabase"]
collection = db["tenders"]


def id_to_string(mongo_objs):
    for mongo_obj in mongo_objs:
     mongo_obj['_id'] = str(mongo_obj['_id'])
    return mongo_objs

@router.get("/")
async def home_page():
    return {"Hello again with no knowledge "}

@router.get("/all/objects")
async def show_all():
    items= await collection.find().to_list(None)
    return {"items": id_to_string(items)} 


@router.delete("/delete/{obj_id}")
async def delete_obj(obj_id: str):
   delete_obj=await collection.delete_one({"_id":ObjectId(obj_id)})
   if delete_obj.deleted_count==1:
      return {"result": "the object got deleted successfully"}
   else:
      return {"result":"fatal error #####"}