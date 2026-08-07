# Zettelkasten AI Notes

A desktop application built with `Flet` (Python UI framework based on Flutter) for efficient knowledge management using the Zettelkasten method. It allows users to create, edit, and link notes, supports `Markdown` for rich content, and provides a real-time preview. It stores all data in a local `SQLite` database. A key feature is its ability to use `Google Gemini AI` (via the modern `google-genai` SDK) to generate Zettelkasten-style notes from PDF documents (extracted via `pypdf`) and automatically suggest relevant links between them.

## Key Features

* **Modern User Interface:** Built with `Flet` for a clean, responsive, and cross-platform desktop GUI.
* **Note Creation and Management:** Easily create, save, rename, and delete individual notes.
* **Markdown Support with Live Preview:** Write your notes in `Markdown` and see the generated output in real-time.
* **Categorization:** Organize notes into custom categories for better filtering and navigation.
* **AI-Powered Note Generation from PDF:** Extract text from PDF documents using `pypdf` and utilize the `google-genai` SDK with `Google Gemini AI` to automatically generate Zettelkasten-style notes with suggested relevant links.
* **Flet Canvas Mind Map Visualization:** View your notes and their links as an interactive mind map powered by `flet.canvas`. This helps you visualize relationships between your ideas and navigate your knowledge base seamlessly.
* **Smart Note Linking:** Create explicit links between notes to build a rich, interconnected graph of your knowledge.
* **Theming:** Choose between light and dark themes to customize the application's appearance.
* **SQLite Database:** Robust and reliable local storage for all your notes and their relationships.
* **Comprehensive Test Suite:** Includes automated unit testing for core operations, note title sanitization, and database interactions.
