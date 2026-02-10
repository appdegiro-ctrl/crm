from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import init_db
from routes import auth, restaurants, leads, messages, campaigns, products, whatsapp
import uvicorn
import os

app = FastAPI(
    title="SaaS CRM API",
    description="API para SaaS de CRM com WhatsApp",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar banco de dados
try:
    init_db()
    print("Database initialized successfully")
except Exception as e:
    print(f"Error initializing database: {e}")

# Rotas
app.include_router(auth.router)
app.include_router(restaurants.router)
app.include_router(leads.router)
app.include_router(messages.router)
app.include_router(campaigns.router)
app.include_router(products.router)
app.include_router(whatsapp.router)

@app.get("/")
async def root():
    return {
        "message": "SaaS CRM API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)