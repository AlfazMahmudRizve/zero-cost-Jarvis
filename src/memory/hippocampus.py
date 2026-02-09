"""
Memory Module (The Hippocampus)
Handles long-term memory storage and retrieval using ChromaDB.
"""

import uuid
import time
import chromadb
from datetime import datetime
from typing import List, Optional
from src.core.config import settings
from src.core.logger import get_logger

logger = get_logger(__name__)


class Hippocampus:
    """
    The Memory Unit.
    Manages vector storage of conversations and facts.
    """

    def __init__(self):
        self.persist_path = str(settings.chroma_persist_path)
        self.collection_name = settings.memory_collection_name
        
        try:
            # Initialize persistent client
            self.client = chromadb.PersistentClient(path=self.persist_path)
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Hippocampus initialized at {self.persist_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Memory: {e}")
            self.collection = None

    def memorize(self, text: str, source: str = "user") -> None:
        """
        Store a text memory with metadata.
        
        Args:
            text: The content to remember.
            source: 'user' or 'sheriff'.
        """
        if not self.collection or not text:
            return

        try:
            memory_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            self.collection.add(
                documents=[text],
                metadatas=[{
                    "source": source,
                    "timestamp": timestamp,
                    "type": "conversation"
                }],
                ids=[memory_id]
            )
            logger.debug(f"Memorized ({source}): '{text[:30]}...'")
            
        except Exception as e:
            logger.error(f"Failed to memorize: {e}")

    def recall(self, query: str, n_results: int = 3) -> str:
        """
        Retrieve relevant memories for a query.
        
        Args:
            query: The search text.
            n_results: Number of results to return.
            
        Returns:
            Formatted context string.
        """
        if not self.collection or not query:
            return ""

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            documents = results['documents'][0] if results['documents'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            
            if not documents:
                return ""

            context_parts = []
            for doc, meta in zip(documents, metadatas):
                source = meta.get('source', 'unknown')
                context_parts.append(f"[{source.upper()}]: {doc}")

            formatted_context = "\n".join(context_parts)
            logger.debug(f"Recalled {len(documents)} memories for '{query[:20]}...'")
            return f"Relevant Context:\n{formatted_context}"

        except Exception as e:
            logger.error(f"Failed to recall: {e}")
            return ""


# Singleton instance
d_hippocampus = Hippocampus()
