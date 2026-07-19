from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from app.schemas import UserRequest, JobResponse, JobResult, JobStatus
from datetime import datetime
import uuid

load_dotenv()

app = FastAPI(
    title="CL-04 AI Agents Orchestrator",
    description="Orchestration layer — Infrastructure · Cost · DevOps · Deployment",
    version="0.1.0"
)

# ── Stockage temporaire (remplacé par PostgreSQL à l'étape 8) ──
fake_db: dict = {}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "cl-04-orchestrator",
        "version": "0.1.0"
    }


@app.post("/requests", response_model=JobResponse)
def create_request(request: UserRequest):
    """
    Reçoit la demande utilisateur.
    Crée un job → retourne job_id immédiatement.
    """
    job = JobResponse(
        job_id=str(uuid.uuid4()),
        status=JobStatus.PENDING,
        created_at=datetime.utcnow()
    )

    fake_db[job.job_id] = {
        "job":     job,
        "request": request,
        "result":  None
    }

    return job


@app.get("/requests/{job_id}", response_model=JobResult)
def get_request(job_id: str):
    """
    Retourne le statut et résultat d'un job.
    """
    if job_id not in fake_db:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' introuvable"
        )

    stored = fake_db[job_id]
    job    = stored["job"]

    return JobResult(
        job_id     = job.job_id,
        status     = job.status,
        result     = stored["result"],
        created_at = job.created_at
    )