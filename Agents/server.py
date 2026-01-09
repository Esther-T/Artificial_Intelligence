from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import json
from judge import detect_intent

PORT = int(os.environ.get("PORT", 8000))

class SimpleHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"No data received")
                return

            post_data = self.rfile.read(content_length)
            post_data_str = post_data.decode()

            try:
                data = json.loads(post_data_str)
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid JSON")
                return

            user_input = data.get("user_input", "")
            print("User input:", user_input)

            verdict = detect_intent(user_input)

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(verdict.encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode())


server = HTTPServer(("", PORT), SimpleHandler)
print(f"Server running on port {PORT}...")
server.serve_forever()
