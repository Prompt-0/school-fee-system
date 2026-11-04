"""
CLI Entrypoint for running the Web Terminal server directly:
    python -m web_terminal [--port 8080] [--host 127.0.0.1]
"""

from __future__ import annotations

import argparse
import os

from web_terminal.server import run_terminal_server


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="web_terminal",
        description="Delhi Public Academy — In-Browser Web Terminal Console Server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 8080)),
        help="Port to listen on (default: 8080 or $PORT env)",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "127.0.0.1"),
        help="Host address to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="Custom SQLite database file path",
    )
    args = parser.parse_args()
    run_terminal_server(host=args.host, port=args.port, db_path=args.db)


if __name__ == "__main__":
    main()
