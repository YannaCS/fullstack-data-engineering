from typing import List, Dict, Any, Tuple
from loguru import logger
from openai import AsyncOpenAI
import numpy as np

from app.core.config import settings


class AdvancedRAGPipeline:
    """
    Advanced RAG Pipeline implementing:
    1. Query Optimization (HyDE)
    2. Hybrid Search (Dense + Sparse with RRF)
    3. LLM-based Reranking
    """
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
    async def query_optimization_hyde(self, query: str) -> List[str]:
        """
        HyDE (Hypothetical Document Embeddings):
        Generate hypothetical documents that would answer the query,
        then use those for retrieval instead of the raw query.
        """
        if not settings.HYDE_ENABLED:
            return [query]
        
        logger.info(f"Generating HyDE hypothetical documents for: {query[:50]}...")
        
        prompt = f"""Given the question: "{query}"

Generate {settings.HYDE_NUM_HYPOTHETICAL_DOCS} different hypothetical document passages that would perfectly answer this question. Each passage should be detailed and comprehensive.

Format your response as a numbered list."""

        try:
            response = await self.client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at generating hypothetical documents for information retrieval."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            
            # Parse the hypothetical documents
            hypothetical_docs = []
            for line in content.split('\n'):
                line = line.strip()
                if line and not line[0].isdigit():
                    hypothetical_docs.append(line)
            
            # Include original query as well
            all_queries = [query] + hypothetical_docs[:settings.HYDE_NUM_HYPOTHETICAL_DOCS]
            
            logger.info(f"Generated {len(all_queries)} queries for retrieval")
            return all_queries
            
        except Exception as e:
            logger.error(f"HyDE generation failed: {str(e)}")
            return [query]
    
    async def hybrid_search(
        self, 
        queries: List[str], 
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Hybrid Search combining:
        - Dense retrieval (semantic/vector search)
        - Sparse retrieval (keyword/BM25)
        - Reciprocal Rank Fusion (RRF) for combining results
        """
        if top_k is None:
            top_k = settings.TOP_K_RETRIEVAL
        
        logger.info(f"Performing hybrid search with {len(queries)} queries, top_k={top_k}")
        
        all_results = []
        
        for query in queries:
            # Dense retrieval (vector search)
            dense_results = await self.vector_store.similarity_search(
                query=query,
                k=top_k
            )
            
            # Sparse retrieval (keyword search)
            # Note: For full BM25, you'd need to implement this separately
            # Here we'll use the vector store's metadata filtering as a proxy
            sparse_results = await self.vector_store.keyword_search(
                query=query,
                k=top_k
            )
            
            # Combine using RRF
            combined = self._reciprocal_rank_fusion(
                dense_results,
                sparse_results,
                k=60  # RRF constant
            )
            
            all_results.extend(combined)
        
        # Deduplicate and re-rank
        unique_results = self._deduplicate_results(all_results)
        
        logger.info(f"Hybrid search returned {len(unique_results)} unique results")
        return unique_results[:top_k]
    
    def _reciprocal_rank_fusion(
        self,
        dense_results: List[Dict],
        sparse_results: List[Dict],
        k: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Reciprocal Rank Fusion: RRF(d) = Σ(1 / (k + rank_i(d)))
        where k is a constant (typically 60) and rank_i(d) is the rank of document d in list i
        """
        rrf_scores = {}
        
        # Score dense results
        for rank, result in enumerate(dense_results, start=1):
            doc_id = result.get('id', result.get('content', '')[:50])
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = {'score': 0, 'result': result}
            rrf_scores[doc_id]['score'] += 1 / (k + rank)
        
        # Score sparse results
        for rank, result in enumerate(sparse_results, start=1):
            doc_id = result.get('id', result.get('content', '')[:50])
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = {'score': 0, 'result': result}
            rrf_scores[doc_id]['score'] += 1 / (k + rank)
        
        # Sort by RRF score
        sorted_results = sorted(
            rrf_scores.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        return [item['result'] for item in sorted_results]
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on content similarity"""
        seen_content = set()
        unique_results = []
        
        for result in results:
            content = result.get('content', '')
            content_hash = hash(content[:100])  # Use first 100 chars for deduplication
            
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_results.append(result)
        
        return unique_results
    
    async def llm_rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        LLM-based reranking: Use LLM to score relevance of each result to the query
        """
        if top_k is None:
            top_k = settings.RERANK_TOP_K
        
        logger.info(f"LLM reranking {len(results)} results to top {top_k}")
        
        if len(results) <= top_k:
            return results
        
        # Prepare ranking prompt
        ranking_prompt = f"""Given the query: "{query}"

Rate the relevance of each document passage to this query on a scale of 0-10, where:
- 10: Highly relevant, directly answers the query
- 5: Somewhat relevant, contains related information
- 0: Not relevant

Documents:
"""
        
        for i, result in enumerate(results, start=1):
            content = result.get('content', '')[:500]  # Limit to 500 chars
            ranking_prompt += f"\n{i}. {content}\n"
        
        ranking_prompt += "\nProvide your ratings as a JSON array of numbers, e.g., [8, 3, 9, 7, ...]"
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at evaluating document relevance for information retrieval."},
                    {"role": "user", "content": ranking_prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            
            # Extract scores
            import json
            scores = json.loads(content.strip())
            
            # Combine results with scores
            ranked_results = [
                {**result, 'relevance_score': score}
                for result, score in zip(results, scores)
            ]
            
            # Sort by relevance score
            ranked_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            logger.info(f"Reranked results, top score: {ranked_results[0].get('relevance_score', 0)}")
            return ranked_results[:top_k]
            
        except Exception as e:
            logger.error(f"LLM reranking failed: {str(e)}, returning original order")
            return results[:top_k]
    
    async def retrieve(
        self,
        query: str,
        use_hyde: bool = True,
        use_reranking: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Full retrieval pipeline:
        1. Query Optimization (HyDE)
        2. Hybrid Search
        3. LLM Reranking
        """
        logger.info(f"Starting advanced RAG retrieval for query: {query[:50]}...")
        
        # Step 1: Query Optimization (HyDE)
        if use_hyde:
            queries = await self.query_optimization_hyde(query)
        else:
            queries = [query]
        
        # Step 2: Hybrid Search
        results = await self.hybrid_search(queries, top_k=settings.TOP_K_RETRIEVAL)
        
        # Step 3: LLM Reranking
        if use_reranking:
            results = await self.llm_rerank(query, results, top_k=settings.RERANK_TOP_K)
        
        logger.info(f"Retrieval complete, returning {len(results)} results")
        return results