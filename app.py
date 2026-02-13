import os
from flask import Flask, send_from_directory

# The 'docs' directory is where our static site is built.
# We configure Flask to serve files from there.
# Note: For development, this provides a simple way to test the built site.
app = Flask(__name__)

DOCS_DIR = 'docs'

@app.route('/')
def index():
    """Serves the index.html file from the 'docs' directory."""
    return send_from_directory(DOCS_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """
    Serves any other file (e.g., /about.html, /static/css/style.css)
    from the 'docs' directory.
    """
    return send_from_directory(DOCS_DIR, path)

if __name__ == '__main__':
    if not os.path.exists(DOCS_DIR):
        print("---")
        print("ERROR: The 'docs' directory does not exist.")
        print("Please run 'python build.py' first to build the site.")
        print("---")
    else:
        print("---")
        print("Starting development server...")
        print(f"Serving files from the '{DOCS_DIR}' directory.")
        print("Access the site at http://localhost:5000")
        print("To rebuild the site, stop this server (Ctrl+C) and run 'python build.py' again.")
        print("---")
        # Using Flask's built-in server for simplicity in development.
        app.run(debug=True, host='0.0.0.0', port=5000)
