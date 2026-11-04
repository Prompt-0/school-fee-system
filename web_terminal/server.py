"""
Web-based Terminal Server for Delhi Public Academy Fee Management.
Serves a self-contained in-browser terminal console connected to TerminalShell via REST.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from typing import Optional, Any

from school_fee_system.services import SchoolFeeService
from web_terminal.shell import TerminalShell


TERMINAL_PAGE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="theme-color" content="#0b0f17">
<title>DPA Fee Console — Web Terminal</title>
<style>
  :root {
    --bg-window: #0b0f17;
    --bg-term: #0f172a;
    --bg-header: #1e293b;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --accent: #2dd4bf;
    --accent-glow: rgba(45, 212, 191, 0.25);
    --prompt-user: #38bdf8;
    --prompt-host: #2dd4bf;
    --prompt-path: #facc15;
    --border-color: #334155;
    --font-term: "Adwaita Mono", "Cascadia Code", "Fira Code", SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    --font-size: 14.5px;
  }

  /* Themes */
  body[data-theme="matrix"] {
    --bg-window: #000000;
    --bg-term: #050b05;
    --bg-header: #0a1f0a;
    --text-main: #22c55e;
    --text-muted: #15803d;
    --accent: #4ade80;
    --accent-glow: rgba(74, 222, 128, 0.35);
    --prompt-user: #4ade80;
    --prompt-host: #86efac;
    --prompt-path: #16a34a;
    --border-color: #14532d;
  }
  body[data-theme="amber"] {
    --bg-window: #0a0601;
    --bg-term: #120c02;
    --bg-header: #261705;
    --text-main: #f59e0b;
    --text-muted: #b45309;
    --accent: #fbbf24;
    --accent-glow: rgba(251, 191, 36, 0.35);
    --prompt-user: #f59e0b;
    --prompt-host: #fbbf24;
    --prompt-path: #d97706;
    --border-color: #451a03;
  }
  body[data-theme="cyberpunk"] {
    --bg-window: #0b0214;
    --bg-term: #130324;
    --bg-header: #24053d;
    --text-main: #f43f5e;
    --text-muted: #9333ea;
    --accent: #06b6d4;
    --accent-glow: rgba(6, 182, 212, 0.4);
    --prompt-user: #f43f5e;
    --prompt-host: #06b6d4;
    --prompt-path: #a855f7;
    --border-color: #4c1d95;
  }
  body[data-theme="nord"] {
    --bg-window: #242933;
    --bg-term: #2e3440;
    --bg-header: #3b4252;
    --text-main: #eceff4;
    --text-muted: #7b88a1;
    --accent: #88c0d0;
    --accent-glow: rgba(136, 192, 208, 0.25);
    --prompt-user: #81a1c1;
    --prompt-host: #88c0d0;
    --prompt-path: #ebcb8b;
    --border-color: #434c5e;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }

  html, body {
    width: 100%;
    height: 100%;
    background-color: var(--bg-window);
    color: var(--text-main);
    font-family: var(--font-term);
    overflow: hidden;
  }

  /* CRT Scanline Effect Overlay (Toggled via button) */
  .crt::after {
    content: " ";
    display: block;
    position: absolute;
    top: 0; left: 0; bottom: 0; right: 0;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
    z-index: 50;
    background-size: 100% 3px, 6px 100%;
    pointer-events: none;
    opacity: 0.65;
  }

  /* Main Container */
  .terminal-wrapper {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    max-width: 1400px;
    margin: 0 auto;
  }

  /* Window Titlebar Header */
  .term-header {
    background: var(--bg-header);
    border-bottom: 1px solid var(--border-color);
    padding: 0.55rem 0.9rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
    user-select: none;
  }
  .window-controls {
    display: flex;
    align-items: center;
    gap: 7px;
  }
  .dot {
    width: 11px;
    height: 11px;
    border-radius: 50%;
    display: inline-block;
  }
  .dot-red { background: #ef4444; }
  .dot-yellow { background: #eab308; }
  .dot-green { background: #22c55e; }

  .term-title {
    font-size: 0.8rem;
    color: var(--text-muted);
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .badge-live {
    font-size: 0.65rem;
    padding: 1px 6px;
    border-radius: 9999px;
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    border: 1px solid rgba(74, 222, 128, 0.3);
    font-weight: 700;
    text-transform: uppercase;
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .action-btn {
    background: transparent;
    border: 1px solid var(--border-color);
    color: var(--text-muted);
    font-family: inherit;
    font-size: 0.72rem;
    padding: 3px 8px;
    border-radius: 5px;
    cursor: pointer;
    transition: all 0.15s ease;
  }
  .action-btn:hover {
    color: var(--text-main);
    border-color: var(--accent);
  }

  /* Output Viewport */
  .term-body {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 1rem;
    background: var(--bg-term);
    font-size: var(--font-size);
    line-height: 1.45;
    -webkit-overflow-scrolling: touch;
    white-space: pre-wrap;
    word-break: break-word;
  }

  .term-output {
    margin-bottom: 0.5rem;
  }
  .term-output pre {
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
    white-space: pre-wrap;
    word-break: break-word;
  }

  /* Active Input Prompt Row */
  .prompt-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.35rem;
    margin-top: 0.25rem;
    padding-bottom: 0.5rem;
  }
  .prompt-label {
    display: inline-flex;
    align-items: center;
    font-weight: 700;
    white-space: nowrap;
  }
  .prompt-user { color: var(--prompt-user); }
  .prompt-at { color: var(--text-muted); }
  .prompt-host { color: var(--prompt-host); }
  .prompt-colon { color: var(--text-muted); }
  .prompt-path { color: var(--prompt-path); }
  .prompt-symbol { color: var(--accent); margin-left: 2px; }

  .input-wrapper {
    flex: 1;
    display: flex;
    align-items: center;
    min-width: 140px;
    position: relative;
  }
  .term-input {
    width: 100%;
    background: transparent;
    border: none;
    outline: none;
    color: var(--text-main);
    font-family: inherit;
    font-size: 16px; /* Avoid mobile browser zoom */
    caret-color: var(--accent);
    padding: 0;
  }

  /* Mobile Quick Action Pill Bar */
  .touch-bar {
    background: var(--bg-header);
    border-top: 1px solid var(--border-color);
    padding: 0.4rem 0.6rem;
    display: flex;
    gap: 0.4rem;
    overflow-x: auto;
    flex-shrink: 0;
    -webkit-overflow-scrolling: touch;
    padding-bottom: calc(0.4rem + env(safe-area-inset-bottom));
  }
  .touch-pill {
    background: var(--bg-term);
    border: 1px solid var(--border-color);
    color: var(--accent);
    padding: 0.35rem 0.65rem;
    border-radius: 6px;
    font-family: inherit;
    font-size: 0.76rem;
    font-weight: 700;
    cursor: pointer;
    white-space: nowrap;
    min-height: 34px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .touch-pill:active {
    background: var(--accent);
    color: #000;
  }

  /* History & Auto-complete suggestions popup */
  .completion-bar {
    color: var(--text-muted);
    font-size: 0.8rem;
    margin-bottom: 0.35rem;
    font-style: italic;
  }

  /* Link styling inside terminal output */
  .term-body a {
    color: var(--accent);
    text-decoration: underline;
  }
</style>
</head>
<body data-theme="teal">
<div class="terminal-wrapper" id="terminalWrapper">
  <!-- Window Header -->
  <header class="term-header">
    <div class="window-controls">
      <span class="dot dot-red"></span>
      <span class="dot dot-yellow"></span>
      <span class="dot dot-green"></span>
    </div>
    <div class="term-title">
      <span>dpa-admin@cbse-terminal: /opt/fee-system</span>
      <span class="badge-live">● Online</span>
    </div>
    <div class="header-actions">
      <button class="action-btn" id="themeBtn" title="Switch Theme">Palette ▾</button>
      <button class="action-btn" id="crtBtn" title="Toggle CRT Scanline Effect">CRT: Off</button>
      <a href="/" class="action-btn" style="text-decoration: none;" title="Open GUI Dashboard">GUI ↗</a>
    </div>
  </header>

  <!-- Output Log Container -->
  <main class="term-body" id="termBody" onclick="focusInput()">
    <div id="termHistory"></div>
    <div class="prompt-row" id="activePromptRow">
      <span class="prompt-label">
        <span class="prompt-user">admin</span><span class="prompt-at">@</span><span class="prompt-host">dpa-terminal</span><span class="prompt-colon">:</span><span class="prompt-path">~</span><span class="prompt-symbol">$</span>
      </span>
      <div class="input-wrapper">
        <input type="text" id="termInput" class="term-input" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" autofocus />
      </div>
    </div>
  </main>

  <!-- Mobile Quick Touch Pill Bar -->
  <nav class="touch-bar">
    <button class="touch-pill" onclick="handleTouchAction('TAB')">⇥ TAB</button>
    <button class="touch-pill" onclick="handleTouchAction('UP')">↑</button>
    <button class="touch-pill" onclick="handleTouchAction('DOWN')">↓</button>
    <button class="touch-pill" onclick="runDirectCmd('help')">help</button>
    <button class="touch-pill" onclick="runDirectCmd('kpis')">kpis</button>
    <button class="touch-pill" onclick="runDirectCmd('students list')">students</button>
    <button class="touch-pill" onclick="runDirectCmd('invoices list')">invoices</button>
    <button class="touch-pill" onclick="runDirectCmd('defaulters')">defaulters</button>
    <button class="touch-pill" onclick="runDirectCmd('reports collection')">revenue</button>
    <button class="touch-pill" onclick="runDirectCmd('clear')">clear</button>
  </nav>
</div>

<script>
// Available commands for auto-completion
const AUTO_COMMANDS = [
  "help", "kpis", "students", "students list", "students view", 
  "invoices", "invoices list", "invoices view", "invoices generate",
  "pay", "receipts", "receipts view", "receipts verify",
  "defaulters", "reports", "reports collection", "classes",
  "theme", "theme teal", "theme matrix", "theme amber", "theme nord", "theme cyberpunk",
  "clear", "banner", "version"
];

const THEMES = ["teal", "matrix", "amber", "nord", "cyberpunk"];
let currentThemeIdx = 0;

// Command history memory
let history = JSON.parse(localStorage.getItem("term_history") || "[]");
let historyIndex = history.length;

const termBody = document.getElementById("termBody");
const termHistory = document.getElementById("termHistory");
const termInput = document.getElementById("termInput");
const themeBtn = document.getElementById("themeBtn");
const crtBtn = document.getElementById("crtBtn");

function focusInput() {
  termInput.focus();
}

// Convert ANSI escape sequences to styled HTML
function ansiToHtml(text) {
  let out = "";
  let openSpans = 0;
  
  // Replace HTML special characters first
  let escaped = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Regex to match ANSI escape codes: \033[...m
  const regex = /\x1B\[([0-9;]+)m/g;
  let lastIdx = 0;
  let match;

  while ((match = regex.exec(escaped)) !== null) {
    out += escaped.substring(lastIdx, match.index);
    lastIdx = regex.lastIndex;
    
    const codes = match[1].split(";");
    if (codes[0] === "0" || codes[0] === "") {
      // Reset all
      while (openSpans > 0) {
        out += "</span>";
        openSpans--;
      }
    } else if (codes[0] === "1") {
      out += '<span style="font-weight: 700;">';
      openSpans++;
    } else if (codes[0] === "2") {
      out += '<span style="opacity: 0.65;">';
      openSpans++;
    } else if (codes[0] === "31") {
      out += '<span style="color: #ef4444; font-weight: 600;">'; // Red
      openSpans++;
    } else if (codes[0] === "32") {
      out += '<span style="color: #22c55e; font-weight: 600;">'; // Green
      openSpans++;
    } else if (codes[0] === "33") {
      out += '<span style="color: #facc15; font-weight: 600;">'; // Yellow
      openSpans++;
    } else if (codes[0] === "34") {
      out += '<span style="color: #38bdf8;">'; // Blue
      openSpans++;
    } else if (codes[0] === "35") {
      out += '<span style="color: #c084fc;">'; // Magenta
      openSpans++;
    } else if (codes[0] === "36") {
      out += '<span style="color: #2dd4bf;">'; // Cyan / Teal
      openSpans++;
    } else if (codes[0] === "37") {
      out += '<span style="color: #f8fafc;">'; // White
      openSpans++;
    } else if (codes[0] === "38" && codes[1] === "2") {
      // 24-bit TrueColor: \033[38;2;r;g;bm
      const r = codes[2], g = codes[3], b = codes[4];
      out += `<span style="color: rgb(${r}, ${g}, ${b});">`;
      openSpans++;
    } else if (codes[0] === "48" && codes[1] === "2") {
      // 24-bit TrueColor background: \033[48;2;r;g;bm
      const r = codes[2], g = codes[3], b = codes[4];
      out += `<span style="background-color: rgb(${r}, ${g}, ${b}); padding: 1px 4px; border-radius: 3px;">`;
      openSpans++;
    }
  }

  out += escaped.substring(lastIdx);
  while (openSpans > 0) {
    out += "</span>";
    openSpans--;
  }
  return out;
}

// Append command and response to terminal view
function appendToTerminal(cmd, output) {
  const block = document.createElement("div");
  block.className = "term-output";

  let promptHtml = `
    <div class="prompt-row" style="margin-bottom: 2px;">
      <span class="prompt-label">
        <span class="prompt-user">admin</span><span class="prompt-at">@</span><span class="prompt-host">dpa-terminal</span><span class="prompt-colon">:</span><span class="prompt-path">~</span><span class="prompt-symbol">$</span>
      </span>
      <span style="font-weight: 600; color: #ffffff; margin-left: 0.35rem;">${escapeHtml(cmd)}</span>
    </div>
  `;

  if (output === "\033[2J\033[H") {
    // Clear screen command
    termHistory.innerHTML = "";
    termBody.scrollTop = 0;
    return;
  }

  block.innerHTML = promptHtml + `<pre>${ansiToHtml(output)}</pre>`;
  termHistory.appendChild(block);
  termBody.scrollTop = termBody.scrollHeight;
}

function escapeHtml(text) {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Execute command via REST API
async function executeCommand(cmdStr) {
  const trimmed = cmdStr.trim();
  if (!trimmed) return;

  // Add to history
  if (history[history.length - 1] !== trimmed) {
    history.push(trimmed);
    if (history.length > 100) history.shift();
    localStorage.setItem("term_history", JSON.stringify(history));
  }
  historyIndex = history.length;

  // Check client-side direct commands
  const tokens = trimmed.split(/\s+/);
  const root = tokens[0].toLowerCase();

  if (root === "clear" || root === "cls") {
    termHistory.innerHTML = "";
    termInput.value = "";
    termBody.scrollTop = 0;
    return;
  }

  if (root === "theme") {
    if (tokens[1]) {
      setTheme(tokens[1].toLowerCase());
      appendToTerminal(trimmed, `\033[32m✓ Theme set to: ${tokens[1]}\033[0m\n`);
    } else {
      cycleTheme();
      appendToTerminal(trimmed, `\033[32m✓ Switched theme to: ${document.body.getAttribute("data-theme")}\033[0m\n`);
    }
    termInput.value = "";
    return;
  }

  try {
    const res = await fetch("/api/exec", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cmd: trimmed })
    });
    const data = await res.json();
    appendToTerminal(trimmed, data.output || "");
  } catch (err) {
    appendToTerminal(trimmed, `\033[31mTerminal Network Error: ${err.message}\033[0m\n`);
  }
  termInput.value = "";
  termBody.scrollTop = termBody.scrollHeight;
}

function runDirectCmd(c) {
  executeCommand(c);
  focusInput();
}

function handleTouchAction(act) {
  if (act === "TAB") {
    triggerTabCompletion();
  } else if (act === "UP") {
    navigateHistory(-1);
  } else if (act === "DOWN") {
    navigateHistory(1);
  }
  focusInput();
}

function navigateHistory(direction) {
  if (history.length === 0) return;
  historyIndex += direction;
  if (historyIndex < 0) historyIndex = 0;
  if (historyIndex > history.length) historyIndex = history.length;

  if (historyIndex === history.length) {
    termInput.value = "";
  } else {
    termInput.value = history[historyIndex];
  }
}

function triggerTabCompletion() {
  const current = termInput.value.trimStart();
  if (!current) return;

  const matches = AUTO_COMMANDS.filter(c => c.startsWith(current));
  if (matches.length === 1) {
    termInput.value = matches[0] + " ";
  } else if (matches.length > 1) {
    // Show match suggestions
    const suggestionText = "\n\033[38;2;148;163;184mSuggestions:\033[0m\n  " + matches.join("   ") + "\n";
    appendToTerminal(current, suggestionText);
  }
}

// Keyboard navigation
termInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    executeCommand(termInput.value);
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    navigateHistory(-1);
  } else if (e.key === "ArrowDown") {
    e.preventDefault();
    navigateHistory(1);
  } else if (e.key === "Tab") {
    e.preventDefault();
    triggerTabCompletion();
  } else if (e.key === "c" && e.ctrlKey) {
    e.preventDefault();
    appendToTerminal(termInput.value, "^C\n");
    termInput.value = "";
  } else if (e.key === "l" && e.ctrlKey) {
    e.preventDefault();
    termHistory.innerHTML = "";
    termBody.scrollTop = 0;
  }
});

// Theme Management
function setTheme(name) {
  if (THEMES.includes(name)) {
    document.body.setAttribute("data-theme", name);
    localStorage.setItem("term_theme", name);
    themeBtn.textContent = `Theme: ${name}`;
  }
}

function cycleTheme() {
  currentThemeIdx = (currentThemeIdx + 1) % THEMES.length;
  setTheme(THEMES[currentThemeIdx]);
}

themeBtn.onclick = () => cycleTheme();

// CRT scanline toggle
crtBtn.onclick = () => {
  const wrapper = document.getElementById("terminalWrapper");
  const isCrt = wrapper.classList.toggle("crt");
  crtBtn.textContent = `CRT: ${isCrt ? "On" : "Off"}`;
  localStorage.setItem("term_crt", isCrt ? "1" : "0");
};

// Initial boot
window.onload = async () => {
  const savedTheme = localStorage.getItem("term_theme") || "teal";
  setTheme(savedTheme);
  currentThemeIdx = THEMES.indexOf(savedTheme);

  if (localStorage.getItem("term_crt") === "1") {
    document.getElementById("terminalWrapper").classList.add("crt");
    crtBtn.textContent = "CRT: On";
  }

  // Print startup welcome banner and KPIs
  try {
    const res = await fetch("/api/exec", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cmd: "banner" })
    });
    const bannerData = await res.json();
    
    const kpiRes = await fetch("/api/exec", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cmd: "kpis" })
    });
    const kpiData = await kpiRes.json();

    const initialBlock = document.createElement("div");
    initialBlock.className = "term-output";
    initialBlock.innerHTML = `<pre>${ansiToHtml(bannerData.output || "")}${ansiToHtml(kpiData.output || "")}</pre>`;
    termHistory.appendChild(initialBlock);
  } catch (e) {
    // Fallback if offline
  }

  focusInput();
};
</script>
</body>
</html>
"""


class WebTerminalHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, shell: TerminalShell, **kwargs):
        self.shell = shell
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html", "/terminal"):
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(TERMINAL_PAGE_HTML.encode("utf-8"))
            return

        if path == "/api/kpis":
            kpis = self.shell.service.get_kpis()
            self._send_json({k: str(v) if isinstance(v, Decimal) else v for k, v in kpis.items()})
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Path not found.")

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/exec":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
            try:
                data = json.loads(body)
                cmd = data.get("cmd", "")
                output = self.shell.execute(cmd)
                self._send_json({"output": output, "status": "ok"})
            except Exception as exc:
                self._send_json({"error": str(exc), "status": "error"}, status=HTTPStatus.BAD_REQUEST)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "API route not found.")

    def _send_json(self, data: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        raw = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def run_terminal_server(
    host: Optional[str] = None,
    port: Optional[int] = None,
    db_path: Optional[str] = None,
) -> None:
    host = host or os.environ.get("HOST", "127.0.0.1")
    if port is None:
        port = int(os.environ.get("PORT", 8080))

    service = SchoolFeeService(db_path=db_path)
    shell = TerminalShell(service=service)

    def factory(*args, **kwargs):
        return WebTerminalHandler(*args, shell=shell, **kwargs)

    server = ThreadingHTTPServer((host, port), factory)
    print(f"\n💻 Delhi Public Academy Web Terminal Console running at:")
    print(f"   👉 http://{host}:{port}/")
    print(f"   (Press Ctrl+C to stop the terminal server)\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down web terminal server gracefully...")
        server.server_close()


if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8080
    run_terminal_server(port=port_arg)
