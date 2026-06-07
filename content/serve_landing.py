#!/usr/bin/env python3
"""
Simple landing page server for the agency service offering.
Run: python3 serve_landing.py
Then open http://localhost:8080
"""

import http.server
import socketserver
import os

PORT = 8080
DIR = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)


if __name__ == "__main__":
    print(f"\n  🌐 Agency Landing Page")
    print(f"  Open: http://localhost:{PORT}")
    print(f"  Press Ctrl+C to stop\n")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
