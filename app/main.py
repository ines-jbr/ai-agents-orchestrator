from fastapi import FastAPI, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from datetime import datetime
import uuid

from app.schemas import (
    UserRequest, JobResponse,
    JobResult, JobStatus
)
from app.orchestrator import run_orchestrator

load_dotenv()

# ════════════════════════════════════════════
# APP FASTAPI
# ════════════════════════════════════════════
app = FastAPI(
    title="CL-04 AI Agents Orchestrator",
    description="""
    Orchestration layer that coordinates multiple
    specialized AI agents for :

    - 🏗️  Infrastructure Provisioning
    - 💰  Cost Optimization
    - ⚙️  DevOps Automation
    - 🚀  Deployment
    """,
    version="0.1.0"
)

# ════════════════════════════════════════════
# FAKE DB
# (remplacé par PostgreSQL à l'étape 9)
# ════════════════════════════════════════════
fake_db: dict = {}


# ════════════════════════════════════════════
# BACKGROUND TASK
# ════════════════════════════════════════════
def process_job(job_id: str, user_request: dict):
    """
    Tâche arrière-plan :
    ① Met le job en IN_PROGRESS
    ② Lance l'orchestrateur LangGraph
    ③ Sauvegarde le résultat
    ④ Met le statut en DONE ou ERROR
    """
    try:
        # ── ① IN_PROGRESS ──
        fake_db[job_id]["status"]     = JobStatus.IN_PROGRESS
        fake_db[job_id]["updated_at"] = datetime.utcnow()
        print(f"\n🔄 Job {job_id[:8]}... → IN_PROGRESS")

        # ── ② Lancer l'orchestrateur ──
        result = run_orchestrator(user_request)

        # ── ③ Sauvegarder le résultat ──
        fake_db[job_id]["status"]     = JobStatus.DONE
        fake_db[job_id]["result"]     = result
        fake_db[job_id]["updated_at"] = datetime.utcnow()
        print(f"✅ Job {job_id[:8]}... → DONE")

    except Exception as e:
        # ── ④ En cas d'erreur ──
        fake_db[job_id]["status"]     = JobStatus.ERROR
        fake_db[job_id]["error"]      = str(e)
        fake_db[job_id]["updated_at"] = datetime.utcnow()
        print(f"❌ Job {job_id[:8]}... → ERROR : {e}")


# ════════════════════════════════════════════
# ENDPOINTS
# ════════════════════════════════════════════

@app.get(
    "/health",
    tags=["System"]
)
def health_check():
    """
    Vérifie que l'API tourne correctement.
    """
    return {
        "status"      : "ok",
        "service"     : "cl-04-orchestrator",
        "version"     : "0.1.0",
        "total_jobs"  : len(fake_db),
        "agents"      : [
            "provisioning",
            "cost_optimization",
            "devops",
            "deployment"
        ]
    }


@app.post(
    "/requests",
    response_model=JobResponse,
    status_code=201,
    tags=["Requests"]
)
def create_request(
    request: UserRequest,
    background_tasks: BackgroundTasks
):
    """
    Soumet une demande d'infrastructure.

    - Crée un job avec statut **PENDING**
    - Lance l'orchestrateur en **arrière-plan**
    - Retourne un **job_id** immédiatement

    Utilise ensuite **GET /requests/{job_id}**
    pour suivre le statut.
    """
    job_id = str(uuid.uuid4())

    # ── Sauvegarder dans fake_db ──
    fake_db[job_id] = {
        "job_id"     : job_id,
        "status"     : JobStatus.PENDING,
        "request"    : request.model_dump(),
        "result"     : None,
        "error"      : None,
        "created_at" : datetime.utcnow(),
        "updated_at" : None,
    }

    # ── Lancer l'orchestrateur en arrière-plan ──
    background_tasks.add_task(
        process_job,
        job_id,
        request.model_dump()
    )

    print(f"\n📥 Nouvelle requête → job_id: {job_id[:8]}...")

    return JobResponse(
        job_id     = job_id,
        status     = JobStatus.PENDING,
        created_at = fake_db[job_id]["created_at"]
    )


@app.get(
    "/requests/{job_id}",
    response_model=JobResult,
    tags=["Requests"]
)
def get_request(job_id: str):
    """
    Retourne le statut et résultat d'un job.

    **Statuts possibles :**
    - `pending`     → job créé, pas encore traité
    - `in_progress` → agents en train de travailler
    - `done`        → résultat prêt ✅
    - `error`       → une erreur s'est produite ❌
    """
    if job_id not in fake_db:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' introuvable"
        )

    job = fake_db[job_id]

    return JobResult(
        job_id     = job["job_id"],
        status     = job["status"],
        result     = job["result"],
        erreur     = job["error"],
        created_at = job["created_at"],
        updated_at = job.get("updated_at")
    )


@app.get(
    "/requests",
    tags=["Requests"]
)
def list_requests():
    """
    Liste tous les jobs avec leur statut.
    """
    jobs = [
        {
            "job_id"     : job["job_id"],
            "status"     : job["status"],
            "created_at" : job["created_at"],
            "updated_at" : job.get("updated_at"),
        }
        for job in fake_db.values()
    ]

    return {
        "total" : len(jobs),
        "jobs"  : jobs
    }


@app.delete(
    "/requests/{job_id}",
    tags=["Requests"]
)
def delete_request(job_id: str):
    """
    Supprime un job de la base de données.
    """
    if job_id not in fake_db:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' introuvable"
        )

    del fake_db[job_id]

    return {
        "message" : f"Job '{job_id}' supprimé avec succès"
    }