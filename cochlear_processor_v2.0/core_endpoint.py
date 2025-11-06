# core_endpoint.py
"""
Core Endpoint – lightweight receiver for Cochlear Processor v2
Accepts incoming sensory matrices from CoreBridge and relays them
into Caleon Core or logs them for local inspection.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading

# -------------------------------------------------------------------
# Simple HTTP Receiver (POST /sensory)
# -------------------------------------------------------------------
class SensoryHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/sensory":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        try:
            data = json.loads(body)
            process_sensory_data(data)
            self.send_response(200)
        except Exception as e:
            self.send_response(400)
            print(f"[CORE_ENDPOINT] Error: {e}")
        self.end_headers()


def start_server(host="0.0.0.0", port=8088):
    """Run the HTTP listener in a background thread."""
    server = HTTPServer((host, port), SensoryHandler)
    print(f"[CORE_ENDPOINT] Listening on http://{host}:{port}/sensory")
    threading.Thread(target=server.serve_forever, daemon=True).start()


# -------------------------------------------------------------------
# Core Processing Stub (extend for Caleon Core logic)
# -------------------------------------------------------------------
def process_sensory_data(payload: dict):
    """
    Handle incoming sensory packet from Cochlear Processor.
    Extend this to insert data into cortex queue or reasoning modules.
    """
    trace_id = payload.get("trace_id")
    matrix = payload.get("matrix", {})
    print(f"[CORE_ENDPOINT] Received {trace_id} → {matrix}")


# -------------------------------------------------------------------
# Optional standalone execution
# -------------------------------------------------------------------
if __name__ == "__main__":
    start_server()
    print("🧠 Core Endpoint online. Waiting for sensory input...")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\n[CORE_ENDPOINT] Shutting down.")
