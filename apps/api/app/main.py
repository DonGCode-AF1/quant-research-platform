from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.api import router

app = FastAPI(title="Quant Research Platform API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
