#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request, urllib.error, os, re

TV = ["192.168.1.101"]
SESSION = [""]
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

        # Endpoint sec
        if 'AuthKeyReq' in body_str or 'AuthReq' in body_str or 'hello' in body_str:
            tv_path = "/udap/api/pairing"
        else:
            tv_path = "/udap/api/data"

        url = "http://{}:8080{}".format(TV[0], tv_path)
        print("-> {} | session={}".format(tv_path, SESSION[0][:20] if SESSION[0] else "none"))

        try:
            r = urllib.request.Request(url, data=body, method="POST")
            r.add_header("Content-Type","application/atom+xml")
            # Session key varsa gonder
            if SESSION[0]:
                r.add_header("Cookie", "session={}".format(SESSION[0]))

            with urllib.request.urlopen(r, timeout=5) as res:
                data = res.read()
                # Session key yakala
                cookie = res.headers.get("Set-Cookie","")
                if cookie and "session=" in cookie:
                    m = re.search(r'session=([^;]+)', cookie)
                    if m:
                        SESSION[0] = m.group(1)
                        print("SESSION KEY:", SESSION[0][:20])
                # XML'den session key yakala
                data_str = data.decode('utf-8', errors='ignore')
                m = re.search(r'<session>([^<]+)</session>', data_str)
                if m:
                    SESSION[0] = m.group(1)
                    print("SESSION KEY XML:", SESSION[0][:20])
                print("<-", data_str[:80])

            self.send_response(200); self.cors()
            self.send_header("Content-Type","application/atom+xml")
            self.end_headers(); self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            print("<- ERR", e.code)
            self.send_response(e.code); self.cors()
            self.send_header("Content-Type","application/atom+xml")
            self.end_headers(); self.wfile.write(data)
        except Exception as e:
            print("ERR:", e)
            self.send_response(500); self.cors()
            self.end_headers(); self.wfile.write(str(e).encode())

print("Sunucu: http://127.0.0.1:{}".format(PORT))
HTTPServer(("127.0.0.1", PORT), H).serve_forever()
