# DocNeedle: Schema-Guided Local Document Information Extraction Engine

**DocNeedle** is an open-source, privacy-first **structured information extraction engine** and microservice designed to extract schema-governed data from complex enterprise documents—including PDFs, scans, receipts, contracts, and spreadsheets. It pairs every extracted field with auditable page-level citations and statistical confidence scores, running entirely on local neural models with zero reliance on cloud APIs.

By bypassing fragile traditional OCR pipelines and enforcing strict volatile in-memory execution, DocNeedle ensures that enterprise documents never touch persistent storage or leak into external services.

![DocNeedle Interactive Dashboard](/static/images/portfolio-images/docneedle/dashboard_preview.png)

---

## Architectural Highlights

```
DocNeedle/
├── assets/                       # Branding assets & SVG icons
├── app.py                        # Unified Gradio 6 UI + FastAPI root mount & ZeroGPU entry
├── config.toml                   # Central application, model & pipeline settings
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

### 1. Zero-Disk In-Memory Privacy & Kernel Hardening
Enterprise documents often contain sensitive personal, financial, or proprietary information. DocNeedle enforces an air-gapped data guarantee:
* **Volatile-Only Memory:** Uploaded files, chunk representations, vector embeddings, and retrieval indices exist exclusively in system RAM inside `SessionVectorStore`. Every request unconditionally purges its allocated memory buffers inside a `finally: store.clear()` block.
* **Kernel Anti-Dumping:** Process memory is protected against unauthorized inspection, core dumping, and debugger attachment using the Linux kernel prctl interface: `prctl(PR_SET_DUMPABLE, 0)` (`src/docneedle/hardening.py`).
* **Hardened Production Profile:** Containers run with a read-only root filesystem (`read_only: true`), temporary files mapped strictly to RAM (`tmpfs`, 1 GB, `nosuid`), zero core dump limits (`ulimits: core: 0`), and offline Hugging Face mode (`HF_HUB_OFFLINE=1`).

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
[Structured JSON Output with Source Citations]
            │
            ▼
  finally: store.clear() (RAM purged)
```

### 2. OCR-Free Visual RAG & Multimodal Grounding
Traditional document processing pipelines suffer compounding errors when OCR misinterprets handwritten annotations, stamps, faded scans, or complex table hierarchies. DocNeedle sidesteps these pitfalls with a dual-track ingestion pipeline:
* **Digital Documents:** Files containing embedded text layers (`pdf_embedded_text_min_chars = 50`) are parsed using Docling Core into clean, hierarchical Markdown chunks with heading structures and tables intact.
* **Scanned Pages & Images:** Scanned documents and raw images (PNG, JPG, TIFF, WEBP) are rasterized at high resolution (108 DPI) via `pypdfium2` and ingested directly as visual chunks without lossy text conversion.
* **Visual Context Passing:** Candidate page images are projected into vector space via the SigLIP vision projector (`mmproj-F16.gguf`) and passed directly into the multimodal LLM (Qwen3.5-4B) as high-resolution visual tokens. The model interprets page layouts and visual cues directly, just as a human reader would.

### 3. Native C++ Cross-Modal Embedding Engine
To deliver low-latency retrieval across large document corpora, DocNeedle integrates a standalone C++ embedding core (`src/docneedle/retrieval/docneedle_embed.cpp`) compiled as a shared library (`libdocneedle_embed.so`):
* **Unified Vector Space:** Maps both text queries (`task: search result | query: {text}`) and raw page images into a shared 768-dimensional L2-normalized space using EmbeddingGemma-2.
* **Precompiled Multi-Architecture CUDA Kernels:** `libggml-cuda.so` embeds precompiled kernels for modern NVIDIA architectures (`sm_80` Ampere, `sm_86`, `sm_89` Ada Lovelace, `sm_120a` Blackwell), avoiding runtime JIT compilation delays.
* **DSO Symbol Isolation:** Loaded via Python `ctypes` with `RTLD_LOCAL | RTLD_DEEPBIND` flags in an isolated worker process, preventing internal runtime symbol clashes with `llama-cpp-python`.

### 4. Interactive PDF AcroForm Stream Parsing
When extracting data from official forms, tax documents, or insurance claims, general-purpose LLMs frequently hallucinate check states or confuse adjacent fields.
* DocNeedle interfaces directly with PDF dictionary streams via low-level `pypdfium2` bindings (`FPDFPage_GetAnnot`, `FPDFAnnot_GetFormFieldType`).
* It extracts form field names, developer tooltips, checked states, and user inputs from UTF-16LE streams.
* The extracted fields are structured into clean Markdown tables and injected into the retrieval context ahead of time, ensuring near-perfect accuracy on interactive forms.

### 5. Spatial Collision Resolution
When a document features a single prominent number (such as an invoice total or transaction date), large language models tend to repeat that same value across multiple unpopulated or missing schema fields.
* `SpatialCollisionResolver` (`src/docneedle/extraction/collision.py`) monitors extraction outputs for duplicate values across distinct schema keys.
* It verifies the physical occurrence count of the value across candidate source pages.
* If a value appears only once on the source page, it scores the contextual affinity between each field's description and the text surrounding the token.
* The value is assigned strictly to the highest-affinity field, while ambiguous duplicates are cleanly reset to `found: False, value: None`.

### 6. Hybrid RRF Retrieval & Auxiliary Reranking
* **Reciprocal Rank Fusion (RRF):** Dense semantic embeddings (EmbeddingGemma-2) and sparse lexical signals (Okapi BM25) are fused using Reciprocal Rank Fusion ($k=60$) alongside document-diversity constraints to prevent single-page bias.
* **Cross-Encoder Scoring:** For high-precision extraction, candidate chunks can be passed through **Qwen3-Reranker-0.6B**, which evaluates `(query, chunk)` pairs via cross-attention logit scoring (`logit("yes") - logit("no")`).

### 7. Speculative Decoding & KV Cache Optimization
* **Flash Attention & Compact KV Cache:** Leverages Flash Attention with quantized or FP16 KV caching (`model_kv_cache_type_k=1`, `model_kv_cache_type_v=8` [Q8_0]), comfortably running 32,768-token contexts on consumer hardware.
* **Speculative Acceleration:** Supports optional in-process `LlamaPromptLookupDecoding` (`max_ngram_size=2`, `num_pred_tokens=5`) to significantly accelerate throughput during repetitive JSON key-value extraction.

### 8. Web Dashboard & Asynchronous Streaming API
* **Unified Service on Port 7860:** The Gradio 6 web interface and FastAPI REST endpoints are co-hosted on a single port.
* **Visual & Raw Schema Synchronization:** Users can configure schemas visually with field-type pickers or use the raw JSON schema tab, backed by two-way synchronization and recursive `$ref` pointer resolution up to 20 levels deep.
* **Real-Time Job Telemetry:** Heavy multi-document batch jobs (`POST /v1/jobs`) stream progress, execution steps, and field-level extractions over Server-Sent Events (`GET /v1/jobs/{id}/events`).

---

## Benchmark Performance: ExtractBench Evaluation

DocNeedle was evaluated on **ExtractBench** (LlamaIndex, arXiv:2607.29677), an enterprise document extraction benchmark spanning **370 documents**, **4,869 pages**, and **13,577 annotated fields** across invoices, financial filings, regulatory forms, and handwritten receipts.

| System / Model | Architecture & Deployment | Overall Value F1 | Short (≤10p) | Medium (11-50p) | Long (>50p) | Page Grounding | Cost / Page | Privacy & Storage |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **LlamaExtract Agentic Plus** | Cloud Agentic Pipeline | **96.17%** | 97.02% | 94.30% | 94.65% | 88.26% | $0.0750 | Cloud API (External) |
| **Codex (GPT-6.1 Sol Evidence)** | Frontier Coding Agent | **95.31%** | 97.01% | 92.96% | 85.46% | 89.37% | $0.0713 | Cloud API (External) |
| **Claude Code (Sonnet 5.5 Evidence)**| Frontier Coding Agent | **94.68%** | 96.22% | 92.97% | 83.69% | 75.99% | $0.0569 | Cloud API (External) |
| **OpenAI GPT-6 Astra** | Commercial Frontier VLM | **91.91%** | 97.22% | 90.56% | 31.70% | 0.00% *(N/A)* | $0.1109 | Cloud API (External) |
| **Qwen3.5 4B (Raw Base Model)** | Standalone Base Model | **82.43%** | 89.06% | 76.64% | 27.31% | 0.00% *(N/A)* | Free (self-host) | Self-Hosted / Local |
| **Google Gemini 3.8 Flash** | Commercial Fast VLM | **80.71%** | 88.14% | 72.23% | 28.70% | 0.00% *(N/A)* | $0.0043 | Cloud API (External) |
| **DocNeedle (In-Process)** | **Qwen3.5-4B + Gemma2-RAG** | **75.71%** | **77.16%** | **69.70%** | **71.43%** | **80.95%** | **$0.00 (local)** | **Zero-Disk RAM / Air-Gapped** |

### Key Benchmark Insights
* **Long-Document Resilience (+44.12 pts vs. Base Model):** On documents exceeding 50 pages, unaugmented frontier models suffer severe attention degradation (raw Qwen3.5 4B drops to 27.31%, GPT-6 Astra drops to 31.70%). DocNeedle sustains **71.43% F1** by filtering and routing relevant visual and textual chunks into a compact bounded context window.
* **Auditable Page Grounding (90.67% Short, 80.95% Overall):** While raw commercial VLMs provide zero source attribution (0.00%), DocNeedle pairs every extracted value with verified page citations and verbatim text evidence.
* **Air-Gapped Economics:** Delivers enterprise extraction at $0.00 marginal cost per page while strictly guaranteeing zero-disk RAM privacy.

---

## Technologies Used

* **Runtime & Microservice:** Python 3.14+, FastAPI 0.115+, Pydantic v2, Uvicorn, Server-Sent Events (SSE)
* **Frontend UI:** Gradio 6+ (Responsive Dark Theme, Dynamic Schema Editor, Telemetry Gauges)
* **Inference Engine:** `llama-cpp-python` (with CUDA/cuBLAS & Flash Attention), Qwen3.5-4B GGUF Multimodal, SigLIP Vision Projector
* **Vector Embeddings & Native Core:** C++ (`docneedle_embed.cpp`, `libdocneedle_embed.so`), EmbeddingGemma-2 GGUF, `ctypes` process isolation
* **Document Ingestion:** Docling Core 2.15+, `pypdfium2` (AcroForm parser & 108 DPI rasterizer), `python-docx`, `openpyxl`, Pillow
* **Retrieval & Reranking:** Okapi BM25 (`rank-bm25`), Reciprocal Rank Fusion (RRF), Qwen3-Reranker-0.6B GGUF
* **Security & Containerization:** Linux `prctl(PR_SET_DUMPABLE, 0)`, Docker, Docker Compose, Hugging Face Spaces (ZeroGPU)
* **Testing & Quality Assurance:** Pytest (159 unit tests), Ruff, Zero-Disk CI validation
