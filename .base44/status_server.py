#!/usr/bin/env python3
"""Sandbox status page for Cinnabar.

The sandbox preview is a browser iframe on port 3000, but this repository builds
a native desktop client, so there is no application web server to point it at.
This page reports the real state of the Cargo (Rust) and Go builds that
docker-compose.base44.yml runs from this checkout: toolchain versions, outcome,
and the build log tail, plus whether the expected binaries exist.

It is sandbox scaffolding only - it is not part of the client or the core.
"""

from __future__ import annotations

import html
import http.server
import os
import pathlib

PORT = 3000
ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE = ROOT / ".local" / "base44"
TAIL_LINES = 40

JOBS = (
    {
        "key": "rust-build",
        "title": "Rust client build (Cargo)",
        "detail": "cargo fetch --locked && cargo build --locked -p bedrock-client",
        "artifact": ROOT / "target" / "debug" / "bedrock-client",
        "artifact_label": "target/debug/bedrock-client",
    },
    {
        "key": "go-core",
        "title": "Go core (vet, build, test)",
        "detail": "go vet ./core/... && go build ./core/cmd/bedrock-core && go test ./core/...",
        "artifact": STATE / "bin" / "bedrock-core",
        "artifact_label": ".local/base44/bin/bedrock-core",
    },
)


def read_status(key: str) -> str:
    try:
        return (STATE / f"{key}.status").read_text(encoding="utf-8").strip()
    except OSError:
        return "pending"


def read_log(key: str) -> list[str]:
    try:
        text = (STATE / f"{key}.log").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return text.splitlines()


def job_html(job: dict) -> str:
    status = read_status(job["key"])
    artifact = job["artifact"]
    exists = artifact.exists()
    lines = read_log(job["key"])
    head = "\n".join(lines[:3])
    tail = "\n".join(lines[-TAIL_LINES:]) or "(no output yet)"

    return f"""
    <section class="card {html.escape(status)}">
      <h2>{html.escape(job['title'])} <span class="badge">{html.escape(status)}</span></h2>
      <p class="cmd">{html.escape(job['detail'])}</p>
      <p class="artifact">artifact <code>{html.escape(job['artifact_label'])}</code>:
        <strong>{'present' if exists else 'absent'}</strong></p>
      <details>
        <summary>toolchain</summary>
        <pre>{html.escape(head) or '(not started)'}</pre>
      </details>
      <pre class="log">{html.escape(tail)}</pre>
    </section>
    """


def page() -> str:
    cards = "".join(job_html(job) for job in JOBS)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="10">
<title>Cinnabar - sandbox status</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; padding: 2rem 1.25rem 4rem; background: #14161a; color: #e6e8eb;
         font: 15px/1.5 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }}
  main {{ max-width: 900px; margin: 0 auto; }}
  h1 {{ margin: 0 0 .35rem; font-size: 1.55rem; letter-spacing: -.01em; }}
  .note {{ margin: 0 0 1.75rem; max-width: 70ch; color: #9aa3ad; }}
  .note code {{ color: #cfd6de; }}
  .card {{ margin-bottom: 1.25rem; padding: 1.1rem 1.2rem 1.2rem; border: 1px solid #262b32;
           border-radius: 10px; background: #1a1d22; }}
  .card.ok {{ border-color: #2f6b45; }}
  .card.failed {{ border-color: #7a3030; }}
  .card.running {{ border-color: #6b5a2f; }}
  h2 {{ margin: 0 0 .5rem; font-size: 1.05rem; display: flex; align-items: center; gap: .6rem; }}
  .badge {{ font-size: .72rem; text-transform: uppercase; letter-spacing: .06em;
            padding: .15rem .5rem; border-radius: 999px; background: #2a2f36; color: #aeb7c2; }}
  .card.ok .badge {{ background: #1d3d2a; color: #8fd8a8; }}
  .card.failed .badge {{ background: #45201f; color: #f0a6a0; }}
  .card.running .badge {{ background: #403720; color: #e6cf92; }}
  .cmd {{ margin: 0 0 .35rem; font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
          font-size: .82rem; color: #b9c2cc; }}
  .artifact {{ margin: 0 0 .8rem; font-size: .85rem; color: #9aa3ad; }}
  code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
  details summary {{ cursor: pointer; color: #9aa3ad; font-size: .85rem; }}
  pre {{ margin: .7rem 0 0; padding: .8rem .9rem; overflow-x: auto; border-radius: 8px;
         background: #101215; font-size: .78rem; line-height: 1.45; color: #c8d0d9; }}
</style>
</head>
<body>
<main>
  <h1>Cinnabar - sandbox status</h1>
  <p class="note">
    This repository builds a <strong>native desktop client</strong> (Rust + Bevy) with a
    <strong>Go networking core</strong> (<code>core/cmd/bedrock-core</code>); it contains no web
    frontend, so the preview cannot render the game window itself. This page reports the live
    state of the Cargo and Go builds running from this checkout.
  </p>
  {cards}
  <p class="note">Auto-refreshes every 10 seconds.</p>
</main>
</body>
</html>
"""


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:  # noqa: N802
        body = page().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        pass


if __name__ == "__main__":
    STATE.mkdir(parents=True, exist_ok=True)
    os.chdir(ROOT)
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"status page on http://0.0.0.0:{PORT}", flush=True)
    server.serve_forever()
