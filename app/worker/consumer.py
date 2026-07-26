import aio_pika
import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from app.orchestrator import run_orchestrator
from app.schemas import JobStatus

# ── Base de données partagée ──
jobs_db: dict = {}


async def process_message(message: aio_pika.IncomingMessage):
    """
    Consumer : traite un message reçu de RabbitMQ.
    """
    async with message.process():
        job_id = None
        try:
            # ── Décoder le message ──
            body         = json.loads(message.body.decode())
            job_id       = body["job_id"]
            user_request = body["user_request"]

            print(f"\n📨 Message reçu → job_id: {job_id[:8]}...")

            # ── Mettre à jour le statut ──
            jobs_db[job_id] = {
                "status"     : JobStatus.IN_PROGRESS,
                "updated_at" : datetime.utcnow()
            }
            print(f"🔄 Job {job_id[:8]}... → IN_PROGRESS")

            # ── Lancer l'orchestrateur ──
            result = run_orchestrator(user_request)

            # ── Sauvegarder le résultat ──
            jobs_db[job_id] = {
                "status"     : JobStatus.DONE,
                "result"     : result,
                "updated_at" : datetime.utcnow()
            }
            print(f"✅ Job {job_id[:8]}... → DONE")

        except Exception as e:
            print(f"❌ Erreur : {e}")
            if job_id:
                jobs_db[job_id] = {
                    "status"     : JobStatus.ERROR,
                    "error"      : str(e),
                    "updated_at" : datetime.utcnow()
                }


async def start_worker():
    """
    Lance le worker — écoute la queue en permanence.
    """
    print("🐰 Worker démarré — connexion à RabbitMQ...")

    connection = await aio_pika.connect_robust(
        os.environ["RABBITMQ_URL"]
    )

    async with connection:
        channel = await connection.channel()

        # ── 1 message à la fois ──
        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue(
            "jobs_queue",
            durable=True
        )

        await queue.consume(process_message)

        print("✅ Worker connecté à RabbitMQ !")
        print("⏳ En attente de jobs...\n")

        # ── Garder le worker actif ──
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(start_worker())