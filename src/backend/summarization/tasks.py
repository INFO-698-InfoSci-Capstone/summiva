from celery import Celery, states
from celery.exceptions import Ignore
from .config import get_settings
from .core.summarizer import summarize_url
from .core.db import AsyncSessionLocal, Summary
import asyncio, logging

cfg = get_settings()
celery_app = Celery(
    "summiva_summarization",
    broker=cfg.broker_url,
    backend=cfg.result_backend,
)
celery_app.conf.update(
    task_soft_time_limit=cfg.task_soft_time_limit,
    task_acks_late=True,
    task_track_started=True,
)

_log = logging.getLogger(__name__)

@celery_app.task(bind=True, name="summiva.summarize_url")
def task_summarize_url(self, url: str):
    _log.info("Starting summarization for %s", url)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:  # no running loop (worker thread)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    try:
        summary = loop.run_until_complete(summarize_url(url))
        
        # Persist to database
        async def _save():
            async with AsyncSessionLocal() as db:
                await db.merge(Summary(url=url, summary=summary))
                await db.commit()
        loop.run_until_complete(_save())
        
        return {"url": url, "summary": summary}
    except Exception as exc:
        _log.exception("Summarization failed: %s", exc)
        self.update_state(state=states.FAILURE, meta=str(exc))
        raise Ignore()