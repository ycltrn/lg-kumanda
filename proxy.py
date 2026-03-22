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
            print("TV IP:", TV[0])
            self.send_response(200); self.cors()
            self.send_header("Content-Type","text/plain")
            self.end_headers(); self.wfile.write(b"ok")
        elif self.path in ["/", "/index.html"]:
            with open(HTML_FILE, "rb") as f:
                data = f.read()
            self.send_response(200); self.cors()
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.end_headers(); self.wfile.write(data)
        else:
            self.send_response(404); self.end_headers()
    def do_POST(self):
        n = int(self.headers.get("Content-Length",0))
        body = self.rfile.read(n)
        body_str = body.decode('utf-8', errors='ignore')
        
        # Pairing istekleri icin dogru endpoint sec
        if 'AuthKeyReq' in body_str:
            tv_path = "/udap/api/pairing"
        elif 'AuthReq' in body_str or 'hello' in body_str:
            tv_path = "/udap/api/pairing"
        else:
            tv_path = "/udap/api/data"
            
        url = "http://{}:8080{}".format(TV[0], tv_path)
        print("-> {} {}".format(tv_path, body_str[:50]))
        try:
            r = urllib.request.Request(url, data=body, method="POST")
            r.add_header("Content-Type","application/atom+xml")
            with urllib.request.urlopen(r, timeout=5) as res:
                data = res.read()
                print("<-", data[:80])
            self.send_response(200); self.cors()
            self.send_header("Content-Type","application/atom+xml")
            self.end_headers(); self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            print("<- ERR", e.code, data[:80])
            self.send_response(e.code); self.cors()
            self.send_header("Content-Type","application/atom+xml")
            self.end_headers(); self.wfile.write(data)
        except Exception as e:
            print("ERR:", e)
            self.send_response(500); self.cors()
            self.end_headers(); self.wfile.write(str(e).encode())

print("Sunucu: http://127.0.0.1:{}".format(PORT))
HTTPServer(("127.0.0.1", PORT), H).serve_forever()
