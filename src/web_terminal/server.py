"""
Web Terminal Server for Delhi Public Academy.
Serves the in-browser bash & Python developer sandbox.
Can run standalone or be mounted into the primary application server.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from typing import Optional, Any, Dict

from web_terminal.shell import RealTerminalEngine, TerminalShell


TERMINAL_PAGE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="theme-color" content="#0b0f17">
<title>Student Terminal Sandbox — Delhi Public Academy</title>
<style>
  :root {
    --bg-window: #0b0f17;
    --bg-term: #0f172a;
    --bg-header: #1e293b;
    --bg-sidebar: #131b2e;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --accent: #2dd4bf;
    --accent-glow: rgba(45, 212, 191, 0.25);
    --prompt-user: #38bdf8;
    --prompt-host: #2dd4bf;
    --prompt-path: #facc15;
    --border-color: #283548;
    --font-term: "Adwaita Mono", "Cascadia Code", "Fira Code", SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    --font-size: 14px;
  }

  /* Themes */
  body[data-theme="matrix"] {
    --bg-window: #000000;
    --bg-term: #050b05;
    --bg-header: #0a1f0a;
    --bg-sidebar: #081408;
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
    --bg-sidebar: #1a0f04;
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
    --bg-sidebar: #1a0433;
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
    --bg-sidebar: #2b303c;
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

  /* CRT Scanline Effect Overlay */
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

  /* Split Layout: Terminal + Student Practice Lab Sidebar */
  .app-container {
    display: flex;
    height: 100%;
    width: 100%;
  }

  .terminal-wrapper {
    display: flex;
    flex-direction: column;
    flex: 1;
    height: 100%;
    min-width: 0;
    position: relative;
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
    gap: 0.4rem;
  }
  .action-btn {
    background: transparent;
    border: 1px solid var(--border-color);
    color: var(--text-muted);
    font-family: inherit;
    font-size: 0.72rem;
    padding: 4px 8px;
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
    margin-bottom: 0.6rem;
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
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: var(--text-main);
    font-family: inherit;
    font-size: 16px; /* Avoid mobile browser auto-zoom */
    caret-color: var(--accent);
    padding: 0;
    min-width: 0;
  }
  .submit-btn {
    background: var(--accent);
    color: #0b0f17;
    border: none;
    border-radius: 4px;
    font-size: 0.95rem;
    font-weight: 900;
    padding: 2px 10px;
    cursor: pointer;
    flex-shrink: 0;
    margin-left: 6px;
    height: 28px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
  .submit-btn:active {
    opacity: 0.8;
    transform: scale(0.95);
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
  .touch-pill.touch-primary {
    background: var(--accent);
    color: #0b0f17;
    border-color: var(--accent);
  }
  .touch-pill:active {
    background: var(--accent);
    color: #000;
  }

  /* Student Practice Lab Sidebar */
  .lab-sidebar {
    width: 340px;
    background: var(--bg-sidebar);
    border-left: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    transition: transform 0.25s ease;
  }
  @media (max-width: 860px) {
    .lab-sidebar {
      position: fixed;
      top: 0; bottom: 0; right: 0;
      z-index: 60;
      transform: translateX(100%);
      box-shadow: -5px 0 25px rgba(0, 0, 0, 0.5);
    }
    .lab-sidebar.open {
      transform: translateX(0);
    }
  }

  .lab-header {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--bg-header);
  }
  .lab-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--accent);
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }
  .lab-body {
    padding: 1rem;
    overflow-y: auto;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
  }

  .mission-card {
    background: var(--bg-term);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 0.75rem;
  }
  .mission-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--text-muted);
    margin-bottom: 0.35rem;
  }
  .mission-desc {
    font-size: 0.77rem;
    color: var(--text-main);
    margin-bottom: 0.5rem;
    line-height: 1.35;
  }
  .mission-cmd {
    background: #090d16;
    border: 1px solid var(--border-color);
    padding: 0.35rem 0.5rem;
    border-radius: 5px;
    font-size: 0.75rem;
    color: #38bdf8;
    word-break: break-all;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
  }
  .btn-run {
    background: var(--accent);
    color: #0b0f17;
    border: none;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 7px;
    cursor: pointer;
    flex-shrink: 0;
  }
  .btn-run:hover { opacity: 0.9; }
</style>
</head>
<body data-theme="teal">

<div class="app-container">
  <!-- Terminal Console -->
  <div class="terminal-wrapper" id="terminalWrapper">
    <!-- Window Header -->
    <header class="term-header">
      <div class="window-controls">
        <span class="dot dot-red"></span>
        <span class="dot dot-yellow"></span>
        <span class="dot dot-green"></span>
      </div>
      <div class="term-title">
        <span id="titleText">student@dpa-box: ~/school-fee-system — bash</span>
        <span class="badge-live">● Sandbox Live</span>
      </div>
      <div class="header-actions">
        <button class="action-btn" id="themeBtn" title="Switch Theme">Palette ▾</button>
        <button class="action-btn" id="crtBtn" title="Toggle CRT Scanlines">CRT: Off</button>
        <button class="action-btn" id="labToggleBtn" onclick="toggleLab()">Missions 📖</button>
        <a href="/" class="action-btn" style="text-decoration: none;" title="Open GUI Dashboard">GUI ↗</a>
      </div>
    </header>

    <!-- Output Log Container -->
    <main class="term-body" id="termBody" onclick="focusInput()">
      <div id="termHistory"></div>
      
      <!-- Command Input Form (handles Enter reliably across mobile virtual keyboards) -->
      <form id="termForm" class="prompt-row" onsubmit="handleFormSubmit(event)">
        <span class="prompt-label" id="currentPromptLabel">
          <span class="prompt-user" id="promptUser">student</span><span class="prompt-at" id="promptAt">@</span><span class="prompt-host" id="promptHost">dpa-box</span><span class="prompt-colon" id="promptColon">:</span><span class="prompt-path" id="promptPath">~/school-fee-system</span><span class="prompt-symbol" id="promptSymbol">$</span>
        </span>
        <div class="input-wrapper">
          <input type="text" id="termInput" class="term-input" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" autofocus />
          <button type="submit" class="submit-btn" id="submitBtn" title="Send (Enter)">↵</button>
        </div>
      </form>
    </main>

    <!-- Mobile Quick Touch Pill Bar -->
    <nav class="touch-bar">
      <button class="touch-pill touch-primary" onclick="submitCurrentInput()">↵ Enter</button>
      <button class="touch-pill touch-primary" onclick="runDirectCmd('python main.py')">▶ python main.py</button>
      <button class="touch-pill" onclick="runDirectCmd('python')">python (REPL)</button>
      <button class="touch-pill" onclick="handleTouchAction('TAB')">⇥ TAB</button>
      <button class="touch-pill" onclick="handleTouchAction('UP')">↑</button>
      <button class="touch-pill" onclick="handleTouchAction('DOWN')">↓</button>
      <button class="touch-pill" onclick="runDirectCmd('1')">1 (Scholars)</button>
      <button class="touch-pill" onclick="runDirectCmd('2')">2 (Invoices)</button>
      <button class="touch-pill" onclick="runDirectCmd('4')">4 (Defaulters)</button>
      <button class="touch-pill" onclick="runDirectCmd('0')">0 (Exit)</button>
      <button class="touch-pill" onclick="runDirectCmd('ls -la')">ls -la</button>
      <button class="touch-pill" onclick="runDirectCmd('python -m unittest discover tests')">run tests</button>
      <button class="touch-pill" onclick="runDirectCmd('clear')">clear</button>
    </nav>
  </div>

  <!-- Student Practice Lab Missions Sidebar -->
  <aside class="lab-sidebar" id="labSidebar">
    <div class="lab-header">
      <span class="lab-title">🎓 Student Missions Lab</span>
      <button class="action-btn" onclick="toggleLab(false)">✕ Close</button>
    </div>
    <div class="lab-body">
      <div class="mission-card">
        <div class="mission-header"><span>Mission 1</span> <span>Interactive Project</span></div>
        <div class="mission-desc">Run the student fee system interactive console with menus and payments!</div>
        <div class="mission-cmd">
          <code>python main.py</code>
          <button class="btn-run" onclick="runDirectCmd('python main.py')">▶ Run</button>
        </div>
      </div>

      <div class="mission-card">
        <div class="mission-header"><span>Mission 2</span> <span>Interactive Python REPL</span></div>
        <div class="mission-desc">Start a live Python prompt (>>>) to tinker with variables and code.</div>
        <div class="mission-cmd">
          <code>python</code>
          <button class="btn-run" onclick="runDirectCmd('python')">▶ Run</button>
        </div>
      </div>

      <div class="mission-card">
        <div class="mission-header"><span>Mission 3</span> <span>Explore Files</span></div>
        <div class="mission-desc">Check out the project directory structure and files.</div>
        <div class="mission-cmd">
          <code>ls -la</code>
          <button class="btn-run" onclick="runDirectCmd('ls -la')">▶ Run</button>
        </div>
      </div>

      <div class="mission-card">
        <div class="mission-header"><span>Mission 4</span> <span>Scholars Register</span></div>
        <div class="mission-desc">List all 43 enrolled students in Delhi Public Academy.</div>
        <div class="mission-cmd">
          <code>python -m school_fee_system students list</code>
          <button class="btn-run" onclick="runDirectCmd('python -m school_fee_system students list')">▶ Run</button>
        </div>
      </div>

      <div class="mission-card">
        <div class="mission-header"><span>Mission 5</span> <span>Fee Invoices</span></div>
        <div class="mission-desc">Inspect generated student billing and fee invoices.</div>
        <div class="mission-cmd">
          <code>python -m school_fee_system invoices list</code>
          <button class="btn-run" onclick="runDirectCmd('python -m school_fee_system invoices list')">▶ Run</button>
        </div>
      </div>

      <div class="mission-card">
        <div class="mission-header"><span>Mission 6</span> <span>Defaulters</span></div>
        <div class="mission-desc">Find accounts overdue past their 21-day grace period.</div>
        <div class="mission-cmd">
          <code>python -m school_fee_system defaulters</code>
          <button class="btn-run" onclick="runDirectCmd('python -m school_fee_system defaulters')">▶ Run</button>
        </div>
      </div>

      <div class="mission-card">
        <div class="mission-header"><span>Mission 7</span> <span>Record Payment</span></div>
        <div class="mission-desc">Collect ₹5,000 for Invoice #1 via UPI and issue receipt.</div>
        <div class="mission-cmd">
          <code>python -m school_fee_system payments record --invoice-id 1 --amount 5000 --method UPI</code>
          <button class="btn-run" onclick="runDirectCmd('python -m school_fee_system payments record --invoice-id 1 --amount 5000 --method UPI')">▶ Run</button>
        </div>
      </div>

      <div class="mission-card">
        <div class="mission-header"><span>Mission 8</span> <span>Audit Receipt</span></div>
        <div class="mission-desc">Verify cryptographic SHA-256 digital security seal.</div>
        <div class="mission-cmd">
          <code>python -m school_fee_system receipts verify REC-2026-0001</code>
          <button class="btn-run" onclick="runDirectCmd('python -m school_fee_system receipts verify REC-2026-0001')">▶ Run</button>
        </div>
      </div>

      <div class="mission-card">
        <div class="mission-header"><span>Mission 9</span> <span>Automated Tests</span></div>
        <div class="mission-desc">Execute all 20 automated unit tests with unittest.</div>
        <div class="mission-cmd">
          <code>python -m unittest discover tests</code>
          <button class="btn-run" onclick="runDirectCmd('python -m unittest discover tests')">▶ Run</button>
        </div>
      </div>
    </div>
  </aside>
</div>

<script>
const AUTO_COMMANDS = [
  "python main.py", "python", "ls -la", "pwd", "cat README.md", "cd src", "cd ..", "cd ~",
  "python -m school_fee_system students list",
  "python -m school_fee_system invoices list",
  "python -m school_fee_system defaulters",
  "python -m school_fee_system reports collection",
  "python -m school_fee_system payments record --invoice-id 1 --amount 5000 --method UPI",
  "python -m school_fee_system receipts verify REC-2026-0001",
  "python -m unittest discover tests",
  "reset-db", "clear", "help"
];

const THEMES = ["teal", "matrix", "amber", "nord", "cyberpunk"];
let currentThemeIdx = 0;

let history = JSON.parse(localStorage.getItem("real_term_history") || "[]");
let historyIndex = history.length;

// Persistent session id per browser tab
let sessionId = localStorage.getItem("dpa_term_session_id");
if (!sessionId) {
  sessionId = "sess_" + Math.random().toString(36).substring(2, 10);
  localStorage.setItem("dpa_term_session_id", sessionId);
}

let currentPrompt = {
  user: "student",
  host: "dpa-box",
  path: "~/school-fee-system",
  symbol: "$"
};

const termBody = document.getElementById("termBody");
const termHistory = document.getElementById("termHistory");
const termInput = document.getElementById("termInput");
const themeBtn = document.getElementById("themeBtn");
const crtBtn = document.getElementById("crtBtn");
const promptUser = document.getElementById("promptUser");
const promptHost = document.getElementById("promptHost");
const promptPath = document.getElementById("promptPath");
const promptSymbol = document.getElementById("promptSymbol");
const promptColon = document.getElementById("promptColon");
const promptAt = document.getElementById("promptAt");
const titleText = document.getElementById("titleText");
const labSidebar = document.getElementById("labSidebar");

function focusInput() {
  termInput.focus();
}

function toggleLab(state) {
  if (state !== undefined) {
    labSidebar.classList.toggle("open", state);
  } else {
    labSidebar.classList.toggle("open");
  }
}

// Convert ANSI escape sequences to styled HTML
function ansiToHtml(text) {
  let out = "";
  let openSpans = 0;
  
  let escaped = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  const regex = /\x1B\[([0-9;]+)m/g;
  let lastIdx = 0;
  let match;

  while ((match = regex.exec(escaped)) !== null) {
    out += escaped.substring(lastIdx, match.index);
    lastIdx = regex.lastIndex;
    
    const codes = match[1].split(";");
    if (codes[0] === "0" || codes[0] === "") {
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
      out += '<span style="color: #ef4444; font-weight: 600;">';
      openSpans++;
    } else if (codes[0] === "32") {
      out += '<span style="color: #22c55e; font-weight: 600;">';
      openSpans++;
    } else if (codes[0] === "33") {
      out += '<span style="color: #facc15; font-weight: 600;">';
      openSpans++;
    } else if (codes[0] === "34") {
      out += '<span style="color: #38bdf8;">';
      openSpans++;
    } else if (codes[0] === "35") {
      out += '<span style="color: #c084fc;">';
      openSpans++;
    } else if (codes[0] === "36") {
      out += '<span style="color: #2dd4bf;">';
      openSpans++;
    } else if (codes[0] === "37") {
      out += '<span style="color: #f8fafc;">';
      openSpans++;
    } else if (codes[0] === "38" && codes[1] === "2") {
      const r = codes[2], g = codes[3], b = codes[4];
      out += `<span style="color: rgb(${r}, ${g}, ${b});">`;
      openSpans++;
    } else if (codes[0] === "48" && codes[1] === "2") {
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

function escapeHtml(text) {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function updatePromptUI(p) {
  if (!p) return;
  currentPrompt = p;
  promptUser.textContent = p.user || "student";
  promptHost.textContent = p.host || "dpa-box";
  promptPath.textContent = p.path || "~/school-fee-system";
  promptSymbol.textContent = p.symbol || "$";

  if (p.user === "python" || p.user === "dpa") {
    promptColon.style.display = "none";
    promptAt.style.display = "none";
  } else {
    promptColon.style.display = "inline";
    promptAt.style.display = "inline";
  }

  titleText.textContent = `${p.user}@${p.host}: ${p.path} — console`;
}

function appendToTerminal(cmd, output, promptObj) {
  if (output === "\033[2J\033[H") {
    termHistory.innerHTML = "";
    termBody.scrollTop = 0;
    return;
  }

  const block = document.createElement("div");
  block.className = "term-output";

  const p = promptObj || currentPrompt;
  const isSpecial = (p.user === "python" || p.user === "dpa");
  const middle = isSpecial ? "" : `@${p.host}:`;

  let promptHtml = `
    <div class="prompt-row" style="margin-bottom: 2px;">
      <span class="prompt-label">
        <span class="prompt-user">${p.user}</span>${middle}<span class="prompt-path">${p.path}</span><span class="prompt-symbol">${p.symbol}</span>
      </span>
      <span style="font-weight: 600; color: #ffffff; margin-left: 0.35rem;">${escapeHtml(cmd)}</span>
    </div>
  `;

  block.innerHTML = promptHtml + `<pre>${ansiToHtml(output)}</pre>`;
  termHistory.appendChild(block);
  termBody.scrollTop = termBody.scrollHeight;
}

async function executeCommand(cmdStr) {
  const trimmed = cmdStr.trim();
  if (!trimmed) return;

  const previousPrompt = Object.assign({}, currentPrompt);

  if (history[history.length - 1] !== trimmed) {
    history.push(trimmed);
    if (history.length > 100) history.shift();
    localStorage.setItem("real_term_history", JSON.stringify(history));
  }
  historyIndex = history.length;

  termInput.value = "";

  try {
    const res = await fetch("/api/exec", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cmd: trimmed, session_id: sessionId })
    });
    const data = await res.json();
    
    if (data.prompt) {
      updatePromptUI(data.prompt);
    }

    appendToTerminal(trimmed, data.output || "", previousPrompt);
  } catch (err) {
    appendToTerminal(trimmed, `\033[31mSandbox Error: ${err.message}\033[0m\n`, previousPrompt);
  }

  termBody.scrollTop = termBody.scrollHeight;
  focusInput();
}

function handleFormSubmit(e) {
  if (e) e.preventDefault();
  submitCurrentInput();
}

function submitCurrentInput() {
  const val = termInput.value;
  if (val.trim()) {
    executeCommand(val);
  }
}

function runDirectCmd(cmd) {
  termInput.value = cmd;
  executeCommand(cmd);
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
    const suggestionText = "\n\033[38;2;148;163;184mSuggestions:\033[0m\n  " + matches.join("   ") + "\n";
    appendToTerminal(current, suggestionText, currentPrompt);
  }
}

termInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    submitCurrentInput();
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
    appendToTerminal(termInput.value, "^C\n", currentPrompt);
    termInput.value = "";
  } else if (e.key === "l" && e.ctrlKey) {
    e.preventDefault();
    termHistory.innerHTML = "";
    termBody.scrollTop = 0;
  }
});

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

crtBtn.onclick = () => {
  const wrapper = document.getElementById("terminalWrapper");
  const isCrt = wrapper.classList.toggle("crt");
  crtBtn.textContent = `CRT: ${isCrt ? "On" : "Off"}`;
  localStorage.setItem("term_crt", isCrt ? "1" : "0");
};

window.onload = async () => {
  const savedTheme = localStorage.getItem("term_theme") || "teal";
  setTheme(savedTheme);
  currentThemeIdx = THEMES.indexOf(savedTheme);

  if (localStorage.getItem("term_crt") === "1") {
    document.getElementById("terminalWrapper").classList.add("crt");
    crtBtn.textContent = "CRT: On";
  }

  try {
    const res = await fetch("/api/exec", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cmd: "banner", session_id: sessionId })
    });
    const data = await res.json();
    if (data.prompt) {
      updatePromptUI(data.prompt);
    }
    const initialBlock = document.createElement("div");
    initialBlock.className = "term-output";
    initialBlock.innerHTML = `<pre>${ansiToHtml(data.output || "")}</pre>`;
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
    _sessions: Dict[str, RealTerminalEngine] = {}

    def __init__(self, *args, project_root: Optional[str] = None, **kwargs):
        self.project_root = project_root
        super().__init__(*args, **kwargs)

    def _get_engine(self, session_id: str) -> RealTerminalEngine:
        if session_id not in WebTerminalHandler._sessions:
            WebTerminalHandler._sessions[session_id] = RealTerminalEngine(project_root=self.project_root)
        return WebTerminalHandler._sessions[session_id]

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html", "/terminal", "/terminal/"):
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(TERMINAL_PAGE_HTML.encode("utf-8"))
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
                session_id = data.get("session_id", "default")
                engine = self._get_engine(session_id)
                result = engine.execute(cmd)
                self._send_json(result)
            except Exception as exc:
                self._send_json({"error": str(exc), "exit_code": 1}, status=HTTPStatus.BAD_REQUEST)
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
    project_root: Optional[str] = None,
) -> None:
    host = host or os.environ.get("HOST", "127.0.0.1")
    if port is None:
        port = int(os.environ.get("PORT", 8080))

    def factory(*args, **kwargs):
        return WebTerminalHandler(*args, project_root=project_root, **kwargs)

    server = ThreadingHTTPServer((host, port), factory)
    print(f"\n💻 Delhi Public Academy Real Terminal Sandbox running at:")
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
