from app.api.v1.transactions import router
from app.core.config import app

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de BTG Pactual"}
