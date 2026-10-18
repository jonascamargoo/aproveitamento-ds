"""Serve o front-end em http://localhost:5500 sem cache (cada F5 pega a versão nova dos .js/.css).

Uso: python3 frontend/servidor.py
"""

from functools import partial
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from socketserver import ThreadingTCPServer

PORTA = 5500


class HandlerSemCache(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


# TCPServer em vez de HTTPServer: o HTTPServer faz uma consulta de DNS no start que pode demorar no macOS
ThreadingTCPServer.allow_reuse_address = True

if __name__ == "__main__":
    handler = partial(HandlerSemCache, directory=Path(__file__).parent)
    with ThreadingTCPServer(("127.0.0.1", PORTA), handler) as servidor:
        print(f"Front-end em http://localhost:{PORTA}/login.html  (Ctrl+C para parar)")
        servidor.serve_forever()
