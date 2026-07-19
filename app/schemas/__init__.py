from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# ════════════════════════════════════
# ENUMS  (ton diagramme : <<enum>>)
# ════════════════════════════════════

class Environment(str, Enum):
    """Environnement cible du déploiement"""
    DEV     = "dev"
    STAGING = "staging"
    PROD    = "prod"


class JobStatus(str, Enum):
    """Cycle de vie d'un job"""
    PENDING     = "pending"
    IN_PROGRESS = "in_progress"
    DONE        = "done"
    ERROR       = "error"


# ════════════════════════════════════
# SCHEMAS  (ton diagramme : <<schema>>)
# ════════════════════════════════════

class UserRequest(BaseModel):
    """
    Ce que l'utilisateur envoie.
    Ton diagramme : <<schema>>UserRequest
    """
    description: str = Field(
        ...,
        description="Besoin infra en langage naturel",
        example="App Node.js, 1000 users/jour, budget 200$/mois"
    )
    environment: Environment = Field(
        default=Environment.DEV,
        description="Environnement cible"
    )
    budget_usd: Optional[float] = Field(
        default=None,
        description="Budget mensuel max en USD"
    )


class JobResponse(BaseModel):
    """
    Ce que FastAPI retourne immédiatement après POST.
    Ton diagramme : <<schema>>JobResponse
    """
    job_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Identifiant unique du job"
    )
    status: JobStatus = Field(
        default=JobStatus.PENDING
    )
    message: str = Field(
        default="Job créé avec succès, traitement en cours..."
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )


class JobResult(BaseModel):
    """
    Ce que l'utilisateur récupère via GET.
    Ton diagramme : <<schema>>JobResult
    result : Dict? → résultats agrégés des 4 agents
    """
    job_id: str
    status: JobStatus
    result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Résultats des 4 agents une fois le job terminé"
    )
    erreur: Optional[str] = Field(
        default=None,
        description="Message d'erreur si status=ERROR"
    )
    created_at: datetime
    updated_at: Optional[datetime] = None