from fastapi import FastAPI
import uvicorn
from routes import router


app = FastAPI()

app.include_router(router)


if __name__== "__main__":
    uvicorn.run(app, host="192.168.1.9",port=8080)