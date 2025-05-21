import http.server
import socketserver
import os
import cgi
import shutil
import json
from urllib.parse import urlparse

# -----------------------------
# Configuration
# -----------------------------
PORT = 8000  # Port for the local server
WEB_DIR = os.path.join(os.path.dirname(__file__), 'web')  # Directory for static files (HTML, CSS, JS)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'Output')  # Directory for generated notebooks

# -----------------------------
# HTTP Request Handler
# -----------------------------
class Handler(http.server.SimpleHTTPRequestHandler):
    """
    Custom HTTP handler to:
    - Serve static files from /web (frontend)
    - Serve generated notebooks from /Output
    - Handle POST requests to /run-pipeline for file upload and pipeline execution
    """
    def do_GET(self):
        """
        Handle GET requests:
        - /                -> Serves web/index.html
        - /Output/...      -> Serves generated notebook files
        - /[other static]  -> Serves static files from web/
        """
        if self.path.startswith('/Output/'):
            # Serve generated notebooks (e.g., /Output/gen_A_1_one_csv.ipynb)
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        if self.path == '/':
            self.path = '/index.html'  # Default to index.html
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        """
        Handle POST requests:
        - /run-pipeline: Receives a file and dataset style, saves the file, runs the pipeline, and returns a JSON response.
        """
        if self.path == '/run-pipeline':
            # Parse multipart form data
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            if ctype == 'multipart/form-data':
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                # Extract uploaded file and dataset style from the form
                dataset_file = form['dataset']  # Uploaded file (input name="dataset")
                dataset_style = form.getvalue('style')  # Selected dataset style (input name="style")

                # Save uploaded file to Datasets/Tabular/Binary_pred/csv/
                # (This path is expected by the pipeline for A_1_one_csv style)
                dataset_path = os.path.join('Web', dataset_file.filename)
                os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
                with open(dataset_path, 'wb') as f:
                    shutil.copyfileobj(dataset_file.file, f)

                # Run the pipeline as a subprocess, passing style and file path
                import subprocess
                try:
                    result = subprocess.run(
                        ['python', 'run.py', dataset_style], check=True
                    )
                    # On success, the pipeline generates Output/gen_{dataset_style}.ipynb
                    gen_notebook_name = f"gen_{dataset_style}.ipynb"
                    exe_notebook_name = f"exe_{dataset_style}.ipynb"
                    gen_notebook_url = f"/Output/{gen_notebook_name}"
                    exe_notebook_url = f"/Output/{exe_notebook_name}"
                    response = {'success': True, 'gen_notebook_url': gen_notebook_url, 'exe_notebook_url': exe_notebook_url}
                except subprocess.CalledProcessError as e:
                    # On error, return the error message
                    response = {'success': False, 'error': e.stderr}

                # Return JSON response to the frontend
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                # If not multipart/form-data, return 400 error
                self.send_error(400, "Bad request")
        else:
            # Any other POST endpoint is not found
            self.send_error(404, "Not found")

    def translate_path(self, path):
        """
        Map URL paths to local filesystem paths:
        - /Output/... -> Output/...
        - /...        -> web/...
        """
        if path.startswith('/Output/'):
            return os.path.join(os.path.dirname(__file__), path[1:])
        return os.path.join(WEB_DIR, path[1:])

# -----------------------------
# Server Entry Point
# -----------------------------
if __name__ == '__main__':
    # Change working directory to project root
    os.chdir(os.path.dirname(__file__))
    # Start the server
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever() 