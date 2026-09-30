import os
from flask import Flask, send_from_directory

DEFAULT_DOCS_DIR = 'docs'


def create_app(docs_dir=DEFAULT_DOCS_DIR):
    """
    Application factory for the development server.
    Serves generated static files directly from the build directory.
    """
    server = Flask(__name__, static_folder=None)
    server.config['DOCS_DIR'] = docs_dir

    @server.route('/')
    def index():
        """Serves index.html from the build directory."""
        target_dir = server.config['DOCS_DIR']
        return send_from_directory(target_dir, 'index.html')

    @server.route('/<path:path>')
    def serve_static(path):
        """
        Serves static assets and pages.
        Falls back to directory index.html or adds .html extension if applicable.
        """
        target_dir = server.config['DOCS_DIR']
        full_path = os.path.join(target_dir, path)

        if os.path.isdir(full_path):
            return send_from_directory(full_path, 'index.html')

        if not os.path.exists(full_path) and os.path.exists(full_path + '.html'):
            return send_from_directory(target_dir, path + '.html')

        return send_from_directory(target_dir, path)

    return server


# Default instance for WSGI runners or direct imports
app = create_app()


if __name__ == '__main__':
    target_docs = app.config['DOCS_DIR']
    if not os.path.exists(target_docs):
        print("---")
        print(f"ERROR: The '{target_docs}' directory does not exist.")
        print("Please run 'python build.py' first to compile the site.")
        print("---")
    else:
        print("---")
        print("Starting development server...")
        print(f"Serving files from the '{target_docs}' directory.")
        print("Access the site at http://localhost:5000")
        print("To rebuild the site, stop this server (Ctrl+C) and run 'python build.py' again.")
        print("---")
        app.run(debug=True, host='0.0.0.0', port=5000)
