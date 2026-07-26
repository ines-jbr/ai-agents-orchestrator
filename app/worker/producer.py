import aio_pika
import asyncio
import json
import os


async def publish_job(job_id: str, user_request: dict):
    """
    Producer : publie un job dans RabbitMQ.
    Appelé par FastAPI après création du job.
    """
    try:
        # ── Connexion à RabbitMQ ──
        connection = await aio_pika.connect_robust(
            os.environ["RABBITMQ_URL"]
        )

        async with connection:
            channel = await connection.channel()

            # ── Déclarer la queue ──
            await channel.declare_queue(
                "jobs_queue",
                durable=True
            )

            # ── Préparer le message ──
            message_body = json.dumps({
                "job_id"       : job_id,
                "user_request" : user_request
            })

            # ── Publier le message ──
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body          = message_body.encode(),
                    delivery_mode = aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key = "jobs_queue"
            )

            print(f"📤 Job {job_id[:8]}... publié dans RabbitMQ ✅")

    except Exception as e:
        print(f"❌ Erreur publication RabbitMQ : {e}")