import http.server
import socketserver
import os
import cgi
import shutil
import json
from urllib.parse import urlparse
import sys
import urllib.request

# -----------------------------
# Configuration
# -----------------------------
PORT = 8000  # Port for the local server

# Serve from web/out if it exists (Next.js static export), else from web
WEB_OUT_DIR = os.path.join(os.path.dirname(__file__), 'web', 'out')
WEB_DIR = os.path.join(os.path.dirname(__file__), 'web')
if os.path.exists(WEB_OUT_DIR):
    STATIC_DIR = WEB_OUT_DIR
else:
    STATIC_DIR = WEB_DIR
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'Output')  # Directory for generated notebooks

# Detect if Next.js dev server is running (localhost:3000)
def is_next_dev_server_running():
    try:
        with urllib.request.urlopen('http://localhost:3000') as response:
            return response.status == 200
    except Exception:
        return False

NEXT_DEV = is_next_dev_server_running()

# -----------------------------
# HTTP Request Handler
# -----------------------------
class Handler(http.server.SimpleHTTPRequestHandler):
    """
    Custom HTTP handler to:
    - Serve generated notebooks from /Output
    - Handle POST requests to /run-pipeline for file upload and pipeline execution
    - (In dev) Proxy all other requests to Next.js dev server
    - (In prod) Serve static files from /web/out
    """
    def end_headers(self):
        # Allow CORS for local dev (Next.js on 3000)
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:3000')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/Output/'):
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        if self.path == '/':
            # In dev, show a message to use http://localhost:3000
            if NEXT_DEV:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<h2>Next.js dev server is running on <a href='http://localhost:3000'>http://localhost:3000</a>. Please use that for the frontend UI.</h2>")
                return
            else:
                self.path = '/index.html'
                return http.server.SimpleHTTPRequestHandler.do_GET(self)
        # In dev, proxy all other requests to Next.js dev server
        if NEXT_DEV:
            try:
                url = f"http://localhost:3000{self.path}"
                with urllib.request.urlopen(url) as resp:
                    self.send_response(resp.status)
                    for k, v in resp.getheaders():
                        if k.lower() != 'transfer-encoding':
                            self.send_header(k, v)
                    self.end_headers()
                    self.wfile.write(resp.read())
            except Exception as e:
                self.send_error(502, f"Proxy to Next.js dev server failed: {e}")
            return
        # In prod, serve static files
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/run-pipeline':
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            if ctype == 'multipart/form-data':
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                dataset_file = form['dataset']
                dataset_style = form.getvalue('style')
                dataset_path = os.path.join('Web', dataset_file.filename)
                os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
                with open(dataset_path, 'wb') as f:
                    shutil.copyfileobj(dataset_file.file, f)
                import subprocess
                try:
                    result = subprocess.run(
                        ['python', 'run.py', dataset_style], check=True
                    )
                    gen_notebook_name = f"gen_{dataset_style}.ipynb"
                    exe_notebook_name = f"exe_{dataset_style}.ipynb"
                    gen_notebook_url = f"/Output/{gen_notebook_name}"
                    exe_notebook_url = f"/Output/{exe_notebook_name}"
                    response = {'success': True, 'gen_notebook_url': gen_notebook_url, 'exe_notebook_url': exe_notebook_url}
                except subprocess.CalledProcessError as e:
                    response = {'success': False, 'error': str(e)}
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_error(400, "Bad request")
        else:
            self.send_error(404, "Not found")

    def translate_path(self, path):
        if path.startswith('/Output/'):
            return os.path.join(os.path.dirname(__file__), path[1:])
        return os.path.join(STATIC_DIR, path[1:])

# -----------------------------
# Server Entry Point
# -----------------------------
if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever() 