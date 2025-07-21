from fastapi import FastAPI
from app.routers import jobs, candidates, jobs_upload, candidates_upload

app = FastAPI(
    title="TalentFlow - Sistema de Seleção Inteligente",
    description="API para seleção inteligente de candidatos usando IA",
    version="1.0.0"
)

app.include_router(jobs.router)
app.include_router(candidates.router)
app.include_router(jobs_upload.router)
app.include_router(candidates_upload.router)