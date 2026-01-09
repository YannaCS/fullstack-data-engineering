from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS

from typing import List, Dict, Any
import json

# Load PDF
loader = PyPDFLoader("TSLA-Q2-2025-Update.pdf")
pdf_pages = loader.load()

# Chunk
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(pdf_pages)

# Create vector store
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ============================================================
# 1. Basic Metadata + Vector Search
# ============================================================

# Filter by source and year
retriever_filtered = vectorstore.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"source": "TSLA-Q2-2025-Update.pdf"}
    }
)

# Filter by page range
retriever_pages = vectorstore.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"page": {"$gte": 1, "$lte": 10}}  # First 10 pages only
    }
)

# ============================================================
# 2. Multi-Faceted Retrieval Class
# ============================================================

class MultiFacetedRetriever:
    def __init__(self, vectorstore, llm):
        self.vectorstore = vectorstore
        self.llm = llm
    
    # Facet 1: Semantic similarity search
    def semantic_search(self, query: str, k: int = 5) -> List:
        return self.vectorstore.similarity_search(query, k=k)
    
    # Facet 2: MMR (Maximum Marginal Relevance) for diversity
    def mmr_search(self, query: str, k: int = 5, diversity: float = 0.7) -> List:
        return self.vectorstore.max_marginal_relevance_search(
            query, 
            k=k, 
            fetch_k=20,  # Fetch more, then select diverse subset
            lambda_mult=diversity  # 0 = max diversity, 1 = max relevance
        )
    
    # Facet 3: Metadata-filtered search
    def filtered_search(self, query: str, filters: Dict, k: int = 5) -> List:
        return self.vectorstore.similarity_search(
            query, 
            k=k, 
            filter=filters
        )
    
    # Facet 4: Keyword search (BM25-style if available)
    def keyword_search(self, query: str, k: int = 5) -> List:
        # Extract keywords from query
        keywords = query.lower().split()
        
        # Search for each keyword and combine results
        all_docs = []
        seen_ids = set()
        
        for keyword in keywords:
            docs = self.vectorstore.similarity_search(keyword, k=3)
            for doc in docs:
                doc_id = hash(doc.page_content)
                if doc_id not in seen_ids:
                    seen_ids.add(doc_id)
                    all_docs.append(doc)
        
        return all_docs[:k]
    
    # Facet 5: Query-guided metadata extraction
    def smart_filter_search(self, query: str, k: int = 5) -> List:
        # Use LLM to extract filter criteria from query
        filter_prompt = ChatPromptTemplate.from_template("""
Extract metadata filters from this query. Return JSON only.

Available filters:
- source: document filename
- page: page number (integer)
- year: year mentioned
- section: like "financials", "operations", "outlook"

Query: {query}

Return format: {{"filter_name": "value"}} or {{}} if no specific filters.
JSON:""")
        
        filter_chain = filter_prompt | self.llm | StrOutputParser()
        filter_json = filter_chain.invoke({"query": query})
        
        try:
            # Clean and parse JSON
            filter_json = filter_json.strip().strip("```json").strip("```")
            filters = json.loads(filter_json)
        except:
            filters = {}
        
        if filters:
            return self.filtered_search(query, filters, k)
        else:
            return self.semantic_search(query, k)
    
    # Combined multi-faceted retrieval
    def retrieve(
        self, 
        query: str, 
        k: int = 5,
        use_semantic: bool = True,
        use_mmr: bool = True,
        use_keyword: bool = False,
        filters: Dict = None,
        deduplicate: bool = True
    ) -> List:
        all_docs = []
        seen_content = set()
        
        def add_docs(docs, source_name):
            for doc in docs:
                content_hash = hash(doc.page_content[:200])
                if not deduplicate or content_hash not in seen_content:
                    seen_content.add(content_hash)
                    doc.metadata["retrieval_source"] = source_name
                    all_docs.append(doc)
        
        # Run each facet
        if use_semantic:
            docs = self.semantic_search(query, k=k)
            add_docs(docs, "semantic")
        
        if use_mmr:
            docs = self.mmr_search(query, k=k)
            add_docs(docs, "mmr")
        
        if use_keyword:
            docs = self.keyword_search(query, k=k)
            add_docs(docs, "keyword")
        
        if filters:
            docs = self.filtered_search(query, filters, k=k)
            add_docs(docs, "filtered")
        
        return all_docs


# ============================================================
# 3. Usage Examples
# ============================================================

# Initialize
mf_retriever = MultiFacetedRetriever(vectorstore, llm)

# Example 1: Basic semantic search
results = mf_retriever.semantic_search(
    "Tesla Q2 2025 profitability", 
    k=5
)

# Example 2: Diverse results with MMR
results = mf_retriever.mmr_search(
    "Tesla financial performance",
    k=5,
    diversity=0.5  # Balance relevance and diversity
)

# Example 3: Filtered by metadata
results = mf_retriever.filtered_search(
    "vehicle deliveries",
    filters={"page": {"$in": [5, 6, 7]}},  # Specific pages
    k=5
)

# Example 4: Smart filtering (LLM extracts filters)
results = mf_retriever.smart_filter_search(
    "What does page 6 say about production numbers?"
)

# Example 5: Combined multi-faceted retrieval
results = mf_retriever.retrieve(
    query="Tesla Q2 2025 revenue and Robotaxi launch",
    k=5,
    use_semantic=True,
    use_mmr=True,
    use_keyword=True,
    filters={"source": "TSLA-Q2-2025-Update.pdf"}
)


# ============================================================
# 4. Pretty Print Results
# ============================================================

def print_results(results, max_content_length=300):
    print(f"Retrieved {len(results)} documents:\n")
    
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get("retrieval_source", "unknown")
        page = doc.metadata.get("page_label", "N/A")
        
        print(f"--- Result {i} [{source}] ---")
        print(f"Page: {page}")
        print(f"Content: {doc.page_content[:max_content_length]}...")
        print()


# Example with output
query = "How many vehicles did Tesla deliver and what was their profit?"

print(f"Query: {query}\n")
print("=" * 60)

results = mf_retriever.retrieve(
    query=query,
    k=3,
    use_semantic=True,
    use_mmr=True,
    use_keyword=False
)

print_results(results)


# ============================================================
# 5. Hybrid Retrieval with Scoring
# ============================================================

class ScoredMultiFacetedRetriever(MultiFacetedRetriever):
    
    def retrieve_with_scores(self, query: str, k: int = 5) -> List[Dict]:
        """Retrieve and combine scores from multiple methods"""
        
        # Get results with scores
        semantic_results = self.vectorstore.similarity_search_with_score(query, k=k)
        
        # Normalize and combine
        scored_docs = []
        
        for doc, score in semantic_results:
            scored_docs.append({
                "document": doc,
                "semantic_score": 1 - score,  # Convert distance to similarity
                "page": doc.metadata.get("page_label"),
                "source": doc.metadata.get("source")
            })
        
        # Sort by score
        scored_docs.sort(key=lambda x: x["semantic_score"], reverse=True)
        
        return scored_docs
    
    def print_scored_results(self, results: List[Dict]):
        print(f"{'Rank':<6}{'Score':<10}{'Page':<8}{'Content Preview'}")
        print("-" * 70)
        
        for i, r in enumerate(results, 1):
            content = r["document"].page_content[:50].replace("\n", " ")
            print(f"{i:<6}{r['semantic_score']:.4f}    {r['page']:<8}{content}...")


# Usage
scored_retriever = ScoredMultiFacetedRetriever(vectorstore, llm)
scored_results = scored_retriever.retrieve_with_scores(
    "Tesla deliveries Q2 2025", 
    k=5
)
scored_retriever.print_scored_results(scored_results)