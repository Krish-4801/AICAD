import http.server
import json
import os
import re
import urllib.parse
from socketserver import ThreadingTCPServer
import time

PORT = 8080
DIRECTORY_WEB = os.path.join(os.getcwd(), 'web')
DIRECTORY_REQUESTS = os.path.join(os.getcwd(), 'requests')

os.makedirs(DIRECTORY_WEB, exist_ok=True)
os.makedirs(DIRECTORY_REQUESTS, exist_ok=True)

class CADRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # API: Status
        status_match = re.match(r'^/api/status/([^/]+)$', path)
        if status_match:
            req_id = status_match.group(1)
            # Prevent path traversal
            if not req_id.isalnum() and '_' not in req_id:
                self.send_error(400, "Invalid Request ID")
                return

            req_dir = os.path.join(DIRECTORY_REQUESTS, req_id)
            resp_file = os.path.join(req_dir, 'response.json')
            req_file = os.path.join(req_dir, 'request.json')

            if os.path.exists(resp_file):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                with open(resp_file, 'rb') as f:
                    self.wfile.write(f.read())
            elif os.path.exists(req_file):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                with open(req_file, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Request Not Found")
            return

        # API: History
        if path == '/api/history':
            history = []
            if os.path.exists(DIRECTORY_REQUESTS):
                for req_id in os.listdir(DIRECTORY_REQUESTS):
                    req_dir = os.path.join(DIRECTORY_REQUESTS, req_id)
                    if os.path.isdir(req_dir):
                        resp_file = os.path.join(req_dir, 'response.json')
                        req_file = os.path.join(req_dir, 'request.json')
                        if os.path.exists(resp_file):
                            try:
                                with open(resp_file, 'r') as f:
                                    data = json.load(f)
                                # Merge parent_id from request.json if missing
                                if 'parent_id' not in data and os.path.exists(req_file):
                                    try:
                                        with open(req_file, 'r') as rf:
                                            req_data = json.load(rf)
                                            if 'parent_id' in req_data:
                                                data['parent_id'] = req_data['parent_id']
                                    except:
                                        pass
                                history.append(data)
                            except:
                                pass
                        elif os.path.exists(req_file):
                            try:
                                with open(req_file, 'r') as f:
                                    data = json.load(f)
                                history.append(data)
                            except:
                                pass
            
            # Sort history by request id (contains timestamp) descending
            history.sort(key=lambda x: x.get('id', ''), reverse=True)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(history).encode('utf-8'))
            return

        # Serve static files from requests/ directory
        if path.startswith('/requests/'):
            rel_path = path[len('/requests/'):]
            target_path = os.path.abspath(os.path.join(DIRECTORY_REQUESTS, rel_path))
            if not target_path.startswith(os.path.abspath(DIRECTORY_REQUESTS)):
                self.send_error(403, "Forbidden")
                return
            
            if os.path.exists(target_path) and os.path.isfile(target_path):
                self.serve_file(target_path)
            else:
                self.send_error(404, "File Not Found")
            return

        # Serve static files from web/ directory
        if path == '/':
            path = '/index.html'
        
        rel_path = path.lstrip('/')
        target_path = os.path.abspath(os.path.join(DIRECTORY_WEB, rel_path))
        if not target_path.startswith(os.path.abspath(DIRECTORY_WEB)):
            self.send_error(403, "Forbidden")
            return

        if os.path.exists(target_path) and os.path.isfile(target_path):
            self.serve_file(target_path)
        else:
            self.send_error(404, "File Not Found")

    def serve_file(self, file_path):
        content_type = 'application/octet-stream'
        if file_path.endswith('.html'):
            content_type = 'text/html'
        elif file_path.endswith('.css'):
            content_type = 'text/css'
        elif file_path.endswith('.js'):
            content_type = 'application/javascript'
        elif file_path.endswith('.json'):
            content_type = 'application/json'
        elif file_path.endswith('.png'):
            content_type = 'image/png'
        elif file_path.endswith('.stl'):
            content_type = 'model/stl'
        elif file_path.endswith('.step') or file_path.endswith('.stp'):
            content_type = 'application/step'
        elif file_path.endswith('.pptx'):
            content_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(os.path.getsize(file_path)))
        self.end_headers()
        with open(file_path, 'rb') as f:
            self.wfile.write(f.read())

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == '/api/generate':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                prompt = data.get('prompt', '').strip()
                parent_id = data.get('parent_id')
                if not prompt:
                    self.send_error(400, "Prompt is required")
                    return
                
                # Prevent directory traversal
                if parent_id and (not parent_id.isalnum() and '_' not in parent_id):
                    self.send_error(400, "Invalid parent ID")
                    return

                req_id = f"req_{int(time.time())}"
                req_dir = os.path.join(DIRECTORY_REQUESTS, req_id)
                os.makedirs(req_dir, exist_ok=True)
                
                req_data = {
                    "id": req_id,
                    "prompt": prompt,
                    "status": "pending",
                    "timestamp": time.time(),
                    "step": "queued"
                }
                if parent_id:
                    req_data["parent_id"] = parent_id
                    parent_dir = os.path.join(DIRECTORY_REQUESTS, parent_id)
                    parent_py = os.path.join(parent_dir, 'model.py')
                    if os.path.exists(parent_py):
                        import shutil
                        shutil.copy(parent_py, os.path.join(req_dir, 'model.py'))

                with open(os.path.join(req_dir, 'request.json'), 'w') as f:
                    json.dump(req_data, f)
                
                print(f"[AGENT_REQUEST] {req_id}", flush=True)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(req_data).encode('utf-8'))
            except Exception as e:
                self.send_error(500, f"Server Error: {str(e)}")
            return

        self.send_error(404, "Not Found")

def run():
    print(f"Starting server on port {PORT}...", flush=True)
    server_address = ('', PORT)
    httpd = ThreadingTCPServer(server_address, CADRequestHandler)
    print(f"Server is running at http://localhost:{PORT}/", flush=True)
    httpd.serve_forever()

if __name__ == '__main__':
    run()
