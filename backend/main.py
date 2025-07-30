from fastapi import FastAPI
from .routes import router

app = FastAPI()

@app.get('/ping')
def ping():
    return {'status': 'ok'}

app.include_router(router)
