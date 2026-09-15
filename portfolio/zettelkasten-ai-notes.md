# Zettelkasten AI Notes

A desktop knowledge management system implementing the **Zettelkasten** methodology, built with **Python** and the **Flet** UI framework. Originally recognized as a **Top 10 Finalist at the Pupilica AI Hackathon**, the project has evolved into a privacy-first, modular desktop environment that transforms unstructured documents into an interconnected web of atomic notes.

It features a **Dual AI Engine** offering both cloud-based analysis via Google Gemini and 100% offline local inference using GGUF models accelerated by Vulkan GPU compute, coupled with an interactive canvas mind map, an advanced live Markdown editor, and a smart bidirectional [[WikiLink]] system.

---

## Architecture & Core Capabilities

### 1. Dual AI Extraction Engine (Cloud & Offline Local)
The core feature of Zettelkasten AI Notes is its ability to ingest dense PDF documents, extract meaningful atomic insights, and establish semantic relationships:

* **Cloud AI (Google Gemini API):** Fast, high-throughput extraction utilizing the official `google-genai` SDK for users with an API key.
* **Offline Local AI (GGUF via Vulkan GPU):** Privacy-first, local LLM inference powered by `llama-cpp-python` with cross-vendor **Vulkan GPU acceleration** (compatible with NVIDIA, AMD, Intel, and Apple Silicon).
* **Process-Isolated Execution:** Local inference executes inside a dedicated `multiprocessing` worker. This prevents GUI thread freezes and deadlocks with Wayland/Vulkan presentation pipelines, keeping the interface fluid while ensuring immediate memory reclamation upon task completion or cancellation.
* **Intelligent Response Parsing (`AiResponseParser`):** A multi-stage JSON recovery pipeline that strips academic citation markers (`[1]`, `[Smith et al.]`), ignores structural headings (Figure, Table, Section), and repairs malformed LLM responses into clean graph connections.

### 2. In-App Model Manager & Downloader
Users can run local AI without setting up external servers or command-line tools:

* **Curated Local Model Catalog:** Pre-configured models tailored for different hardware tiers, including the **Gemma 4 family** (Lightweight E2B 3.2 GB with a 128K context window, Balanced 12B 6.2 GB, and Flagship 26B MoE 13.1 GB).
* **Chunked HTTP Downloader:** Integrated background downloader fetching models directly from Hugging Face with live progress indicators, download speed, ETA calculation, and cancellation support.

### 3. Hardware Resource Inspector & OOM Guard
* **Proactive Resource Detection:** Automatically detects host system RAM, CPU cores, GPU devices, and available VRAM.
* **Out-Of-Memory (OOM) Protection:** Validates system headroom before downloading or loading models into memory.
* **Dynamic Layer Offloading:** Automatically computes the optimal number of GPU offloading layers (`n_gpu_layers`) based on current hardware capability.

### 4. Advanced Live Markdown Workspace
* **Source & Reading Modes:** Seamlessly toggle between raw Markdown editing and formatted preview using `Ctrl+E` or the header toolbar button.
* **Rich Formatting Toolbar:** One-click shortcuts for Headings (H1–H4), bold (`Ctrl+B`), italic (`Ctrl+I`), strikethrough, syntax-highlighted code blocks, blockquotes, lists, tables, and horizontal rules.
* **Interactive Task Checklists:** Toggle `- [ ]` and `- [x]` checkboxes with direct click interaction in both editing and reading modes.
* **LaTeX Math Normalization:** Full support for inline math (`$ ... $`, `\( ... \)`) and display math (`$$ ... $$`, `\[ ... \]`) rendered cleanly within the Flet Markdown viewer.
* **Document Telemetry:** Live counter tracking words, characters, lines, and estimated reading time.
* **Debounced Auto-Save:** Background non-blocking auto-save with dirty state indicators (`*`) to ensure no thoughts are lost.

### 5. Smart Bidirectional [[WikiLink]] System
* **WikiLink Syntax:** Connect concepts effortlessly using `[[Note Title]]` or `[[Target Note|Custom Alias]]`.
* **Interactive Navigation & Auto-Creation:** Clicking any WikiLink jumps straight to that note. If the target note does not exist yet, the application prompts to create and link it in a single click.
* **Quick Link Picker (`Ctrl+K`):** Fast search modal to quickly insert links and establish directional or bidirectional connections between notes.

### 6. Interactive Canvas Mind Map & Knowledge Graph
* **Canvas Rendering:** Hardware-accelerated dynamic graph rendering via `flet.canvas` with automatic node layout calculation using `PyGraphviz`.
* **Pan & Zoom Navigation:** Smooth, fluid navigation powered by `InteractiveViewer` controls.
* **Direct Interaction:** Clicking any node on the graph canvas instantly focuses and opens the note in the editor workspace.

### 7. Modular 3-Pane Responsive Layout
* **Left Sidebar:** Filter collections, search in real-time, view note counts, and access configuration settings.
* **Center Workspace:** Markdown editor, reading preview, and note action buttons.
* **Right Panel:** Interactive Mind Map canvas and Linked Notes relationship inspector.
* **Collapsible Narrow Rails:** Minimize the left sidebar (`Ctrl+[`) or right panel (`Ctrl+]`) into compact 50px icon rails to maximize editor focus.
* **Draggable Splitters:** Adjust pane widths smoothly with draggable splitter handles.

### 8. Robust SQLite Persistence
* **Write-Ahead Logging (WAL):** Local SQLite storage configured with WAL mode for rapid, non-blocking concurrent reads and writes.
* **Thread-Local Safety:** Managed via thread-local connections to guarantee thread safety across workers.
* **Foreign Key Constraints:** Cascading deletes and relational integrity enforced (`PRAGMA foreign_keys = ON`).

---

## Technologies Used

* **Desktop Framework:** Python, Flet
* **AI & Inference:** `llama-cpp-python` (Vulkan GPU acceleration), Google Gemini API (`google-genai`)
* **Document & Graph Processing:** `pypdf`, `pygraphviz`, `markdown`
* **Storage & Systems:** SQLite (WAL mode), `psutil`, `requests`
