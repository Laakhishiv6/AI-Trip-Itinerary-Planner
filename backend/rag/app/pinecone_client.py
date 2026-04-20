import time
import logging
import unicodedata
from functools import lru_cache
from pinecone import Pinecone, ServerlessSpec
from .config import settings

log = logging.getLogger(__name__)
BATCH_SIZE = 100


@lru_cache(maxsize=1)
def get_index():
    log.info(f"Connecting to Pinecone index '{settings.pinecone_index_name}'...")
    pc = Pinecone(api_key=settings.pinecone_api_key)

    existing_names = [idx.name for idx in pc.list_indexes()]
    if settings.pinecone_index_name not in existing_names:
        log.info(f"Index not found — creating '{settings.pinecone_index_name}' (dim={settings.embedding_dim})")
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=settings.embedding_dim,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        # Wait until the index is ready to accept writes
        for _ in range(30):
            status = pc.describe_index(settings.pinecone_index_name).status
            if status.get("ready"):
                break
            log.info("Waiting for Pinecone index to become ready...")
            time.sleep(2)

    index = pc.Index(settings.pinecone_index_name)
    log.info("Pinecone index ready")
    return index


def upsert_places(places: list[dict], vectors: list[list[float]]) -> int:
    """Upsert place vectors with metadata into Pinecone."""
    index = get_index()
    records = []
    for place, vec in zip(places, vectors):
        raw_id = f"{place.get('city', 'unknown')}#{place.get('category', '')}#{place.get('name', '')}"
        # Pinecone requires ASCII-only IDs — normalize accented chars then drop any remaining non-ASCII
        vector_id = unicodedata.normalize("NFKD", raw_id).encode("ascii", "ignore").decode("ascii")
        metadata = {
            "city": place.get("city", ""),
            "country": place.get("country", ""),
            "name": place.get("name", ""),
            "category": place.get("category", ""),
            "rating": place.get("rating"),
            "price": place.get("price"),
            "currency": place.get("currency", ""),
            "address": place.get("formatted_address") or place.get("address", ""),
            "website": place.get("website", ""),
            "cuisine": place.get("cuisine", ""),
            "lat": place.get("lat"),
            "lon": place.get("lon"),
        }
        # Pinecone metadata values must be str / int / float / bool / list[str]
        metadata = {
            k: v
            for k, v in metadata.items()
            if v is not None and v != "" and not (isinstance(v, float) and v != v)  # drop NaN
        }
        records.append({"id": vector_id, "values": vec, "metadata": metadata})

    upserted = 0
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        index.upsert(vectors=batch)
        upserted += len(batch)
        log.info(f"Upserted batch {i // BATCH_SIZE + 1} ({upserted}/{len(records)})")
    return upserted


def query_index(
    vector: list[float],
    top_k: int = 10,
    filter: dict | None = None,
) -> list[dict]:
    index = get_index()
    kwargs = {"vector": vector, "top_k": top_k, "include_metadata": True}
    if filter:
        kwargs["filter"] = filter
    resp = index.query(**kwargs)
    return [
        {"score": match.score, **match.metadata}
        for match in resp.matches
    ]
