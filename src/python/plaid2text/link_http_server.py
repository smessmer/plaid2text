from http.server import HTTPServer, SimpleHTTPRequestHandler
from contextlib import contextmanager
from threading import Thread
import os

class CSPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # self.send_header('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.plaid.com ;")
        super().end_headers()

    def translate_path(self, path):
        # Serve files from the specified directory without changing global working directory
        if self.directory:
            return os.path.join(self.directory, path.lstrip('/'))
        return super().translate_path(path)

@contextmanager
def run_link_http_server(serve_directory: str):
    handler = lambda *args, **kwargs: CSPRequestHandler(*args, directory=serve_directory, **kwargs)
    httpd = HTTPServer(('localhost', 8000), handler)
    server_thread = Thread(target=httpd.serve_forever)
    server_thread.start()
    try:
        yield httpd
    finally:
        httpd.shutdown()
        server_thread.join()
