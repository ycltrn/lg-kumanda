#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error
import json

TV_IP = [""]
PORT = 9090

class ProxyHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Cookie")

    def do_GET(self):
        if self.path == "/ping":
            self.send_response(200)
            self.send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "tv_ip": TV_IP[0]}).encode())
        elif self.path.startswith("/set_ip?"):
            ip = self.path.split("?ip=")[1] if "?ip=" in self.path else ""
            TV_IP[0] = ip.strip()
            self.send_response(200)
            self.send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "tv_ip": TV_IP[0]}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        if self.path.startswith("/tv/"):
            tv_path = self.path[3:]
            tv_url = "http://{}:8080{}".format(TV_IP[0], tv_path)
            try:
                req = urllib.request.Request(tv_url, data=body, method="POST")
                req.add_header("Content-Type", "application/atom+xml")
                with urllib.request.urlopen(req, timeout=5) as resp:
                    resp_body = resp.read()
                    self.send_response(200)
                    self.send_cors_headers()
                    self.send_header("Content-Type", "application/atom+xml")
                    self.end_headers()
                    self.wfile.write(resp_body)
            except urllib.error.HTTPError as e:
                resp_body = e.read()
                self.send_response(e.code)
                self.send_cors_headers()
                self.send_header("Content-Type", "application/atom+xml")
                self.end_headers()
                self.wfile.write(resp_body)
            except Exception as e:
                self.send_response(500)
                self.send_cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print("LG TV Proxy baslatiliyor: http://127.0.0.1:{}".format(PORT))
    print("Durdurmak icin: CTRL+C")
    server = HTTPServer(("127.0.0.1", PORT), ProxyHandler)
    server.serve_forever()
