# Part 2 – Build a Tiny Vector Index & Experiment with Chunking

## 1. Choose a document

Pick **one** reasonably long text source:

- **Option A:** A long technical blog post or documentation page (2–5 pages of content).
- **Option B:** A PDF report (e.g., a research paper, whitepaper, or internal spec).

Try to choose something with **headings and sections**, and ideally at least one table or list.

---

## 2. Implement two chunking strategies

### 1. Naïve fixed-size chunking

- Split the document text into chunks of ~400–500 tokens (or ~800–1000 characters if you don't have a tokenizer).
- Use an overlap of ~80–100 tokens (~150–200 characters).

### 2. Structure-aware chunking (simple version)

- Use headings (e.g., lines starting with `#`, `##`, or capitalized section titles) or `<h1>`/`<h2>` tags or obvious section markers to define **logical sections**.
- For each section, merge the heading + following paragraphs into one chunk (or two chunks if very long, with overlap).
- Keep track of which strategy produced which chunks (e.g., `strategy: naive` vs `strategy: structured`).

You don't need perfect code—just something that clearly produces two sets of chunks.

---

## 3. Embed and search

Having access to any embedding model (OpenAI embeddings, `sentence-transformers`, etc.):

1. Compute embeddings for **all chunks** from both strategies.
2. Implement a simple **cosine similarity search**:
   - For a given query, embed the query,
   - Compute similarity with every chunk,
   - Return Top-5 chunks for each strategy (naïve vs structured).

If you can, try at least **3 queries**, for example:

- A fact-level question ("What are the main limitations of X?").
- A "why" question ("Why does the author recommend Y?").
- A more open question ("What are the main design principles described in this document?").

---

## 4. Compare and reflect

In your homework document, include:

- A short description of:
  - The document you used,
  - How you implemented naive vs structure-aware chunking (high level, no need for full code).

- For **each query**, paste:
  - The query,
  - The top chunk (or top 2 chunks) returned by **naive chunking**,
  - The top chunk (or top 2 chunks) returned by **structure-aware chunking**.

Then, in **8–12 sentences**, answer:

1. For which queries did structure-aware chunking give clearly better context?
2. Did naive chunking ever "win" or look comparable? Why?
3. How did chunk size and overlap affect:
   - Answer completeness,
   - Noise in the retrieved context,
   - Token cost (roughly)?
4. If you had more time, what would you try next to improve retrieval quality?

---

## If you cannot run embeddings:

Instead of coding, do a **manual analysis**:

- Take 1–2 pages of text,
- Manually create "naive" vs "section-based" chunks on paper,
- For 2–3 questions, reason about which chunks are most relevant under each strategy and write your observations in 8–12 sentences.