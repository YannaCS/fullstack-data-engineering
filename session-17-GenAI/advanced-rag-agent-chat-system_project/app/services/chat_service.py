from typing import AsyncIterator, Dict, Any, List
from loguru import logger
from openai import AsyncOpenAI
import json

from app.core.config import settings
from app.services.rag_pipeline import AdvancedRAGPipeline


class ChatService:
    """
    Chat service with agentic orchestration using OpenAI o3 model
    """
    
    def __init__(self, vector_store):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.rag_pipeline = AdvancedRAGPipeline(vector_store)
        self.conversation_history = {}
    
    async def stream_chat_response(
        self,
        query: str,
        conversation_id: str,
        user_id: str = "anonymous"
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream chat response with agentic workflow orchestration
        """
        logger.info(f"Processing chat query for conversation {conversation_id}")
        
        # Initialize conversation history if needed
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []
        
        try:
            # Step 1: Agent decides the workflow
            yield {"type": "status", "message": "Analyzing query..."}
            
            workflow_plan = await self._plan_workflow(query)
            
            yield {
                "type": "workflow",
                "plan": workflow_plan
            }
            
            # Step 2: Execute retrieval if needed
            retrieved_docs = []
            if workflow_plan.get("needs_retrieval", True):
                yield {"type": "status", "message": "Retrieving relevant documents..."}
                
                retrieved_docs = await self.rag_pipeline.retrieve(
                    query=query,
                    use_hyde=workflow_plan.get("use_hyde", True),
                    use_reranking=workflow_plan.get("use_reranking", True)
                )
                
                yield {
                    "type": "retrieval",
                    "num_docs": len(retrieved_docs)
                }
            
            # Step 3: Generate response with reasoning
            yield {"type": "status", "message": "Generating response..."}
            
            async for chunk in self._generate_response_stream(
                query=query,
                retrieved_docs=retrieved_docs,
                conversation_history=self.conversation_history[conversation_id],
                use_reasoning=workflow_plan.get("use_reasoning", False)
            ):
                yield chunk
            
            # Update conversation history
            self.conversation_history[conversation_id].append({
                "role": "user",
                "content": query
            })
            
        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}")
            yield {
                "type": "error",
                "message": f"An error occurred: {str(e)}"
            }
    
    async def _plan_workflow(self, query: str) -> Dict[str, Any]:
        """
        Use agent to plan the RAG workflow dynamically
        This is the agentic orchestration layer
        """
        planning_prompt = f"""Analyze this user query and determine the optimal RAG workflow:

Query: "{query}"

Decide on:
1. needs_retrieval: Does this query need document retrieval? (true/false)
2. use_hyde: Should we use HyDE query optimization? (true/false)
   - Use HyDE for complex, ambiguous, or broad queries
3. use_reranking: Should we use LLM reranking? (true/false)
   - Use reranking when precision is critical
4. use_reasoning: Should we use the reasoning model (o3)? (true/false)
   - Use reasoning for complex analytical questions
5. search_strategy: "semantic" | "keyword" | "hybrid"
6. explanation: Brief explanation of your decisions

Respond in JSON format only."""

        try:
            response = await self.client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert RAG system orchestrator. Analyze queries and decide optimal retrieval strategies."
                    },
                    {
                        "role": "user",
                        "content": planning_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            workflow_plan = json.loads(content.strip())
            
            logger.info(f"Workflow plan: {workflow_plan.get('explanation', 'N/A')}")
            return workflow_plan
            
        except Exception as e:
            logger.error(f"Workflow planning failed: {str(e)}")
            # Return default plan
            return {
                "needs_retrieval": True,
                "use_hyde": True,
                "use_reranking": True,
                "use_reasoning": False,
                "search_strategy": "hybrid",
                "explanation": "Using default workflow due to planning error"
            }
    
    async def _generate_response_stream(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]],
        use_reasoning: bool = False
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Generate streaming response using retrieved documents
        """
        # Build context from retrieved documents
        context = self._build_context(retrieved_docs)
        
        # Build messages
        messages = self._build_messages(
            query=query,
            context=context,
            conversation_history=conversation_history
        )
        
        # Choose model
        model = settings.REASONING_MODEL if use_reasoning else settings.CHAT_MODEL
        
        logger.info(f"Generating response with model: {model}")
        
        try:
            # Stream response
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=2000
            )
            
            full_response = ""
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    
                    yield {
                        "type": "content",
                        "content": content
                    }
            
            # Save assistant response to history
            conversation_history.append({
                "role": "assistant",
                "content": full_response
            })
            
            # Send completion signal with sources
            yield {
                "type": "complete",
                "sources": self._format_sources(retrieved_docs)
            }
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            yield {
                "type": "error",
                "message": f"Failed to generate response: {str(e)}"
            }
    
    def _build_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents"""
        if not retrieved_docs:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(retrieved_docs, start=1):
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            source = metadata.get('source', 'Unknown')
            page = metadata.get('page', '')
            
            source_info = f"Source {i}: {source}"
            if page:
                source_info += f" (Page {page})"
            
            context_parts.append(f"{source_info}\n{content}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def _build_messages(
        self,
        query: str,
        context: str,
        conversation_history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Build message array for the model"""
        messages = [
            {
                "role": "system",
                "content": """You are an advanced AI assistant with access to a knowledge base.

Your responsibilities:
1. Answer questions based primarily on the provided context
2. Be accurate and cite sources when possible
3. If the context doesn't contain the answer, say so clearly
4. Synthesize information from multiple sources when relevant
5. Maintain conversation continuity

Always be helpful, accurate, and transparent about your sources and limitations."""
            }
        ]
        
        # Add conversation history (last 5 exchanges)
        messages.extend(conversation_history[-10:])
        
        # Add current query with context
        user_message = f"""Context from knowledge base:
{context}

---

Question: {query}

Please answer based on the provided context. If the context doesn't contain enough information, please say so."""

        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def _format_sources(self, retrieved_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format sources for display"""
        sources = []
        
        for i, doc in enumerate(retrieved_docs, start=1):
            metadata = doc.get('metadata', {})
            sources.append({
                "id": i,
                "source": metadata.get('source', 'Unknown'),
                "page": metadata.get('page'),
                "relevance_score": doc.get('relevance_score'),
                "excerpt": doc.get('content', '')[:200] + "..."
            })
        
        return sources