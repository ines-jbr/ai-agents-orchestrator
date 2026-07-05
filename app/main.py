from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()  # charge les variables du fichier .env

app = FastAPI(
    title="AI Agents Orchestrator",
    description="Orchestration layer for infrastructure provisioning, cost optimization and DevOps automation",
    version="0.1.0"
)

@app.get("/health")
def health_check():
    """Vérifie que l'API tourne correctement."""
    return {
        "status": "ok",
        "service": "orchestrator",
        "version": "0.1.0"
    }