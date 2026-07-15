import json
import asyncio
from typing import Any, Dict
from app.core.redis import get_redis
from app.core.logging import get_logger

logger = get_logger(__name__)

QUEUE_NAME = "platform:jobs"

async def enqueue(job_type: str, payload: Dict[str, Any]) -> bool:
    """Add a job to the queue. Returns True on success."""
    try:
        r = await get_redis()
        job = json.dumps({
            "type": job_type,
            "payload": payload,
        })
        await r.rpush(QUEUE_NAME, job)
        logger.info("job_enqueued", job_type=job_type, payload=payload)
        return True
    except Exception as e:
        logger.error("job_enqueue_failed", job_type=job_type, error=str(e))
        return False

async def process_job(job: dict):
    """Process a single job based on its type."""
    job_type = job.get("type")
    payload = job.get("payload", {})

    logger.info("job_started", job_type=job_type)

    if job_type == "send_welcome_email":
        # Simulate sending email
        await asyncio.sleep(0.1)
        logger.info(
            "welcome_email_sent",
            to=payload.get("email"),
            user_id=payload.get("user_id")
        )

    elif job_type == "notify_slack":
        await asyncio.sleep(0.05)
        logger.info(
            "slack_notified",
            channel=payload.get("channel"),
            message=payload.get("message")
        )

    else:
        logger.warning("unknown_job_type", job_type=job_type)

    logger.info("job_completed", job_type=job_type)

async def run_worker():
    """
    Background worker that continuously processes jobs.
    Run this as a separate process in production.
    """
    logger.info("worker_started", queue=QUEUE_NAME)
    r = await get_redis()

    while True:
        try:
            # Block up to 5 seconds waiting for a job
            result = await r.blpop(QUEUE_NAME, timeout=5)
            if result:
                _, job_json = result
                job = json.loads(job_json)
                await process_job(job)
        except Exception as e:
            logger.error("worker_error", error=str(e))
            await asyncio.sleep(1)
