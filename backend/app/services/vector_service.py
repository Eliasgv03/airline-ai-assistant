"""
Vector Store Service

This module handles the RAG (Retrieval-Augmented Generation) pipeline:
1. Loading documents from the knowledge base.
2. Splitting text into chunks.
3. Generating embeddings using Google Gemini.
4. Storing and retrieving vectors using pgvector.
"""

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings
from app.db.database import db_url
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


class VectorService:
    def __init__(self):
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        logger.info("Initializing VectorService...")

        # Build list of available API keys (fallback chain)
        api_keys: list[tuple[str, str]] = []  # (key, description)

        if settings.GOOGLE_EMBEDDING_API_KEY:
            api_keys.append((settings.GOOGLE_EMBEDDING_API_KEY, "GOOGLE_EMBEDDING_API_KEY"))
        if settings.GOOGLE_API_KEY:
            api_keys.append((settings.GOOGLE_API_KEY, "GOOGLE_API_KEY"))
        if settings.GOOGLE_FALLBACK_API_KEY:
            api_keys.append((settings.GOOGLE_FALLBACK_API_KEY, "GOOGLE_FALLBACK_API_KEY"))

        if not api_keys:
            raise ValueError(
                "No Google API key configured. "
                "Set GOOGLE_EMBEDDING_API_KEY, GOOGLE_API_KEY, or GOOGLE_FALLBACK_API_KEY."
            )

        # Try each API key until one works
        last_error: Exception | None = None
        for api_key, key_name in api_keys:
            try:
                logger.info(f"🔗 Trying {key_name} for embeddings ({settings.EMBEDDING_MODEL})...")
                # Set API key via environment variable to avoid SecretStr/gRPC issues
                import os

                os.environ["GOOGLE_API_KEY"] = str(api_key)
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model=settings.EMBEDDING_MODEL,
                )  # type: ignore
                logger.info(f"✅ Google Embeddings API connected with {key_name}")
                break
            except Exception as e:
                logger.warning(f"⚠️ {key_name} failed for embeddings: {e}")
                last_error = e
                continue
        else:
            # All keys failed
            logger.error("❌ All API keys failed for embeddings")
            if last_error:
                raise last_error
            raise ValueError("Failed to initialize embeddings with any API key")

        # PGVector instance
        # connecting strictly with the sync driver string or valid connection info
        # langchain-postgres usually handles the connection string.
        # Ensure db_url is a string.
        connection_string = str(db_url)

        # PGVector from langchain-postgres requests a specific connection format or engine.
        # But for simplicity in this version, passing the connection string usually works
        # if the driver (psycopg 3) is installed.
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name=settings.VECTOR_STORE_COLLECTION_NAME,
            connection=connection_string,
            use_jsonb=True,
        )

    def load_documents(self, directory_path: str) -> list[Document]:
        """Loads markdown files from a directory."""
        logger.info(f"Loading documents from {directory_path}")
        loader = DirectoryLoader(directory_path, glob="**/*.md", loader_cls=TextLoader)
        return loader.load()

    def split_documents(self, documents: list[Document]) -> list[Document]:
        """Splits documents into smaller chunks for flexible retrieval."""
        logger.info(f"Splitting {len(documents)} documents...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, separators=["\n## ", "\n### ", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Generated {len(chunks)} chunks.")
        return chunks

    def ingest_data(self, directory_path: str):
        """Orchestrates loading, splitting, and storing documents."""
        docs = self.load_documents(directory_path)
        chunks = self.split_documents(docs)

        if not chunks:
            logger.warning("No chunks to ingest.")
            return

        import time

        logger.info(f"Adding {len(chunks)} chunks to vector store...")

        # Batching to avoid Rate Limit (429) - Extreme Conservative
        batch_size = 1
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            logger.info(
                f"Ingesting batch {i // batch_size + 1}/{len(chunks) // batch_size + 1} ({len(batch)} chunks)..."
            )
            try:
                self.vector_store.add_documents(batch)
            except Exception as e:
                logger.error(f"Error adding batch: {e}")
                # Wait longer if error
                time.sleep(10)
                continue
            time.sleep(5)  # Sleep to respect rate limits

        logger.info("Ingestion complete.")

    def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        """Searches the vector store for relevant chunks."""
        return self.vector_store.similarity_search(query, k=k)

    def as_retriever(self):
        """Returns the vector store as a retriever interface."""
        return self.vector_store.as_retriever()


# Singleton instance - ensures embedding model is loaded only once
_vector_service: VectorService | None = None


def get_vector_service() -> VectorService:
    """
    Get the global VectorService instance (singleton).

    This is critical for production: the embedding model takes ~70 seconds
    to load, so we only want to load it once, not on every request.
    """
    global _vector_service
    if _vector_service is None:
        logger.info("🚀 Creating global VectorService singleton...")
        _vector_service = VectorService()
        logger.info("✅ VectorService singleton created")
    return _vector_service
