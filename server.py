#!/usr/bin/env python3
import http.server
import socketserver

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[platform-api] {format % args}")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"[platform-api] Sagar Serving on port {PORT}")
    httpd.serve_forever()


