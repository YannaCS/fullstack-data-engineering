from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
import faiss
import numpy as np
from openai import AsyncOpenAI
from loguru import logger
import pickle
import os

from app.core.config import settings


class VectorStoreManager:
    """
    Manages both ChromaDB (production) and FAISS (demo) vector stores
    """
    
    def __init__(self, use_chroma: bool = True):
        self.use_chroma = use_chroma
        self.client_openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        if use_chroma:
            self._init_chroma()
        else:
            self._init_faiss()
    
    def _init_chroma(self):
        """Initialize ChromaDB client"""
        try:
            self.chroma_client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
                settings=ChromaSettings(
                    allow_reset=True,
                    anonymized_telemetry=False
                )
            )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="rag_documents",
                metadata={"description": "Advanced RAG document embeddings"}
            )
            
            logger.info("ChromaDB initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise
    
    def _init_faiss(self):
        """Initialize FAISS index"""
        self.dimension = 1536  # OpenAI embedding dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.id_to_metadata = {}
        self.next_id = 0
        logger.info("FAISS initialized successfully")
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI"""
        try:
            response = await self.client_openai.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to get embedding: {str(e)}")
            raise
    
    async def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add documents to vector store"""
        if not texts:
            return []
        
        logger.info(f"Adding {len(texts)} documents to vector store")
        
        # Generate embeddings
        embeddings = []
        for text in texts:
            embedding = await self.get_embedding(text)
            embeddings.append(embedding)
        
        if self.use_chroma:
            return await self._add_to_chroma(texts, embeddings, metadatas, ids)
        else:
            return await self._add_to_faiss(texts, embeddings, metadatas, ids)
    
    async def _add_to_chroma(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict]],
        ids: Optional[List[str]]
    ) -> List[str]:
        """Add documents to ChromaDB"""
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(texts))]
        
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(texts)} documents to ChromaDB")
        return ids
    
    async def _add_to_faiss(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict]],
        ids: Optional[List[str]]
    ) -> List[str]:
        """Add documents to FAISS"""
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Add to index
        start_id = self.next_id
        self.index.add(embeddings_array)
        
        # Store metadata
        if ids is None:
            ids = [f"doc_{i}" for i in range(start_id, start_id + len(texts))]
        
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        for i, (text, metadata, doc_id) in enumerate(zip(texts, metadatas, ids)):
            self.id_to_metadata[start_id + i] = {
                'id': doc_id,
                'text': text,
                'metadata': metadata
            }
        
        self.next_id += len(texts)
        logger.info(f"Added {len(texts)} documents to FAISS")
        return ids
    
    async def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Perform similarity search"""
        logger.info(f"Performing similarity search for: {query[:50]}...")
        
        # Get query embedding
        query_embedding = await self.get_embedding(query)
        
        if self.use_chroma:
            return await self._search_chroma(query_embedding, k, filter_dict)
        else:
            return await self._search_faiss(query_embedding, k)
    
    async def _search_chroma(
        self,
        query_embedding: List[float],
        k: int,
        filter_dict: Optional[Dict]
    ) -> List[Dict[str, Any]]:
        """Search in ChromaDB"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter_dict
        )
        
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })
        
        return formatted_results
    
    async def _search_faiss(
        self,
        query_embedding: List[float],
        k: int
    ) -> List[Dict[str, Any]]:
        """Search in FAISS"""
        query_array = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_array, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx in self.id_to_metadata:
                metadata = self.id_to_metadata[idx]
                results.append({
                    'id': metadata['id'],
                    'content': metadata['text'],
                    'metadata': metadata.get('metadata', {}),
                    'distance': float(distances[0][i])
                })
        
        return results
    
    async def keyword_search(
        self,
        query: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Simple keyword-based search (BM25 approximation)
        For production, consider using Elasticsearch or similar
        """
        # For now, we'll do a simple text matching
        # This is a placeholder - in production you'd use proper BM25
        
        if self.use_chroma:
            # ChromaDB doesn't have built-in BM25, so we'll use metadata search
            # In production, integrate with Elasticsearch
            return await self.similarity_search(query, k)
        else:
            # For FAISS, we'll do simple keyword matching
            query_terms = query.lower().split()
            scored_docs = []
            
            for idx, metadata in self.id_to_metadata.items():
                text = metadata['text'].lower()
                score = sum(term in text for term in query_terms)
                if score > 0:
                    scored_docs.append((score, idx))
            
            scored_docs.sort(reverse=True)
            
            results = []
            for score, idx in scored_docs[:k]:
                metadata = self.id_to_metadata[idx]
                results.append({
                    'id': metadata['id'],
                    'content': metadata['text'],
                    'metadata': metadata.get('metadata', {}),
                    'score': score
                })
            
            return results
    
    async def delete_documents(self, ids: List[str]):
        """Delete documents by IDs"""
        if self.use_chroma:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from ChromaDB")
        else:
            # FAISS doesn't support deletion easily
            # Would need to rebuild index
            logger.warning("FAISS doesn't support efficient deletion")
    
    def save_faiss_index(self, path: str = "faiss_index"):
        """Save FAISS index to disk"""
        if not self.use_chroma:
            os.makedirs(path, exist_ok=True)
            faiss.write_index(self.index, f"{path}/index.faiss")
            with open(f"{path}/metadata.pkl", 'wb') as f:
                pickle.dump(self.id_to_metadata, f)
            logger.info(f"FAISS index saved to {path}")
    
    def load_faiss_index(self, path: str = "faiss_index"):
        """Load FAISS index from disk"""
        if not self.use_chroma:
            self.index = faiss.read_index(f"{path}/index.faiss")
            with open(f"{path}/metadata.pkl", 'rb') as f:
                self.id_to_metadata = pickle.load(f)
            logger.info(f"FAISS index loaded from {path}")