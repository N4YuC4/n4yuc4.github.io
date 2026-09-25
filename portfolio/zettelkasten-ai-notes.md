# Zettelkasten AI Notes

A desktop knowledge management system implementing the **Zettelkasten** methodology, built with **Python 3.13** and the **Flet** UI framework (Flutter-backed desktop runtime). Originally recognized as a **Top 10 Finalist at the Pupilica AI Hackathon**, the project has evolved into a privacy-first, modular desktop environment that transforms unstructured documents into an interconnected web of atomic notes.

It features a **Dual AI Engine** offering both cloud-based analysis via Google Gemini and 100% offline local inference using GGUF models accelerated by Vulkan GPU compute, a **Two-Tier In-Memory Vector RAG Pool** with CPU-isolated cross-encoder reranking, an interactive canvas mind map, an advanced live Markdown editor, and a smart bidirectional [[WikiLink]] system.

---

## Architecture & Core Capabilities

### 1. Dual AI Extraction Engine & Two-Tier In-Memory Vector RAG Pool
The core engine of Zettelkasten AI Notes ingests dense PDF documents, extracts meaningful atomic insights, and establishes semantic relationships without concept duplication across document chunks:

* **Cloud AI (Google Gemini API):** High-throughput extraction utilizing the official `google-genai` SDK (v2.22.0) with custom system prompt governance.
* **Offline Local AI (GGUF via Vulkan GPU):** Privacy-first, local LLM inference powered by `llama-cpp-python` with cross-vendor **Vulkan GPU acceleration** (compatible with NVIDIA, AMD, Intel, and Apple Silicon).
* **Two-Tier Stateful RAG Pool (`note_rag_pool.py`):** Session-scoped RAG pool eliminating cross-chunk concept duplication during multi-chunk PDF and document ingestion:
  * **Tier 1 (Global Concept Map):** Bird's-eye view of all accumulated notes with canonical IDs, titles, and 1-sentence core mechanism summaries injected into generation prompts.
  * **Tier 2 (Focal Note Retrieval):** Dynamically budgeted focal note injection pairing bi-encoder vector similarity with cross-encoder reranking.
  * **Global Union-Find Reconciliation:** Discovers multi-way transitive duplicate clusters across document chunks and consolidates them via LLM or algorithmic non-redundant synthesis while cleanly remapping wikilinks and graph edges.
* **Process-Isolated Execution:** Local inference executes inside a dedicated `multiprocessing` worker. This prevents GUI thread freezes and deadlocks with Wayland/Vulkan presentation pipelines, keeping the interface fluid while ensuring immediate RAM/VRAM reclamation upon task completion or cancellation.

### 2. Dedicated CPU Auxiliary Inference Models (Embeddings & Reranking)
To ensure optimal performance without consuming precious GPU memory needed by generation LLMs, auxiliary NLP models run strictly in CPU-isolated workers:

* **Semantic Memory Service (`semantic_memory_service.py`):** Local CPU embedding inference powered by **Microsoft Harrier (0.6B)** (32K context window, 1024 dimensions) for vector indexing, cosine candidate discovery, and semantic graph linking.
* **Cross-Encoder Reranker (`reranker_service.py`):** High-precision candidate relevance scoring powered by **Qwen3-Reranker (0.6B)**. Evaluates `(query, note)` pairs using instruction-aware cross-attention and calibrated sigmoid logit scoring (`logit("yes") - logit("no")`).
* **Zero VRAM Contention:** Auxiliary models execute strictly on CPU (`n_threads=2`, `n_gpu_layers=0`), preserving 100% of GPU VRAM for the primary generation models (Gemma 4 family).

### 3. Modular Parsing, Concept Matching & Graph Reconciliation
The processing pipeline is decomposed into resilient, decoupled domain engines:

* **Multilingual Concept Matcher (`concept_matcher.py`):** Multi-tier duplicate concept detection engine utilizing character 4-gram overlap, language-agnostic token normalization and stemming, qualifier stripping, and synonym reconciliation.
* **Resilient JSON Repair & LaTeX Sanitizer (`json_repair_engine.py` & `ai_response_parser.py`):** Dedicated parsing and repair engine that balances unclosed brackets and truncated strings from LLM context limits, filters academic citation markers (`[1]`, `[Smith et al.]`), and performs KaTeX-safe LaTeX escaping without corrupting code blocks.
* **Loop-Safe Graph Reconciliation (`graph_reconciliation.py`):** Enforces canonical undirected pair ordering (`canonical_pair`), resolves transitive redirects safely without cyclic loops, and remaps wikilinks across heterogeneous integer and UUID note identifiers.
* **Universal Dynamic Semantic Chunker (`semantic_chunker.py`):** Dynamically splits dense PDF texts along semantic paragraph, sentence, and word boundaries with adaptive token overlap (~4500 tokens default) to prevent context truncation.
* **Non-Blocking PDF Processing (`pdf_processor.py`):** Background thread text extraction with layout awareness and typographical normalization (hyphen healing, newline collapsing) to avoid GUI freezing.

### 4. In-App Model Manager & Downloader
Enables users to discover, download, and configure local models without external servers or command-line tooling:

* **Curated Local Model Catalog (`local_models_catalog.py`):**
  * **Generation Models (Gemma 4 Family):** Lightweight E2B (3.2 GB, 128K context), Balanced 12B (6.2 GB), and Flagship 26B MoE (13.1 GB).
  * **Auxiliary Models:** Microsoft Harrier 0.6B (Embeddings) and Qwen3-Reranker 0.6B (Cross-Encoder).
* **Chunked HTTP Downloader (`model_downloader.py`):** Integrated background downloader fetching weights directly from Hugging Face with live progress indicators, download speed, ETA estimation, and cancellation support. Models are stored in the OS user data directory (`~/.local/share/zettelkasten_ai/models/`) to maintain repository hygiene.

### 5. Hardware Resource Inspector & OOM Guard (`hardware_checker.py`)
* **Proactive Resource Detection:** Automatically detects host system RAM, CPU cores, GPU devices, and available VRAM.
* **Out-Of-Memory (OOM) Protection:** Validates system headroom before downloading or loading models into memory.
* **Dynamic Layer Offloading:** Automatically computes the optimal number of GPU offloading layers (`n_gpu_layers`) based on current hardware capability.

### 6. Advanced Live Markdown Workspace (`markdown_editor_widget.py`)
* **Source & Reading Modes:** Seamlessly toggle between raw Markdown editing and formatted preview using `Ctrl+E` or the header toolbar button.
* **Rich Formatting Toolbar:** One-click shortcuts for Headings (H1–H4), bold (`Ctrl+B`), italic (`Ctrl+I`), strikethrough, syntax-highlighted code blocks, blockquotes, lists, tables, and horizontal rules.
* **Interactive Task Checklists:** Toggle `- [ ]` and `- [x]` checkboxes with direct click interaction in both editing and reading modes.
* **LaTeX Math Normalization:** Full support for inline math (`$ ... $`, `\( ... \)`) and display math (`$$ ... $$`, `\[ ... \]`) rendered cleanly within Flutter KaTeX.
* **Document Telemetry:** Live counter tracking words, characters, lines, and estimated reading time.
* **Debounced Auto-Save:** Background non-blocking auto-save with dirty state indicators (`*`) to ensure no thoughts are lost.

### 7. Smart Bidirectional [[WikiLink]] System
* **WikiLink Syntax:** Connect concepts effortlessly using `[[Note Title]]` or `[[Target Note|Custom Alias]]`.
* **Interactive Navigation & Auto-Creation:** Clicking any WikiLink jumps straight to that note. If the target note does not exist yet, the application prompts to create and link it in a single click.
* **Quick Link Picker (`Ctrl+K`):** Fast search modal to quickly insert links and establish directional or bidirectional connections between notes.
* **Strict Semantic Edge Resolution:** Prevents false graph connections and hallucinated links by matching exact titles and normalized case-folded names.

### 8. Interactive Canvas Mind Map & Knowledge Graph (`mind_map_widget.py`)
* **Canvas Rendering:** Hardware-accelerated dynamic graph rendering via `flet.canvas` with automatic node layout calculation using `PyGraphviz`.
* **Pan & Zoom Navigation:** Smooth, fluid navigation powered by `InteractiveViewer` controls.
* **Direct Interaction & Focus Mode:** Clicking any node on the graph canvas instantly focuses and opens the note in the editor workspace.

### 9. Modern 3-Pane Responsive Layout & Settings Architecture
* **Left Sidebar:** Filter collections, search in real-time, view note counts, and access configuration settings.
* **Center Workspace:** Markdown editor, reading preview, dynamic AppBar header with active note title and category badge.
* **Right Panel:** Interactive Mind Map canvas and Linked Notes relationship inspector.
* **Collapsible Narrow Rails:** Minimize the left sidebar (`Ctrl+[`) or right panel (`Ctrl+]`) into compact 50px icon rails to maximize editor focus.
* **Draggable Splitters:** Adjust pane widths smoothly with draggable splitter handles.
* **Dedicated Settings Repository (`db/settings.db`):** 4-tab settings UI (General, AI, Storage, System) managing preferences and API secrets locally with isolated connections, custom system prompts, live hardware diagnostics, and factory reset.

### 10. Robust SQLite Persistence & Privacy
* **Write-Ahead Logging (WAL):** Local SQLite storage (`db/notes.db` and `db/settings.db`) configured with WAL mode for rapid, non-blocking concurrent reads and writes.
* **Thread-Local Safety:** Managed via thread-local connections to guarantee thread safety across workers with cascading foreign keys (`PRAGMA foreign_keys = ON`).
* **Custom Database Paths (`CUSTOM_DB_PATH`):** Full flexibility for users to specify custom database directories.
* **Zero Data Leakage:** All databases and logs reside locally and are strictly excluded from version control.

### 11. Comprehensive Testing & Engineering Rigor
* **Extensive Automated Test Suite:** **291 passing automated unit tests** across 23 test suites covering domain models, UI view components, AI parsers, RAG vector retrieval, cross-encoder reranking, and SQLite transactions.
* **Fast Test Execution:** Entire test suite runs hermetically in ~15-16 seconds.

---

## Technologies Used

* **Desktop Framework:** Python 3.13, Flet (Flutter Desktop Runtime)
* **AI & Inference:** `llama-cpp-python` (Vulkan GPU compute), Google Gemini API (`google-genai` SDK)
* **RAG & NLP:** Microsoft Harrier 0.6B (Embeddings), Qwen3-Reranker 0.6B (Cross-Encoder), NumPy
* **Document & Graph Processing:** PyPDF, PyGraphviz, Python-Markdown, KaTeX
* **Storage & Systems:** SQLite (WAL mode, Thread-Local Connections), psutil, requests
* **Testing:** Pytest (291 unit tests)
