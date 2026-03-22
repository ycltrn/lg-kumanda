#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request, urllib.error, os

TV = ["192.168.1.101"]
PORT = 9090
HTML_FILE = os.path.expanduser("~/lg_remote.html")

class H(BaseHTTPRequestHandler):
    def log_message(self, f, *a):
        print(self.requestline)
    def cors(self):
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
    def do_OPTIONS(self):
        self.send_response(200); self.cors(); self.end_headers()
    def do_GET(self):
        if self.path.startswith("/setip/"):
            TV[0] = self.path[7:]
            print("TV IP set:", TV[0])
            self.send_response(200); self.cors()
            self.send_header("Content-Type","text/plain")
            self.end_headers(); self.wfile.write(b"ok")
        elif self.path == "/" or self.path == "/index.html":
            with open(HTML_FILE, "rb") as f:
                data = f.read()
            self.send_response(200); self.cors()
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers(); self.wfile.write(data)
        else:
            self.send_response(404); self.end_headers()
    def do_POST(self):
        n = int(self.headers.get("Content-Length",0))
        body = self.rfile.read(n)
        url = "http://{}:8080/udap/api/data".format(TV[0])
        print("-> TV:", url)
        try:
            r = urllib.request.Request(url, data=body, method="POST")
            r.add_header("Content-Type","application/atom+xml")
            with urllib.request.urlopen(r, timeout=5) as res:
                data = res.read()
                print("<- TV:", data[:80])
            self.send_response(200); self.cors()
            self.send_header("Content-Type","application/atom+xml")
            self.end_headers(); self.wfile.write(data)
        except Exception as e:
            print("ERR:", e)
            self.send_response(500); self.cors()
            self.end_headers(); self.wfile.write(str(e).encode())

print("Sunucu baslatiliyor: http://127.0.0.1:{}".format(PORT))
print("Tarayicida ac: http://127.0.0.1:{}/".format(PORT))
HTTPServer(("127.0.0.1", PORT), H).serve_forever()
