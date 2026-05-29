from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import preview, generate

app = FastAPI(title="RDO Automator API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://rdo.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(preview.router, prefix="/api")
app.include_router(generate.router, prefix="/api")
