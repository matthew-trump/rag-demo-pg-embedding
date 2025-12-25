from __future__ import annotations

from sqlalchemy import cast, func, select
from sqlalchemy.orm import Session

from app.rag.db_types import Embedding
from app.rag.schema import Chunk, Document, EMBEDDING_DIM

def retrieve_top_k(session: Session, query_embedding: list[float], top_k: int) -> list[dict]:
    query_vector = cast(query_embedding, Embedding(EMBEDDING_DIM))
    stmt = (
        select(Chunk.id, Chunk.content, Document.source)
        .join(Document, Document.id == Chunk.document_id)
        .order_by(func.cosine_distance(Chunk.embedding, query_vector))
        .limit(top_k)
    )
    rows = session.execute(stmt).all()
    return [{"id": r.id, "content": r.content, "source": r.source} for r in rows]
