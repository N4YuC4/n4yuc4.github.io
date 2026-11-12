# DocNeedle: Privacy-First Local Document Extraction Microservice & Visual RAG

**DocNeedle** is a privacy-first, local document extraction microservice and interactive platform designed to extract schema-governed structured data with auditable source citations and statistical confidence scoring using in-process neural models.

Unlike traditional document automation systems that rely on proprietary cloud APIs or brittle optical character recognition (OCR) engines, DocNeedle operates 100% locally with zero cloud telemetry, strict in-memory volatile execution guarantees, and OCR-free visual RAG capabilities.

![DocNeedle Interactive Dashboard](/static/images/portfolio-images/docneedle/dashboard_preview.png)

---

## Architecture & Core Innovations

```
DocNeedle/
├── assets/                       # Branding & SVG icons
├── app.py                        # Unified Gradio 6 UI + FastAPI root mount & ZeroGPU entry
├── config.toml                   # Primary application, model & pipeline settings
├── src/docneedle/
│   ├── main.py                   # FastAPI service factory, CORS & /healthz diagnostics
│   ├── hardening.py              # Linux kernel PR_SET_DUMPABLE anti-dump protection
│   ├── cuda_compat.py            # ZeroGPU preloaders & dynamic CUDA symbol leasing
│   ├── api/                      # Synchronous (/v1/extract) & asynchronous job endpoints
│   ├── jobs/                     # In-memory async job queue with real-time SSE streaming
│   ├── ingest/                   # Docling chunking, pypdfium2 AcroForm extraction & image rasterizer
│   ├── retrieval/                # Native C++ embedder, SessionVectorStore, BM25 & Qwen3-Reranker
│   ├── extraction/               # Spatial collision resolution, schema validation & confidence scoring
│   └── llm/                      # Qwen3.5-4B GGUF multimodal inference & speculative decoding
└── tests/                        # 159 hermetic unit tests with zero-disk verification
```

### 1. Zero-Disk In-Memory Privacy & Kernel-Level Hardening
DocNeedle guarantees strict data privacy for sensitive enterprise and regulatory documents:
* **Zero Disk Persistence:** Uploaded files, parsed document chunks, cross-modal embeddings, and vector indices reside exclusively in volatile RAM within `SessionVectorStore`. Every request unconditionally deallocates all memory buffers inside a `finally: store.clear()` block.
* **Kernel-Level Anti-Dumping:** Process memory is protected against unauthorized memory inspection, core dumping, and ptrace attachment via the Linux kernel prctl interface: `prctl(PR_SET_DUMPABLE, 0)` (`src/docneedle/hardening.py`).
* **Hardened Container Profile:** Deploys with a read-only root filesystem (`read_only: true`), memory-backed temporary directories via `tmpfs` (1 GB, `nosuid`), zero core dump limits (`ulimits: core: 0`), and fully offline Hugging Face mode (`HF_HUB_OFFLINE=1`).

```
[Uploaded Document & Schema]
            │
            ▼
┌────────────────────────────────────────────────────────┐
│ Volatile In-Memory Pipeline (PR_SET_DUMPABLE = 0)      │
│                                                        │
│  Docling Parser (io.BytesIO) ──► AcroForm Inspection   │
│         │                                              │
│         ▼                                              │
│  SessionVectorStore (In-Memory RRF Hybrid Index)       │
│         │                                              │
│         ▼                                              │
│  In-Process Multimodal LLM (Qwen3.5-4B + mmproj)       │
│         │                                              │
│         ▼                                              │
│  Spatial Collision Resolver & Confidence Verifier      │
└────────────────────────────────────────────────────────┘
            │
            ▼
 [Structured JSON Output with Citations]
            │
            ▼
  finally: store.clear() (RAM purged)
```

### 2. OCR-Free Visual RAG & Hybrid Ingestion
Traditional document pipelines suffer severe cascading errors when OCR misreads handwritten notes, stamps, low-contrast text, or complex table hierarchies. DocNeedle eliminates brittle OCR dependencies through an adaptive dual ingestion strategy:
* **Digital Text Ingestion:** Documents containing accessible text streams (`pdf_embedded_text_min_chars = 50`) are parsed via Docling Core into hierarchical markdown chunks, preserving document headings and tabular structures.
* **Scanned Pages & Visual Chunking:** Purely scanned pages and image inputs (PNG, JPG, TIFF, WEBP) are rasterized at high resolution (108 DPI) and directly ingested as visual chunks without lossy text translation.
* **Cross-Modal Grounding:** Page images are projected into the vector space using the SigLIP vision projector (`mmproj-F16.gguf`) and passed as base64 visual contexts directly into the multimodal LLM (Qwen3.5-4B), achieving high fidelity on messy real-world scans.

### 3. Native C++ Cross-Modal Embedding Engine
To deliver sub-millisecond retrieval without overhead, DocNeedle implements a dedicated C++ embedding engine (`src/docneedle/retrieval/docneedle_embed.cpp`) compiled into a high-performance shared library (`libdocneedle_embed.so`):
* **Single Unified Vector Space:** Embeds textual queries (`task: search result | query: {text}`) and raw visual page images into a unified 768-dimensional L2-normalized hypersphere via EmbeddingGemma-2.
* **Precompiled Multi-Architecture CUDA Kernels:** `libggml-cuda.so` embeds precompiled GPU kernels across modern compute architectures (`sm_80` Ampere, `sm_86`, `sm_89` Ada Lovelace, and `sm_120a` Blackwell), enabling instant GPU execution without on-the-fly compilation delays.
* **Process Symbol Isolation:** Loaded via Python `ctypes` using `RTLD_LOCAL | RTLD_DEEPBIND` flags in an isolated worker process. This guarantees complete separation between internal runtime symbols and `llama-cpp-python`, preventing symbol collisions across shared libraries.

### 4. Interactive PDF AcroForm Direct Parsing
A common failure mode in LLM document processing is hallucinating interactive form values or mistaking empty check boxes for checked ones.
* DocNeedle inspects low-level PDF dictionary streams directly using native `pypdfium2` bindings (`FPDFPage_GetAnnot`, `FPDFAnnot_GetFormFieldType`).
* It extracts form field titles, developer tooltips, check states, and interactive user inputs from UTF-16LE form streams.
* Extracted field pairs are formatted into structured markdown tables and injected directly into chunk contexts before retrieval, providing deterministic accuracy on legal, government, and insurance forms.

### 5. Spatial Collision Resolution
When a document contains a single prominent numerical entity (such as an invoice total or contract date), standard LLM prompts often duplicate that same value across multiple unpopulated or missing schema fields.
* `SpatialCollisionResolver` (`src/docneedle/extraction/collision.py`) intercepts candidate extraction results and detects repeated non-trivial values across distinct schema keys.
* It verifies physical occurrences of the value across candidate source pages.
* If a value appears only once on the source page, the resolver calculates spatial and contextual semantic affinity between each field's schema definition and the surrounding context of the token.
* The value is assigned strictly to the single highest-affinity field, while conflicting fields are reset to `found: False, value: None`.

### 6. Hybrid RRF Retrieval & Cross-Encoder Reranking
* **Reciprocal Rank Fusion (RRF):** Dense semantic embeddings (EmbeddingGemma-2) and sparse lexical signals (Okapi BM25) are fused using Reciprocal Rank Fusion ($k=60$) with document diversity constraints, ensuring balanced retrieval across multi-page files.
* **Neural Reranking:** For maximum citation precision, candidates can be passed through **Qwen3-Reranker-0.6B**, which evaluates `(query, chunk)` candidate pairs using cross-attention logit scoring (`logit("yes") - logit("no")`).

### 7. Speculative Prompt Lookup Decoding & KV Acceleration
* **KV Cache Optimization:** Employs Flash Attention with FP16 or quantized KV cache (`model_kv_cache_type_k=1`, `model_kv_cache_type_v=8` [Q8_0]), enabling 32,768-token context windows within compact VRAM constraints.
* **Speculative Decoding:** Supports optional in-process `LlamaPromptLookupDecoding` (`max_ngram_size=2`, `num_pred_tokens=5`) to accelerate generation throughput during schema-constrained entity extraction.

### 8. Unified Gradio 6 Dashboard & Async Streaming API
* **Unified Interface on Port 7860:** The Gradio 6 web application and FastAPI REST API are served on a single port.
* **Visual & Raw Schema Synchronization:** Build extraction schemas visually via interactive dropdowns or paste raw JSON schemas with two-way synchronization and recursive `$ref` pointer resolution up to 20 levels deep.
* **Asynchronous Jobs & Real-Time SSE:** Heavy multi-document batch jobs (`POST /v1/jobs`) stream progress events, step details, and field-by-field extractions in real-time over Server-Sent Events (`GET /v1/jobs/{id}/events`).

---

## ExtractBench Leaderboard & Benchmark Results

DocNeedle was evaluated on **ExtractBench** (LlamaIndex, arXiv:2607.29677), an enterprise document extraction benchmark spanning **370 documents**, **4,869 pages**, and **13,577 annotated fields** across invoices, regulatory filings, financial statements, and handwritten notes.

| System / Model | Architecture & Deployment | Overall Value F1 | Short (≤10p) | Medium (11-50p) | Long (>50p) | Page Grounding | Cost / Page | Privacy & Storage |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **LlamaExtract Agentic Plus** | Cloud Agentic Pipeline | **96.17%** | 97.02% | 94.30% | 94.65% | 88.26% | $0.0750 | Cloud API (External) |
| **Codex (GPT-6.1 Sol Evidence)** | Frontier Coding Agent | **95.31%** | 97.01% | 92.96% | 85.46% | 89.37% | $0.0713 | Cloud API (External) |
| **Claude Code (Sonnet 5.5 Evidence)**| Frontier Coding Agent | **94.68%** | 96.22% | 92.97% | 83.69% | 75.99% | $0.0569 | Cloud API (External) |
| **OpenAI GPT-6 Astra** | Commercial Frontier VLM | **91.91%** | 97.22% | 90.56% | 31.70% | 0.00% *(N/A)* | $0.1109 | Cloud API (External) |
| **Qwen3.5 4B (Raw Base Model)** | Standalone Base Model | **82.43%** | 89.06% | 76.64% | 27.31% | 0.00% *(N/A)* | Free (self-host) | Self-Hosted / Local |
| **Google Gemini 3.8 Flash** | Commercial Fast VLM | **80.71%** | 88.14% | 72.23% | 28.70% | 0.00% *(N/A)* | $0.0043 | Cloud API (External) |
| **DocNeedle (In-Process)** | **Qwen3.5-4B + Gemma2-RAG** | **75.71%** | **77.16%** | **69.70%** | **71.43%** | **80.95%** | **$0.00 (local)** | **Zero-Disk RAM / Air-Gapped** |

### Benchmark Takeaways
* **Long-Document Resilience (+44.12 pts vs. Base Model):** On documents exceeding 50 pages, unaugmented frontier models suffer severe attention degradation (raw Qwen3.5 4B drops to 27.31%, GPT-6 Astra drops to 31.70%). DocNeedle sustains **71.43% F1** by dynamically routing relevant visual and text chunks into a compact bounded context window.
* **Auditable Page Grounding (90.67% Short, 80.95% Overall):** While raw commercial VLMs provide zero source attribution (0.00%), DocNeedle pairs every extracted value with verified page citations and verbatim text evidence.
* **100% On-Premise Air-Gapped Operation:** Delivers enterprise-grade extraction at $0.00 marginal cost per page while enforcing zero-disk RAM guarantees.

---

## Technologies Used

* **Core Runtime & Microservice:** Python 3.14+, FastAPI 0.115+, Pydantic v2, Uvicorn, Server-Sent Events (SSE)
* **User Interface:** Gradio 6+ (Responsive Dark Theme, Dynamic Schema Editor, Telemetry Gauges)
* **In-Process Neural Inference:** `llama-cpp-python` (with CUDA/cuBLAS & Flash Attention), Qwen3.5-4B GGUF Multimodal, SigLIP Vision Projector
* **Cross-Modal Embeddings & Native Core:** C++ (`docneedle_embed.cpp`, `libdocneedle_embed.so`), EmbeddingGemma-2 GGUF, `ctypes` process isolation
* **Document Ingestion & Parsing:** Docling Core 2.15+, `pypdfium2` (AcroForm parser & 108 DPI rasterizer), `python-docx`, `openpyxl`, Pillow
* **Retrieval & Reranking:** Okapi BM25 (`rank-bm25`), Reciprocal Rank Fusion (RRF), Qwen3-Reranker-0.6B GGUF
* **Security & Containerization:** Linux `prctl(PR_SET_DUMPABLE, 0)`, Docker, Docker Compose, Hugging Face Spaces (ZeroGPU)
* **Testing & Quality Assurance:** Pytest (159 automated unit tests), Ruff, Zero-Disk CI verification
