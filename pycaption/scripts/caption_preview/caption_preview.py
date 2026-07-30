#!/usr/bin/env python3
"""Local caption preview server.

Usage:
    python3 caption_preview.py [directory] [--port PORT]

Serves files from the given directory (default: cwd) and opens a browser
with a Video.js player for visual caption evaluation.
"""

import argparse
import functools
import http.server
import os
import webbrowser


EXTRA_MIME_TYPES = {
    ".vtt": "text/vtt",
    ".srt": "text/plain",
    ".dfxp": "application/ttml+xml",
    ".ttml": "application/ttml+xml",
    ".smi": "text/plain",
    ".sami": "text/plain",
    ".scc": "text/plain",
}

HERE = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, media_dir, **kwargs):
        self.media_dir = media_dir
        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        if path == "/" or path == "/index.html":
            return os.path.join(HERE, "index.html")
        return super().translate_path(path)

    def guess_type(self, path):
        ext = os.path.splitext(path)[1].lower()
        return EXTRA_MIME_TYPES.get(ext, super().guess_type(path))

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()


def main():
    parser = argparse.ArgumentParser(description="Caption preview server")
    parser.add_argument("directory", nargs="?", default=".",
                        help="Directory to serve media/caption files from")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    media_dir = os.path.abspath(args.directory)
    os.chdir(media_dir)

    handler = functools.partial(Handler, media_dir=media_dir)
    server = http.server.HTTPServer(("127.0.0.1", args.port), handler)

    url = f"http://localhost:{args.port}"
    print(f"Serving files from: {media_dir}")
    print(f"Preview at: {url}")
    print("Press Ctrl+C to stop.\n")

    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
