from fastapi import FastAPI
import uvicorn
from routes import router
from bson import ObjectId

app = FastAPI()

app.include_router(router)


if __name__== "__main__":
    uvicorn.run(app, host="127.0.0.1",port=8080)