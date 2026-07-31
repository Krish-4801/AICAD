import os
import json
import time
import sys

DIRECTORY_REQUESTS = os.path.join(os.getcwd(), 'requests')

def check_pending():
    if not os.path.exists(DIRECTORY_REQUESTS):
        return None
    for req_id in os.listdir(DIRECTORY_REQUESTS):
        req_dir = os.path.join(DIRECTORY_REQUESTS, req_id)
        if os.path.isdir(req_dir):
            req_file = os.path.join(req_dir, 'request.json')
            resp_file = os.path.join(req_dir, 'response.json')
            if os.path.exists(req_file) and not os.path.exists(resp_file):
                try:
                    with open(req_file, 'r') as f:
                        data = json.load(f)
                    if data.get('status') == 'pending':
                        return req_id
                except Exception:
                    pass
    return None

def main():
    print("Agent listener started. Watching requests/ for pending tasks...", flush=True)
    while True:
        req_id = check_pending()
        if req_id:
            print(f"FOUND_PENDING_REQUEST: {req_id}", flush=True)
            sys.exit(0)
        time.sleep(1)

if __name__ == '__main__':
    main()
