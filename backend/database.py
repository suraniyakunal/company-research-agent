# backend/database.py

import logging
import os
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    create_engine,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Session

logger = logging.getLogger(__name__)

DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

# Module-level engine — None when DATABASE_URL is absent (local dev without DB).
engine = None


class Base(DeclarativeBase):
    pass


class ResearchEvent(Base):
    """One row per /research request (successful or failed)."""

    __tablename__ = "research_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String, nullable=True)   # anonymous browser UUID
    company_name = Column(String, nullable=False)
    fit_score = Column(Integer, nullable=True)    # None on failure
    is_byok = Column(Boolean, nullable=False)
    success = Column(Boolean, nullable=False)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )


def init_db() -> None:
    """Call once at application startup. No-ops gracefully if DATABASE_URL is unset."""
    global engine
    if not DATABASE_URL:
        logger.warning(
            "DATABASE_URL not set — analytics tracking is disabled. "
            "Add a PostgreSQL plugin on Railway and set DATABASE_URL to enable it."
        )
        return
    try:
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(engine)
        logger.info("Database initialised and schema applied.")
    except Exception:
        logger.exception("Failed to initialise database — tracking disabled.")
        engine = None


def log_event(
    *,
    session_id: Optional[str],
    company_name: str,
    fit_score: Optional[int],
    is_byok: bool,
    success: bool,
    duration_ms: int,
) -> None:
    """Fire-and-forget: insert one research event. Swallows all DB errors."""
    if engine is None:
        return
    try:
        with Session(engine) as db:
            db.add(
                ResearchEvent(
                    session_id=session_id,
                    company_name=company_name,
                    fit_score=fit_score,
                    is_byok=is_byok,
                    success=success,
                    duration_ms=duration_ms,
                )
            )
            db.commit()
    except Exception:
        logger.exception("Failed to write research event — continuing without logging.")


def get_stats(detailed: bool = False) -> dict:
    """
    Return aggregate analytics.  Always returns a valid dict even when the DB
    is unavailable — callers never need to handle None.

    ``detailed=True`` adds day-by-day activity and BYOK breakdown for the
    private /analytics dashboard.
    """
    _empty: dict = {
        "total_searches": 0,
        "unique_sessions": 0,
        "success_rate": 0.0,
        "searches_last_7_days": 0,
        "searches_last_30_days": 0,
        "top_companies": [],
    }

    if engine is None:
        return _empty

    try:
        with Session(engine) as db:
            total: int = db.execute(
                text("SELECT COUNT(*) FROM research_events")
            ).scalar() or 0

            unique_sessions: int = db.execute(
                text(
                    "SELECT COUNT(DISTINCT session_id) FROM research_events "
                    "WHERE session_id IS NOT NULL"
                )
            ).scalar() or 0

            successful: int = db.execute(
                text("SELECT COUNT(*) FROM research_events WHERE success = TRUE")
            ).scalar() or 0

            last_7: int = db.execute(
                text(
                    "SELECT COUNT(*) FROM research_events "
                    "WHERE created_at >= NOW() - INTERVAL '7 days'"
                )
            ).scalar() or 0

            last_30: int = db.execute(
                text(
                    "SELECT COUNT(*) FROM research_events "
                    "WHERE created_at >= NOW() - INTERVAL '30 days'"
                )
            ).scalar() or 0

            top_rows = db.execute(
                text(
                    "SELECT company_name, COUNT(*) AS cnt "
                    "FROM research_events WHERE success = TRUE "
                    "GROUP BY company_name ORDER BY cnt DESC LIMIT 10"
                )
            ).fetchall()
            top_companies = [{"name": r[0], "count": r[1]} for r in top_rows]

            result: dict = {
                "total_searches": total,
                "unique_sessions": unique_sessions,
                "success_rate": round(successful / total, 2) if total else 0.0,
                "searches_last_7_days": last_7,
                "searches_last_30_days": last_30,
                "top_companies": top_companies,
            }

            if detailed:
                prev_7: int = db.execute(
                    text(
                        "SELECT COUNT(*) FROM research_events "
                        "WHERE created_at >= NOW() - INTERVAL '14 days' "
                        "  AND created_at <  NOW() - INTERVAL '7 days'"
                    )
                ).scalar() or 0

                daily_rows = db.execute(
                    text(
                        "SELECT DATE(created_at) AS day, COUNT(*) AS cnt "
                        "FROM research_events "
                        "WHERE created_at >= NOW() - INTERVAL '30 days' "
                        "GROUP BY DATE(created_at) ORDER BY day"
                    )
                ).fetchall()

                byok_count: int = db.execute(
                    text(
                        "SELECT COUNT(*) FROM research_events WHERE is_byok = TRUE"
                    )
                ).scalar() or 0

                avg_dur = db.execute(
                    text(
                        "SELECT AVG(duration_ms) FROM research_events WHERE success = TRUE"
                    )
                ).scalar()

                result.update(
                    {
                        "searches_prev_7_days": prev_7,
                        "daily_activity": [
                            {"date": str(r[0]), "count": r[1]} for r in daily_rows
                        ],
                        "byok_count": byok_count,
                        "free_count": total - byok_count,
                        "avg_duration_ms": round(avg_dur) if avg_dur else 0,
                    }
                )

            return result

    except Exception:
        logger.exception("Failed to read stats from database.")
        return _empty
