#!/usr/bin/env python3
"""Run Collection Explorer locally with Python 3.9+ and no installed packages.

Usage: python3 app.py --port 8000 --no-browser
The API and browser assets are served together. The dataset stays on the server;
only documented JSON routes and explicitly permitted public assets are served.
"""

import argparse
import json
import sys
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import parse_qs, unquote, urlsplit

from collection_core import DatasetError, QueryError, load_dataset, query_records


ROOT = Path(__file__).resolve().parent
PUBLIC_FILES = {"/index.html": "text/html; charset=utf-8",
                "/styles.css": "text/css; charset=utf-8",
                "/script.js": "text/javascript; charset=utf-8"}
ASSET_TYPES = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
               ".jpeg": "image/jpeg", ".webp": "image/webp", ".avif": "image/avif",
               ".gif": "image/gif", ".ico": "image/x-icon", ".woff": "font/woff",
               ".woff2": "font/woff2"}


def make_handler(metadata: Dict[str, Any], records: List[Dict[str, Any]], root: Path):
    """Bind a validated dataset to a handler, with no global mutable request state."""
    static_root = Path(root).resolve()
    objects = {record["id"]: record for record in records}

    class CollectionHandler(BaseHTTPRequestHandler):
        server_version = "CollectionExplorer/1.0"
        sys_version = ""

        def log_message(self, format, *args):
            """Keep serving if the terminal which received request logs closes."""
            try:
                super().log_message(format, *args)
            except (OSError, ValueError):
                pass

        def _send_bytes(self, status, content, content_type):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(content)

        def _send_json(self, status, payload):
            content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self._send_bytes(status, content, "application/json; charset=utf-8")

        def send_error(self, code, message=None, explain=None):
            """Keep unsupported methods and malformed requests in the JSON format."""
            message = message or HTTPStatus(code).phrase
            self._send_json(code, {"error": message})

        def _serve_static(self, path):
            if path == "/":
                path = "/index.html"
            parts = path.split("/")
            if "\\" in path or "\x00" in path or any(part in (".", "..") for part in parts):
                self._send_json(404, {"error": "Page not found."})
                return
            content_type = PUBLIC_FILES.get(path)
            if path.startswith("/assets/"):
                content_type = ASSET_TYPES.get(Path(path).suffix.lower())
            if content_type is None:
                self._send_json(404, {"error": "Page not found."})
                return
            candidate = static_root / path.lstrip("/")
            file_path = candidate.resolve()
            try:
                file_path.relative_to(static_root)
            except ValueError:
                self._send_json(404, {"error": "Page not found."})
                return
            # Public aliases must not expose data or source through symlinks.
            if file_path != candidate or not file_path.is_file():
                self._send_json(404, {"error": "Page not found."})
                return
            self._send_bytes(200, file_path.read_bytes(), content_type)

        def do_GET(self):
            try:
                target = urlsplit(self.path)
                path = unquote(target.path, errors="strict")
                if len(target.query) > 4096:
                    raise QueryError("The request contains too much search text.")
                if path == "/api/collections":
                    try:
                        params = parse_qs(target.query, keep_blank_values=True, max_num_fields=30)
                    except ValueError as exc:
                        raise QueryError("The request contains too many parameters.") from exc
                    self._send_json(200, query_records(records, params))
                elif path == "/api/meta":
                    self._send_json(200, {**metadata, "count": len(records)})
                elif path.startswith("/api/objects/"):
                    record = objects.get(path[len("/api/objects/"):])
                    if record is None:
                        self._send_json(404, {"error": "Collection object not found."})
                    else:
                        self._send_json(200, record)
                elif path.startswith("/api/"):
                    self._send_json(404, {"error": "API route not found."})
                else:
                    self._serve_static(path)
            except QueryError as exc:
                self._send_json(400, {"error": str(exc)})
            except (UnicodeError, ValueError):
                self._send_json(400, {"error": "The request URL is invalid."})
            except (BrokenPipeError, ConnectionResetError):
                pass  # A visitor closed the tab before the response finished.
            except Exception as exc:
                self.log_error("Could not complete request: %s", type(exc).__name__)
                self._send_json(500, {"error": "The server could not complete this request."})

        def do_HEAD(self):
            self.do_GET()

        def do_POST(self):
            self._send_json(405, {"error": "Only GET and HEAD requests are supported."})

        do_PUT = do_POST
        do_PATCH = do_POST
        do_DELETE = do_POST

    return CollectionHandler


def main(argv=None):
    parser = argparse.ArgumentParser(description="Start the Collection Explorer web app.")
    parser.add_argument("--host", default="127.0.0.1", help="Interface to bind (default: 127.0.0.1).")
    parser.add_argument("--port", type=int, default=8000, help="Local port (default: 8000).")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser automatically.")
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535.")
    try:
        metadata, records = load_dataset(ROOT / "data" / "collections.json")
        server = ThreadingHTTPServer((args.host, args.port), make_handler(metadata, records, ROOT))
    except (DatasetError, OSError) as exc:
        print("Could not start Collection Explorer: {}".format(exc), file=sys.stderr, flush=True)
        return 1
    display_host = "127.0.0.1" if args.host in ("0.0.0.0", "::") else args.host
    url = "http://{}:{}/".format(display_host, args.port)
    print("Collection Explorer: {} ({} collection records)".format(url, len(records)), flush=True)
    print("Press Ctrl+C to stop the server.", flush=True)
    if not args.no_browser:
        opener = threading.Timer(0.4, webbrowser.open, args=(url,))
        opener.daemon = True
        opener.start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCollection Explorer stopped.", flush=True)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
