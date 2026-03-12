#!/usr/bin/env python3
"""
Startpage static file server — Python 3.13+ compatible.
Serves index.html at / without a redirect, keeping the URL clean.
"""
import http.server
import os
from pathlib import Path

PORT = 8080
SERVE_DIR = Path("/app")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SERVE_DIR), **kwargs)

    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.path = "/index.html"
        super().do_GET()

    def log_message(self, fmt, *args):
        # Only log errors
        if args and str(args[1]) not in ("200", "304"):
            super().log_message(fmt, *args)


if __name__ == "__main__":
    os.chdir(SERVE_DIR)
    with http.server.ThreadingHTTPServer(("", PORT), Handler) as httpd:
        print(f"Startpage running at http://0.0.0.0:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
