import json
import requests
from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = 8111

with open("credentials.json") as f:
    creds = json.load(f)

CLIENT_ID = creds["clientId"]
CLIENT_SECRET = creds["clientSecret"]

TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
API_URL = "https://opensky-network.org/api/states/all"

access_token = None

def get_token():
    global access_token
    r = requests.post(
        TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET),
        timeout=10
    )
    r.raise_for_status()
    access_token = r.json()["access_token"]

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        global access_token

        if self.path == "/api/planes":
            if not access_token:
                get_token()

            headers = {"Authorization": f"Bearer {access_token}"}
            r = requests.get(API_URL, headers=headers)

            if r.status_code == 401:
                get_token()
                headers["Authorization"] = f"Bearer {access_token}"
                r = requests.get(API_URL, headers=headers)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(r.content)
        else:
            # Let Python serve all static files normally
            super().do_GET()

if __name__ == "__main__":
    get_token()
    print(f"Server running on http://localhost:{PORT}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()