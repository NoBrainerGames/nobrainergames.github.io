import http.server
import socketserver
import signal
import sys

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

class TCPServerReusable(socketserver.TCPServer):
    allow_reuse_address = True

def signal_handler(sig, frame):
    print('\nShutting down server...')
    httpd.shutdown()
    httpd.server_close()
    sys.exit(0)

PORT = 8000
Handler = CORSHTTPRequestHandler

signal.signal(signal.SIGINT, signal_handler)

with TCPServerReusable(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
