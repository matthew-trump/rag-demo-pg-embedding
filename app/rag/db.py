from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.rag.settings import settings
from app.rag.schema import Base

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db() -> None:
    # Ensure pg_embedding extension exists (no-op if already created)
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_embedding;"))
    Base.metadata.create_all(bind=engine)

    # Attempt to create an HNSW index (safe to fail in constrained envs)
    with engine.begin() as conn:
        try:
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_class c
                        JOIN pg_namespace n ON n.oid = c.relnamespace
                        WHERE c.relname = 'idx_chunks_embedding_hnsw'
                    ) THEN
                        CREATE INDEX idx_chunks_embedding_hnsw
                        ON chunks USING hnsw (embedding);
                    END IF;
                END $$;
            """))
        except Exception:
            # It's fine if this fails (e.g., small demo DB, permissions, etc.)
            pass
