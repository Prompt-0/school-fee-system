"""
Zero-dependency Web Dashboard & REST API Server for the School Fee System.
Provides a modern, responsive single-page administration interface along with JSON REST APIs.
"""

from __future__ import annotations

import json
import urllib.parse
from datetime import date
from decimal import Decimal
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional

from school_fee_system.database import initialize_schema, seed_sample_data
from school_fee_system.models import FeeTerm, InvoiceStatus, PaymentMethod, Student, StudentStatus
from school_fee_system.receipt_generator import ReceiptFormatter
from school_fee_system.services import SchoolFeeService


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#0d9488" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0b0f17" media="(prefers-color-scheme: dark)">
<meta name="description" content="Delhi Public Academy — Official CBSE School Student Fee Management & Accounts Terminal">
<title>Delhi Public Academy — School Fee Management System</title>
<style>
  :root {
    color-scheme: light dark;
    --primary: #0d9488;
    --primary-hover: #0f766e;
    --primary-surface: #f0fdfa;
    --primary-border: #99f6e4;
    --primary-text: #0f766e;
    
    --bg-page: #f8fafc;
    --bg-card: #ffffff;
    --bg-subtle: #f1f5f9;
    --bg-input: #ffffff;
    --text-primary: #0f172a;
    --text-muted: #64748b;
    --border-color: #e2e8f0;
    
    --success: #16a34a;
    --success-bg: #dcfce7;
    --warning: #ca8a04;
    --warning-bg: #fef3c7;
    --danger: #dc2626;
    --danger-bg: #fee2e2;
    --info: #0284c7;
    --info-bg: #e0f2fe;

    --sidebar-width: 260px;
    --bottom-nav-height: 64px;
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
    --shadow-lg: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
  }

  @media (prefers-color-scheme: dark) {
    :root {
      --primary: #2dd4bf;
      --primary-hover: #14b8a6;
      --primary-surface: rgba(45, 212, 191, 0.12);
      --primary-border: rgba(45, 212, 191, 0.3);
      --primary-text: #2dd4bf;
      
      --bg-page: #0b0f17;
      --bg-card: #161e2e;
      --bg-subtle: #1f293d;
      --bg-input: #111827;
      --text-primary: #f8fafc;
      --text-muted: #94a3b8;
      --border-color: #283548;
      
      --success: #4ade80;
      --success-bg: rgba(74, 222, 128, 0.15);
      --warning: #facc15;
      --warning-bg: rgba(250, 204, 21, 0.15);
      --danger: #f87171;
      --danger-bg: rgba(248, 113, 113, 0.15);
      --info: #38bdf8;
      --info-bg: rgba(56, 189, 248, 0.15);
    }
  }

  * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
  
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Adwaita Sans", "Helvetica Neue", Arial, sans-serif;
    background-color: var(--bg-page);
    color: var(--text-primary);
    line-height: 1.5;
    font-size: 15px;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    overflow-x: hidden;
  }

  .skip-link {
    position: absolute;
    top: -40px;
    left: 10px;
    background: var(--primary);
    color: #000;
    padding: 8px 12px;
    border-radius: var(--radius-sm);
    z-index: 1000;
    transition: top 0.2s;
  }
  .skip-link:focus { top: 10px; }

  /* App Shell Layout */
  .layout {
    display: flex;
    min-height: 100vh;
    width: 100%;
    position: relative;
  }

  /* Desktop Sidebar */
  .sidebar {
    width: var(--sidebar-width);
    background: #0f172a;
    color: #f8fafc;
    display: flex;
    flex-direction: column;
    padding: 1.5rem 1rem;
    flex-shrink: 0;
    transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 40;
  }

  .brand {
    font-size: 1.15rem;
    font-weight: 800;
    color: #2dd4bf;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    letter-spacing: -0.2px;
  }
  .brand-sub {
    font-size: 0.72rem;
    color: #94a3b8;
    margin-top: 2px;
    margin-bottom: 1.75rem;
  }

  .nav-menu {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    flex: 1;
  }
  
  .nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    border-radius: var(--radius-md);
    color: #94a3b8;
    text-decoration: none;
    font-weight: 500;
    font-size: 0.925rem;
    cursor: pointer;
    transition: all 0.15s ease;
    min-height: 44px;
    border: none;
    background: transparent;
    width: 100%;
    text-align: left;
  }
  .nav-item:hover {
    background: #1e293b;
    color: #38bdf8;
  }
  .nav-item.active {
    background: #0d9488;
    color: #ffffff;
    font-weight: 600;
  }

  .sidebar-backdrop {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.55);
    backdrop-filter: blur(2px);
    z-index: 35;
  }

  /* Main Viewport */
  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
    width: 100%;
    padding-bottom: calc(var(--bottom-nav-height) + 1.5rem);
  }

  @media (min-width: 1024px) {
    .main-content {
      padding-bottom: 2rem;
    }
  }

  /* Header Topbar */
  .topbar {
    background: var(--bg-card);
    border-bottom: 1px solid var(--border-color);
    padding: 0.85rem 1.25rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 20;
    gap: 0.75rem;
  }
  @media (min-width: 768px) {
    .topbar { padding: 1rem 2rem; }
  }

  .topbar-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    min-width: 0;
  }
  
  .hamburger-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: var(--radius-md);
    background: var(--bg-subtle);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    font-size: 1.25rem;
    cursor: pointer;
    flex-shrink: 0;
  }
  @media (min-width: 1024px) {
    .hamburger-btn { display: none; }
  }

  .page-title {
    font-size: 1.15rem;
    font-weight: 700;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  @media (min-width: 768px) {
    .page-title { font-size: 1.35rem; }
  }

  .content-area {
    padding: 1rem;
    flex: 1;
    max-width: 1300px;
    width: 100%;
    margin: 0 auto;
  }
  @media (min-width: 768px) {
    .content-area { padding: 1.75rem 2rem; }
  }

  /* KPI Grid */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.85rem;
    margin-bottom: 1.5rem;
  }
  @media (min-width: 768px) {
    .kpi-grid {
      grid-template-columns: repeat(4, 1fr);
      gap: 1.25rem;
      margin-bottom: 2rem;
    }
  }

  .kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 1.1rem;
    box-shadow: var(--shadow-sm);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .kpi-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }
  .kpi-value {
    font-size: 1.4rem;
    font-weight: 800;
    margin-top: 0.4rem;
    letter-spacing: -0.3px;
  }
  @media (min-width: 768px) {
    .kpi-value { font-size: 1.75rem; }
  }

  /* Cards */
  .card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 1.25rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-sm);
  }
  @media (min-width: 768px) {
    .card { padding: 1.5rem; margin-bottom: 2rem; }
  }

  .card-header {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.25rem;
  }
  .card-title {
    font-size: 1.05rem;
    font-weight: 700;
  }
  @media (min-width: 768px) {
    .card-title { font-size: 1.2rem; }
  }

  /* Filter Toolbar */
  .filter-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }
  .search-input {
    flex: 1;
    min-width: 200px;
    padding: 0.65rem 0.85rem;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-color);
    background: var(--bg-input);
    color: var(--text-primary);
    font-size: 16px; /* Prevents auto-zoom on mobile browsers */
  }

  /* Responsive Table Container (Key Mobile Fix) */
  .table-responsive {
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    background: var(--bg-card);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    min-width: 600px; /* Ensures columns never get squished into illegibility */
  }
  th {
    background: var(--bg-subtle);
    padding: 0.85rem 1rem;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--text-muted);
    border-bottom: 1px solid var(--border-color);
    white-space: nowrap;
    letter-spacing: 0.4px;
  }
  td {
    padding: 0.85rem 1rem;
    border-bottom: 1px solid var(--border-color);
    font-size: 0.9rem;
    vertical-align: middle;
    white-space: nowrap;
  }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background-color: var(--bg-subtle); }

  /* Badges */
  .status-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.65rem;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }
  .badge-paid { background: var(--success-bg); color: var(--success); }
  .badge-unpaid { background: var(--warning-bg); color: var(--warning); }
  .badge-partial { background: var(--info-bg); color: var(--info); }
  .badge-overdue { background: var(--danger-bg); color: var(--danger); }

  /* Buttons (WCAG 2.2 touch compliant: min 44px) */
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    padding: 0.65rem 1.1rem;
    border-radius: var(--radius-md);
    font-weight: 600;
    font-size: 0.9rem;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.15s ease;
    text-decoration: none;
    min-height: 44px;
    white-space: nowrap;
  }
  .btn:active { transform: scale(0.98); }
  
  .btn-primary {
    background: var(--primary);
    color: #ffffff;
    border-color: var(--primary);
  }
  @media (prefers-color-scheme: dark) {
    .btn-primary { color: #0f172a; font-weight: 700; }
  }
  .btn-primary:hover { background: var(--primary-hover); }

  .btn-outline {
    background: transparent;
    border-color: var(--border-color);
    color: var(--text-primary);
  }
  .btn-outline:hover { background: var(--bg-subtle); }

  .btn-sm {
    min-height: 38px;
    padding: 0.4rem 0.85rem;
    font-size: 0.825rem;
  }

  /* Modals (Desktop modal + Mobile Bottom Sheet) */
  .modal-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.65);
    backdrop-filter: blur(4px);
    z-index: 100;
    justify-content: center;
    align-items: center;
    padding: 1rem;
  }
  .modal {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    width: 100%;
    max-width: 540px;
    padding: 1.5rem;
    box-shadow: var(--shadow-lg);
    max-height: 90vh;
    overflow-y: auto;
  }
  @media (max-width: 640px) {
    .modal-overlay {
      padding: 0;
      align-items: flex-end;
    }
    .modal {
      max-width: 100%;
      border-radius: 20px 20px 0 0;
      max-height: 85vh;
      padding: 1.5rem 1.25rem;
      border-bottom: none;
    }
    .modal-drag-handle {
      width: 40px;
      height: 4px;
      background: var(--border-color);
      border-radius: 999px;
      margin: -0.5rem auto 1rem auto;
    }
  }

  .form-group { margin-bottom: 1.1rem; }
  .form-label {
    display: block;
    font-size: 0.85rem;
    font-weight: 700;
    margin-bottom: 0.4rem;
    color: var(--text-primary);
  }
  .form-control {
    width: 100%;
    padding: 0.75rem 0.9rem;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    background: var(--bg-input);
    color: var(--text-primary);
    font-size: 16px; /* Crucial: 16px avoids auto-zoom on mobile */
    min-height: 44px;
  }
  .form-control:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px var(--primary-surface);
  }

  .grid-2 {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  @media (min-width: 500px) {
    .grid-2 { grid-template-columns: 1fr 1fr; }
  }

  /* Bottom Mobile Nav Bar (Modern Mobile Web Standard) */
  .mobile-bottom-nav {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: var(--bottom-nav-height);
    background: var(--bg-card);
    border-top: 1px solid var(--border-color);
    z-index: 30;
    padding-bottom: env(safe-area-inset-bottom);
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  }
  @media (min-width: 1024px) {
    .mobile-bottom-nav { display: none; }
  }

  .b-nav-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: none;
    background: transparent;
    color: var(--text-muted);
    font-size: 0.7rem;
    font-weight: 600;
    gap: 2px;
    cursor: pointer;
    min-height: 44px;
    padding: 4px 0;
  }
  .b-nav-item span { font-size: 1.25rem; }
  .b-nav-item.active {
    color: var(--primary);
  }

  /* Toast Notification */
  .toast-container {
    position: fixed;
    bottom: calc(var(--bottom-nav-height) + 1rem);
    left: 50%;
    transform: translateX(-50%);
    z-index: 200;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    width: 90%;
    max-width: 420px;
    pointer-events: none;
  }
  @media (min-width: 1024px) {
    .toast-container {
      bottom: 1.5rem;
      right: 1.5rem;
      left: auto;
      transform: none;
    }
  }
  .toast {
    background: #0f172a;
    color: #ffffff;
    padding: 0.85rem 1.15rem;
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-lg);
    font-size: 0.9rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    pointer-events: auto;
    animation: toastIn 0.25s ease-out;
  }
  @keyframes toastIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .tab-pane { display: none; }
  .tab-pane.active { display: block; animation: fadeIn 0.15s ease-in; }
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  /* Mobile off-canvas drawer open state */
  @media (max-width: 1023px) {
    .sidebar {
      position: fixed;
      top: 0;
      bottom: 0;
      left: 0;
      transform: translateX(-100%);
      box-shadow: var(--shadow-lg);
    }
    .sidebar.open {
      transform: translateX(0);
    }
    .sidebar-backdrop.open {
      display: block;
    }
  }
</style>
</head>
<body>
<a href="#main-content" class="skip-link">Skip to main content</a>

<div class="layout">
  <!-- Mobile Backdrop Overlay -->
  <div class="sidebar-backdrop" id="sidebar-backdrop" onclick="toggleSidebar(false)"></div>

  <!-- Accessible Navigation Sidebar / Off-Canvas Drawer -->
  <aside class="sidebar" id="app-sidebar" aria-label="Main Application Sidebar">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
      <div>
        <div class="brand">🎓 Delhi Public Academy</div>
        <div class="brand-sub">CBSE Affiliation No: 1930245</div>
      </div>
      <button class="hamburger-btn" style="background: transparent; border: none; color: #fff; width: 36px; height: 36px;" onclick="toggleSidebar(false)" aria-label="Close navigation drawer">✕</button>
    </div>

    <nav aria-label="School Fee Navigation" style="flex: 1;">
      <ul class="nav-menu">
        <li><button class="nav-item active" onclick="switchTab('dashboard')"><span>📊</span> Accounts Dashboard</button></li>
        <li><button class="nav-item" onclick="switchTab('students')"><span>🧑‍🎓</span> Scholar Register</button></li>
        <li><button class="nav-item" onclick="switchTab('invoices')"><span>🧾</span> Fee Invoices & Dues</button></li>
        <li><a href="/terminal" class="nav-item" style="text-decoration: none; color: inherit;"><span>💻</span> Interactive Web Terminal</a></li>
        <li><button class="nav-item" onclick="switchTab('terminal')"><span>💳</span> Fee Collection Desk</button></li>
        <li><button class="nav-item" onclick="switchTab('defaulters')"><span>⚠️</span> Overdue Defaulters</button></li>
        <li><button class="nav-item" onclick="switchTab('reports')"><span>📈</span> Collection Register</button></li>
      </ul>
    </nav>
    <div style="padding-top: 1rem; border-top: 1px solid #1e293b; font-size: 0.75rem; color: #64748b;">
      Active Session: <strong>2026-2027</strong><br>
      CBSE School Code: <strong>45123</strong>
    </div>
  </aside>

  <!-- Main Viewport -->
  <div class="main-content">
    <header class="topbar">
      <div class="topbar-left">
        <button class="hamburger-btn" onclick="toggleSidebar(true)" aria-label="Open navigation drawer">☰</button>
        <div>
          <h1 class="page-title" id="page-title">Accounts Dashboard</h1>
          <div style="font-size: 0.75rem; color: var(--text-muted); display: none;" id="sub-header-desktop">Delhi Public Academy, New Delhi — Session 2026-2027</div>
        </div>
      </div>
      <div style="display: flex; gap: 0.5rem; align-items: center;">
        <a href="/terminal" class="btn btn-outline btn-sm" style="text-decoration: none;" title="Open In-Browser Web Terminal Console">💻 Terminal</a>
        <button class="btn btn-primary btn-sm" onclick="openPaymentModal()">+ Collect Fee</button>
      </div>
    </header>

    <main class="content-area" id="main-content">
      <!-- 1. DASHBOARD TAB -->
      <section id="pane-dashboard" class="tab-pane active" role="tabpanel" aria-label="Accounts Dashboard">
        <div class="kpi-grid">
          <div class="kpi-card">
            <div class="kpi-label">Active Students</div>
            <div class="kpi-value" id="kpi-students" style="color: var(--primary);">...</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Fees Collected</div>
            <div class="kpi-value" id="kpi-collected" style="color: var(--success);">...</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Pending Dues</div>
            <div class="kpi-value" id="kpi-outstanding" style="color: var(--danger);">...</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Defaulters</div>
            <div class="kpi-value" id="kpi-defaulters" style="color: var(--warning);">...</div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div>
              <div class="card-title">Recent Fee Receipts</div>
              <div style="font-size: 0.8rem; color: var(--text-muted);">Real-time UPI, NEFT, Cheque and Cash collections</div>
            </div>
            <button class="btn btn-outline btn-sm" onclick="loadDashboard()">🔄 Refresh</button>
          </div>
          <div class="table-responsive" tabindex="0">
            <table id="tbl-recent-payments">
              <thead>
                <tr>
                  <th scope="col">Receipt Ref</th>
                  <th scope="col">Invoice #</th>
                  <th scope="col">Amount (₹)</th>
                  <th scope="col">Mode</th>
                  <th scope="col">Txn / UTR Ref</th>
                  <th scope="col">Date & Time</th>
                  <th scope="col">Cashier</th>
                </tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- 2. STUDENTS TAB -->
      <section id="pane-students" class="tab-pane" role="tabpanel" aria-label="Scholar Register">
        <div class="card">
          <div class="card-header">
            <div>
              <div class="card-title">Scholar Register (Enrolled Students)</div>
              <div style="font-size: 0.8rem; color: var(--text-muted);">View student profiles, parent contacts, bus/hostel status</div>
            </div>
            <button class="btn btn-primary btn-sm" onclick="openStudentModal()">+ Enroll Student</button>
          </div>

          <div class="filter-bar">
            <input type="text" id="search-students" class="search-input" placeholder="🔍 Search by student name, admission no or parent..." oninput="filterStudentsTable()">
          </div>

          <div class="table-responsive" tabindex="0">
            <table id="tbl-students">
              <thead>
                <tr>
                  <th scope="col">Admission No</th>
                  <th scope="col">Student Name</th>
                  <th scope="col">Class & Sec</th>
                  <th scope="col">Parent Contact</th>
                  <th scope="col">Facilities</th>
                  <th scope="col">Status</th>
                  <th scope="col">Quick Action</th>
                </tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- 3. INVOICES TAB -->
      <section id="pane-invoices" class="tab-pane" role="tabpanel" aria-label="Fee Invoices">
        <div class="card">
          <div class="card-header">
            <div>
              <div class="card-title">Quarterly & Term Fee Invoices</div>
              <div style="font-size: 0.8rem; color: var(--text-muted);">Itemized bills, concessions and payment tracking</div>
            </div>
            <button class="btn btn-primary btn-sm" onclick="openBatchModal()">⚡ Batch Issue Invoices</button>
          </div>

          <div class="filter-bar">
            <input type="text" id="search-invoices" class="search-input" placeholder="🔍 Filter by invoice #, student or class..." oninput="filterInvoicesTable()">
            <select id="filter-invoice-status" class="form-control" style="width: auto; min-width: 150px;" onchange="loadInvoices()">
              <option value="">All Statuses</option>
              <option value="UNPAID">Pending (Unpaid)</option>
              <option value="PARTIALLY_PAID">Partially Paid</option>
              <option value="PAID">Fully Settled</option>
              <option value="OVERDUE">Overdue Defaulter</option>
            </select>
          </div>

          <div class="table-responsive" tabindex="0">
            <table id="tbl-invoices">
              <thead>
                <tr>
                  <th scope="col">Bill / Inv #</th>
                  <th scope="col">Student Name</th>
                  <th scope="col">Class</th>
                  <th scope="col">Term</th>
                  <th scope="col">Due Date</th>
                  <th scope="col">Payable (₹)</th>
                  <th scope="col">Paid (₹)</th>
                  <th scope="col">Balance Due (₹)</th>
                  <th scope="col">Status</th>
                  <th scope="col">Action</th>
                </tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- 4. CASHIER TERMINAL TAB -->
      <section id="pane-terminal" class="tab-pane" role="tabpanel" aria-label="Fee Collection Desk">
        <div class="card" style="max-width: 620px; margin: 0 auto;">
          <div class="card-header">
            <div>
              <div class="card-title">💳 Fee Collection Desk</div>
              <div style="font-size: 0.825rem; color: var(--text-muted);">Record collections, log UTR/cheques, and print receipts</div>
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label" for="terminal-invoice-select">Select Student / Pending Bill</label>
            <select id="terminal-invoice-select" class="form-control" onchange="terminalInvoiceChanged()"></select>
          </div>

          <div id="terminal-invoice-info" style="display: none; background: var(--bg-subtle); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 1rem; margin-bottom: 1.25rem;">
            <div style="font-size: 0.95rem;"><strong>Student:</strong> <span id="term-stu-name"></span></div>
            <div style="margin-top: 4px; font-size: 1rem;"><strong>Outstanding Balance:</strong> <span id="term-stu-bal" style="color: var(--danger); font-weight: 800;"></span></div>
          </div>

          <div class="form-group">
            <label class="form-label" for="terminal-amount">Payment Amount (₹)</label>
            <input type="number" step="1" id="terminal-amount" class="form-control" placeholder="0.00">
          </div>

          <div class="form-group">
            <label class="form-label" for="terminal-method">Payment Mode</label>
            <select id="terminal-method" class="form-control">
              <option value="UPI">UPI (Google Pay / PhonePe / Paytm / BHIM)</option>
              <option value="CASH">Cash at Fee Counter</option>
              <option value="NET_BANKING">Net Banking / NEFT / IMPS</option>
              <option value="CHEQUE_DD">Cheque / Demand Draft (DD)</option>
              <option value="CARD">POS Debit / Credit Card</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label" for="terminal-tx">Transaction Reference (UTR / Cheque No / VPA)</label>
            <input type="text" id="terminal-tx" class="form-control" placeholder="e.g. UPI Ref / UTR No or Cheque: 442101">
          </div>

          <button class="btn btn-primary" style="width: 100%; font-size: 1rem; padding: 0.85rem;" onclick="submitTerminalPayment()">Process Collection & Print Official Receipt</button>
        </div>
      </section>

      <!-- 5. DEFAULTERS TAB -->
      <section id="pane-defaulters" class="tab-pane" role="tabpanel" aria-label="Fee Defaulters">
        <div class="card">
          <div class="card-header">
            <div>
              <div class="card-title">⚠️ Fee Defaulters & Overdue Invoices</div>
              <div style="font-size: 0.8rem; color: var(--text-muted);">Accounts past due date with assessed penalty fines</div>
            </div>
            <a href="/api/export/defaulters.csv" class="btn btn-outline btn-sm">📥 Export Defaulters CSV</a>
          </div>

          <div class="table-responsive" tabindex="0">
            <table id="tbl-defaulters">
              <thead>
                <tr>
                  <th scope="col">Invoice #</th>
                  <th scope="col">Student Name</th>
                  <th scope="col">Class</th>
                  <th scope="col">Parent Contact</th>
                  <th scope="col">Due Date</th>
                  <th scope="col">Overdue Days</th>
                  <th scope="col">Balance Due (₹)</th>
                </tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- 6. ACCOUNTING TAB -->
      <section id="pane-reports" class="tab-pane" role="tabpanel" aria-label="Collection Register">
        <div class="card">
          <div class="card-header">
            <div>
              <div class="card-title">📈 Cashier Daily Collection Register</div>
              <div style="font-size: 0.8rem; color: var(--text-muted);">Reconciliation ledger by date, mode and cashier</div>
            </div>
            <a href="/api/export/collection.csv" class="btn btn-outline btn-sm">📥 Export Collection CSV</a>
          </div>

          <div class="table-responsive" tabindex="0">
            <table id="tbl-all-collections">
              <thead>
                <tr>
                  <th scope="col">Payment Ref</th>
                  <th scope="col">Invoice #</th>
                  <th scope="col">Amount (₹)</th>
                  <th scope="col">Mode</th>
                  <th scope="col">Txn / UTR No</th>
                  <th scope="col">Timestamp</th>
                  <th scope="col">Cashier</th>
                </tr>
              </thead>
              <tbody></tbody>
            </table>
          </div>
        </div>
      </section>
    </main>
  </div>
</div>

<!-- Mobile Bottom Navigation Bar (WCAG Touch Compliant) -->
<nav class="mobile-bottom-nav" aria-label="Mobile Navigation Bar">
  <button class="b-nav-item active" onclick="switchTab('dashboard')" id="bnav-dashboard" aria-label="Dashboard">
    <span>📊</span> Dashboard
  </button>
  <button class="b-nav-item" onclick="switchTab('students')" id="bnav-students" aria-label="Students">
    <span>🧑‍🎓</span> Students
  </button>
  <button class="b-nav-item" onclick="switchTab('invoices')" id="bnav-invoices" aria-label="Invoices">
    <span>🧾</span> Invoices
  </button>
  <button class="b-nav-item" onclick="switchTab('terminal')" id="bnav-terminal" aria-label="Payment Terminal">
    <span>💳</span> Collect
  </button>
  <button class="b-nav-item" onclick="toggleSidebar(true)" aria-label="More Menu">
    <span>☰</span> More
  </button>
</nav>

<!-- Enroll Student Modal -->
<div id="modal-student" class="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-student-title">
  <div class="modal">
    <div class="modal-drag-handle"></div>
    <div class="card-title" id="modal-student-title" style="margin-bottom: 1rem;">Enroll New Student (Scholar Register)</div>
    
    <div class="form-group">
      <label class="form-label" for="stu-id">Admission / S.R. Number</label>
      <input type="text" id="stu-id" class="form-control" placeholder="ADM-2026-050">
    </div>

    <div class="grid-2">
      <div class="form-group">
        <label class="form-label" for="stu-first">First Name</label>
        <input type="text" id="stu-first" class="form-control" placeholder="e.g. Ananya">
      </div>
      <div class="form-group">
        <label class="form-label" for="stu-last">Last Name</label>
        <input type="text" id="stu-last" class="form-control" placeholder="e.g. Sharma">
      </div>
    </div>

    <div class="form-group">
      <label class="form-label" for="stu-class">Class & Section</label>
      <select id="stu-class" class="form-control"></select>
    </div>

    <div class="form-group">
      <label class="form-label" for="stu-parent">Father / Mother / Guardian Name</label>
      <input type="text" id="stu-parent" class="form-control" placeholder="e.g. Ramesh Sharma">
    </div>

    <div class="grid-2">
      <div class="form-group">
        <label class="form-label" for="stu-email">Parent Email ID</label>
        <input type="email" id="stu-email" class="form-control" placeholder="parent@example.com">
      </div>
      <div class="form-group">
        <label class="form-label" for="stu-phone">Parent Mobile No</label>
        <input type="tel" id="stu-phone" class="form-control" placeholder="+91 98765 43210">
      </div>
    </div>

    <div style="display: flex; gap: 1.5rem; margin-bottom: 1.5rem; background: var(--bg-subtle); padding: 0.85rem; border-radius: var(--radius-md);">
      <label style="cursor: pointer; display: flex; align-items: center; gap: 0.4rem; font-size: 0.9rem;">
        <input type="checkbox" id="stu-transport" style="width: 18px; height: 18px;"> 🚌 School Bus Route
      </label>
      <label style="cursor: pointer; display: flex; align-items: center; gap: 0.4rem; font-size: 0.9rem;">
        <input type="checkbox" id="stu-hostel" style="width: 18px; height: 18px;"> 🏠 Hostel & Mess
      </label>
    </div>

    <div style="display: flex; justify-content: flex-end; gap: 0.75rem;">
      <button class="btn btn-outline" onclick="closeModals()">Cancel</button>
      <button class="btn btn-primary" onclick="submitStudent()">Save & Enroll Student</button>
    </div>
  </div>
</div>

<!-- Toast Container -->
<div class="toast-container" id="toast-container" aria-live="polite"></div>

<script>
let allStudents = [];
let allInvoices = [];

function toggleSidebar(open) {
  const sidebar = document.getElementById('app-sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  if (open) {
    sidebar.classList.add('open');
    backdrop.classList.add('open');
  } else {
    sidebar.classList.remove('open');
    backdrop.classList.remove('open');
  }
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = 'toast';
  const icon = type === 'success' ? '✓' : (type === 'error' ? '⚠️' : 'ℹ️');
  toast.innerHTML = `<span><strong>${icon}</strong> ${message}</span><button onclick="this.parentElement.remove()" style="background:none;border:none;color:#94a3b8;cursor:pointer;font-size:1.1rem;padding:0 4px;">✕</button>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.transition = 'opacity 0.3s';
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function switchTab(tabId) {
  toggleSidebar(false);

  document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.b-nav-item').forEach(el => el.classList.remove('active'));
  
  const target = document.getElementById('pane-' + tabId);
  if (target) target.classList.add('active');

  const bnav = document.getElementById('bnav-' + tabId);
  if (bnav) bnav.classList.add('active');

  // Highlight matching sidebar nav item
  document.querySelectorAll('.nav-item').forEach(el => {
    if (el.getAttribute('onclick')?.includes(tabId)) el.classList.add('active');
  });

  const titles = {
    dashboard: 'Accounts Dashboard',
    students: 'Scholar Register',
    invoices: 'Fee Invoices & Dues',
    terminal: 'Fee Collection Desk',
    defaulters: 'Overdue Defaulters',
    reports: 'Collection Register'
  };
  document.getElementById('page-title').innerText = titles[tabId] || 'Fee Management';

  if (tabId === 'dashboard') loadDashboard();
  if (tabId === 'students') loadStudents();
  if (tabId === 'invoices') loadInvoices();
  if (tabId === 'terminal') loadTerminal();
  if (tabId === 'defaulters') loadDefaulters();
  if (tabId === 'reports') loadReports();
}

async function loadDashboard() {
  try {
    const res = await fetch('/api/kpis');
    const data = await res.json();
    document.getElementById('kpi-students').innerText = data.active_students;
    document.getElementById('kpi-collected').innerText = '₹' + parseFloat(data.total_collected).toLocaleString('en-IN', {minimumFractionDigits: 2});
    document.getElementById('kpi-outstanding').innerText = '₹' + parseFloat(data.total_outstanding).toLocaleString('en-IN', {minimumFractionDigits: 2});
    document.getElementById('kpi-defaulters').innerText = data.defaulters_count;

    const repRes = await fetch('/api/reports/collection');
    const repData = await repRes.json();
    const tbody = document.querySelector('#tbl-recent-payments tbody');
    tbody.innerHTML = '';
    
    if (!repData.records || repData.records.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 2rem;">No collections recorded yet.</td></tr>';
      return;
    }

    repData.records.slice(0, 6).forEach(r => {
      tbody.innerHTML += `<tr>
        <td><strong>${r.payment_ref}</strong></td>
        <td>#${r.invoice_id}</td>
        <td style="font-weight: 700;">₹${parseFloat(r.amount).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
        <td><span class="status-badge badge-paid">${r.payment_method}</span></td>
        <td style="font-family: monospace; font-size: 0.85rem;">${r.transaction_id || 'CASH-COUNTER'}</td>
        <td>${r.payment_date}</td>
        <td>${r.cashier_name}</td>
      </tr>`;
    });
  } catch (err) {
    showToast('Failed to load dashboard metrics', 'error');
  }
}

async function loadStudents() {
  try {
    const res = await fetch('/api/students');
    allStudents = await res.json();
    renderStudents(allStudents);
  } catch (err) {
    showToast('Failed to load students list', 'error');
  }
}

function renderStudents(list) {
  const tbody = document.querySelector('#tbl-students tbody');
  tbody.innerHTML = '';
  if (list.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 2rem;">No matching student records found.</td></tr>';
    return;
  }
  list.forEach(s => {
    tbody.innerHTML += `<tr>
      <td><strong>${s.student_id}</strong></td>
      <td>${s.first_name} ${s.last_name}</td>
      <td>${s.class_name}</td>
      <td>${s.parent_phone}</td>
      <td>${s.is_transport_enrolled ? '🚌 Bus ' : ''}${s.is_hostel_enrolled ? '🏠 Hostel' : ''}</td>
      <td><span class="status-badge badge-paid">${s.status}</span></td>
      <td><button class="btn btn-outline btn-sm" onclick="generateInvoiceForStudent('${s.student_id}')">⚡ Issue Invoice</button></td>
    </tr>`;
  });
}

function filterStudentsTable() {
  const q = document.getElementById('search-students').value.toLowerCase().trim();
  const filtered = allStudents.filter(s => 
    s.student_id.toLowerCase().includes(q) ||
    (s.first_name + ' ' + s.last_name).toLowerCase().includes(q) ||
    (s.parent_name && s.parent_name.toLowerCase().includes(q)) ||
    (s.class_name && s.class_name.toLowerCase().includes(q))
  );
  renderStudents(filtered);
}

async function loadInvoices() {
  try {
    const statusVal = document.getElementById('filter-invoice-status').value;
    const url = statusVal ? `/api/invoices?status=${statusVal}` : '/api/invoices';
    const res = await fetch(url);
    allInvoices = await res.json();
    renderInvoices(allInvoices);
  } catch (err) {
    showToast('Failed to load invoices', 'error');
  }
}

function renderInvoices(list) {
  const tbody = document.querySelector('#tbl-invoices tbody');
  tbody.innerHTML = '';
  if (list.length === 0) {
    tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; color: var(--text-muted); padding: 2rem;">No invoices found matching criteria.</td></tr>';
    return;
  }
  list.forEach(i => {
    let badge = 'badge-unpaid';
    if (i.status === 'PAID') badge = 'badge-paid';
    if (i.status === 'PARTIALLY_PAID') badge = 'badge-partial';
    if (i.status === 'OVERDUE') badge = 'badge-overdue';

    tbody.innerHTML += `<tr>
      <td><strong>${i.invoice_number}</strong></td>
      <td>${i.student_name}</td>
      <td>${i.class_name}</td>
      <td>${i.term}</td>
      <td>${i.due_date}</td>
      <td>₹${parseFloat(i.total_payable).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
      <td>₹${parseFloat(i.paid_amount).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
      <td style="font-weight: 800; color: ${i.balance_amount > 0 ? 'var(--danger)' : 'var(--success)'};">₹${parseFloat(i.balance_amount).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
      <td><span class="status-badge ${badge}">${i.status}</span></td>
      <td>${i.balance_amount > 0 ? `<button class="btn btn-primary btn-sm" onclick="paySpecificInvoice(${i.id})">Collect</button>` : '✓ Settled'}</td>
    </tr>`;
  });
}

function filterInvoicesTable() {
  const q = document.getElementById('search-invoices').value.toLowerCase().trim();
  const filtered = allInvoices.filter(i =>
    i.invoice_number.toLowerCase().includes(q) ||
    i.student_name.toLowerCase().includes(q) ||
    i.class_name.toLowerCase().includes(q)
  );
  renderInvoices(filtered);
}

async function loadTerminal() {
  try {
    const res = await fetch('/api/invoices?status=UNPAID');
    const unpaid = await res.json();
    const sel = document.getElementById('terminal-invoice-select');
    sel.innerHTML = '<option value="">-- Choose student with pending dues --</option>';
    unpaid.forEach(inv => {
      sel.innerHTML += `<option value="${inv.id}" data-name="${inv.student_name}" data-bal="${inv.balance_amount}">${inv.invoice_number} — ${inv.student_name} (${inv.class_name}) [Due: ₹${parseFloat(inv.balance_amount).toLocaleString('en-IN')}]</option>`;
    });
  } catch (err) {
    showToast('Failed to load pending bills', 'error');
  }
}

function terminalInvoiceChanged() {
  const sel = document.getElementById('terminal-invoice-select');
  const opt = sel.options[sel.selectedIndex];
  const infoBox = document.getElementById('terminal-invoice-info');
  if (opt && opt.value) {
    infoBox.style.display = 'block';
    document.getElementById('term-stu-name').innerText = opt.getAttribute('data-name');
    document.getElementById('term-stu-bal').innerText = '₹' + parseFloat(opt.getAttribute('data-bal')).toLocaleString('en-IN', {minimumFractionDigits: 2});
    document.getElementById('terminal-amount').value = parseFloat(opt.getAttribute('data-bal')).toFixed(0);
  } else {
    infoBox.style.display = 'none';
  }
}

async function submitTerminalPayment() {
  const invId = document.getElementById('terminal-invoice-select').value;
  const amount = document.getElementById('terminal-amount').value;
  const method = document.getElementById('terminal-method').value;
  const tx = document.getElementById('terminal-tx').value || 'COUNTER-CASH';

  if (!invId || !amount || parseFloat(amount) <= 0) {
    showToast('Please select a student bill and enter a valid positive payment amount.', 'warning');
    return;
  }

  try {
    const res = await fetch('/api/payments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        invoice_id: parseInt(invId),
        amount: parseFloat(amount),
        payment_method: method,
        transaction_id: tx,
        cashier_name: 'Accounts Desk'
      })
    });

    const data = await res.json();
    if (res.ok) {
      showToast('Payment credited! Receipt: ' + data.receipt.receipt_number, 'success');
      window.open('/api/receipts/' + data.receipt.receipt_number + '/html', '_blank');
      loadTerminal();
      loadDashboard();
    } else {
      showToast('Payment failed: ' + (data.error || 'Server error'), 'error');
    }
  } catch (err) {
    showToast('Network error processing payment', 'error');
  }
}

async function loadDefaulters() {
  try {
    const res = await fetch('/api/defaulters');
    const list = await res.json();
    const tbody = document.querySelector('#tbl-defaulters tbody');
    tbody.innerHTML = '';
    if (list.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--success); padding: 2rem;">✓ Excellent! Zero overdue defaulters on record.</td></tr>';
      return;
    }
    list.forEach(d => {
      tbody.innerHTML += `<tr>
        <td><strong>${d.invoice_number}</strong></td>
        <td>${d.student_name}</td>
        <td>${d.class_name}</td>
        <td>${d.parent_phone}</td>
        <td>${d.due_date}</td>
        <td><span class="status-badge badge-overdue">${d.days_overdue} days</span></td>
        <td style="font-weight: 800; color: var(--danger);">₹${parseFloat(d.balance_due).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
      </tr>`;
    });
  } catch (err) {
    showToast('Failed to load defaulter list', 'error');
  }
}

async function loadReports() {
  try {
    const res = await fetch('/api/reports/collection');
    const data = await res.json();
    const tbody = document.querySelector('#tbl-all-collections tbody');
    tbody.innerHTML = '';
    if (!data.records || data.records.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 2rem;">No collection records available.</td></tr>';
      return;
    }
    data.records.forEach(r => {
      tbody.innerHTML += `<tr>
        <td><strong>${r.payment_ref}</strong></td>
        <td>#${r.invoice_id}</td>
        <td style="font-weight: 700;">₹${parseFloat(r.amount).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
        <td><span class="status-badge badge-paid">${r.payment_method}</span></td>
        <td style="font-family: monospace; font-size: 0.85rem;">${r.transaction_id || 'CASH-COUNTER'}</td>
        <td>${r.payment_date}</td>
        <td>${r.cashier_name}</td>
      </tr>`;
    });
  } catch (err) {
    showToast('Failed to load collection log', 'error');
  }
}

function paySpecificInvoice(invId) {
  switchTab('terminal');
  const sel = document.getElementById('terminal-invoice-select');
  sel.value = invId;
  terminalInvoiceChanged();
}

async function generateInvoiceForStudent(studentId) {
  if (!confirm('Issue Term-1 2026-2027 fee invoice for student ' + studentId + '?')) return;
  try {
    const res = await fetch('/api/invoices/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: studentId,
        academic_year: '2026-2027',
        term: 'TERM_1'
      })
    });
    const data = await res.json();
    if (res.ok) {
      showToast('Fee invoice issued: ' + data.invoice_number, 'success');
      loadStudents();
    } else {
      showToast('Failed: ' + data.error, 'error');
    }
  } catch (err) {
    showToast('Error issuing invoice', 'error');
  }
}

function openPaymentModal() {
  switchTab('terminal');
}

async function openStudentModal() {
  try {
    const res = await fetch('/api/classes');
    const classes = await res.json();
    const sel = document.getElementById('stu-class');
    sel.innerHTML = '';
    classes.forEach(c => sel.innerHTML += `<option value="${c.id}">${c.name}</option>`);
    document.getElementById('modal-student').style.display = 'flex';
  } catch (err) {
    showToast('Failed to open enrollment modal', 'error');
  }
}

function closeModals() {
  document.querySelectorAll('.modal-overlay').forEach(m => m.style.display = 'none');
}

// Close modals when pressing Escape key
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModals();
});

async function submitStudent() {
  const payload = {
    student_id: document.getElementById('stu-id').value.trim(),
    first_name: document.getElementById('stu-first').value.trim(),
    last_name: document.getElementById('stu-last').value.trim(),
    class_id: parseInt(document.getElementById('stu-class').value),
    parent_name: document.getElementById('stu-parent').value.trim(),
    parent_email: document.getElementById('stu-email').value.trim(),
    parent_phone: document.getElementById('stu-phone').value.trim(),
    is_transport_enrolled: document.getElementById('stu-transport').checked,
    is_hostel_enrolled: document.getElementById('stu-hostel').checked
  };

  if (!payload.student_id || !payload.first_name || !payload.parent_name) {
    showToast('Please fill in Admission No., Student Name and Parent Name.', 'warning');
    return;
  }

  try {
    const res = await fetch('/api/students', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      closeModals();
      showToast('Student enrolled successfully!', 'success');
      loadStudents();
      loadDashboard();
    } else {
      const err = await res.json();
      showToast('Failed to save student: ' + err.error, 'error');
    }
  } catch (err) {
    showToast('Network error saving student', 'error');
  }
}

window.onload = () => loadDashboard();
</script>
</body>
</html>
"""


class FeeServerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, service: SchoolFeeService, **kwargs):
        self.service = service
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # 1. Main Dashboard UI
        if path == "/" or path == "/index.html":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode("utf-8"))
            return

        # 1.5 Interactive Web Terminal Console
        if path in ("/terminal", "/terminal/"):
            try:
                from web_terminal.server import TERMINAL_PAGE_HTML
            except ImportError:
                proj_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                for p in (proj_root, os.path.join(proj_root, "src")):
                    if p not in sys.path:
                        sys.path.insert(0, p)
                from web_terminal.server import TERMINAL_PAGE_HTML
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(TERMINAL_PAGE_HTML.encode("utf-8"))
            return

        # 2. REST API: KPIs
        if path == "/api/kpis":
            kpis = self.service.get_kpis()
            self._send_json({k: str(v) if isinstance(v, Decimal) else v for k, v in kpis.items()})
            return

        # 3. REST API: Classes
        if path == "/api/classes":
            classes = self.service.get_classes()
            self._send_json([{"id": c.id, "name": c.name, "grade_level": c.grade_level} for c in classes])
            return

        # 4. REST API: Students
        if path == "/api/students":
            class_id = int(query["class_id"][0]) if "class_id" in query else None
            search = query.get("search", [None])[0]
            students = self.service.list_students(class_id=class_id, search=search)
            self._send_json(
                [
                    {
                        "student_id": s.student_id,
                        "first_name": s.first_name,
                        "last_name": s.last_name,
                        "class_id": s.class_id,
                        "class_name": s.class_name,
                        "parent_name": s.parent_name,
                        "parent_email": s.parent_email,
                        "parent_phone": s.parent_phone,
                        "is_transport_enrolled": s.is_transport_enrolled,
                        "is_hostel_enrolled": s.is_hostel_enrolled,
                        "status": s.status.value,
                    }
                    for s in students
                ]
            )
            return

        # 5. REST API: Invoices
        if path == "/api/invoices":
            st_val = query.get("status", [None])[0]
            status_enum = InvoiceStatus(st_val) if st_val else None
            student_id = query.get("student_id", [None])[0]
            invoices = self.service.list_invoices(student_id=student_id, status=status_enum)
            self._send_json(
                [
                    {
                        "id": i.id,
                        "invoice_number": i.invoice_number,
                        "student_id": i.student_id,
                        "student_name": i.student_name,
                        "class_name": i.class_name,
                        "term": i.term.value,
                        "issue_date": str(i.issue_date),
                        "due_date": str(i.due_date),
                        "subtotal": float(i.subtotal),
                        "discount_total": float(i.discount_total),
                        "late_fee": float(i.late_fee),
                        "total_payable": float(i.total_payable),
                        "paid_amount": float(i.paid_amount),
                        "balance_amount": float(i.balance_amount),
                        "status": i.status.value,
                    }
                    for i in invoices
                ]
            )
            return

        # 6. REST API: Defaulters
        if path == "/api/defaulters":
            report = self.service.get_defaulters_report()
            self._send_json(
                [
                    {
                        "invoice_number": r["invoice_number"],
                        "student_id": r["student_id"],
                        "student_name": r["student_name"],
                        "class_name": r["class_name"],
                        "parent_phone": r["parent_phone"],
                        "due_date": r["due_date"],
                        "days_overdue": r["days_overdue"],
                        "balance_due": float(r["balance_due"]),
                    }
                    for r in report
                ]
            )
            return

        # 7. REST API: Collection Summary
        if path == "/api/reports/collection":
            start_d = query.get("start", [None])[0]
            end_d = query.get("end", [None])[0]
            summary = self.service.get_collection_summary(start_d, end_d)
            self._send_json(
                {
                    "total_collected": float(summary["total_collected"]),
                    "by_method": {k: float(v) for k, v in summary["by_method"].items()},
                    "payments_count": summary["payments_count"],
                    "records": [
                        {
                            "payment_ref": r["payment_ref"],
                            "invoice_id": r["invoice_id"],
                            "amount": float(r["amount"]),
                            "payment_method": r["payment_method"],
                            "payment_date": r["payment_date"],
                            "cashier_name": r["cashier_name"],
                        }
                        for r in summary["records"]
                    ],
                }
            )
            return

        # 8. Printable HTML Receipt
        if path.startswith("/api/receipts/") and path.endswith("/html"):
            parts = path.strip("/").split("/")
            rec_num = parts[2]
            receipt = self.service.get_receipt(rec_num)
            if not receipt:
                self.send_error(HTTPStatus.NOT_FOUND, f"Receipt '{rec_num}' not found.")
                return
            html = ReceiptFormatter.format_html(receipt)
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        # 9. CSV Exports
        if path == "/api/export/defaulters.csv":
            csv_data = self.service.export_defaulters_csv()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/csv")
            self.send_header("Content-Disposition", 'attachment; filename="fee_defaulters.csv"')
            self.end_headers()
            self.wfile.write(csv_data.encode("utf-8"))
            return

        if path == "/api/export/collection.csv":
            csv_data = self.service.export_collection_csv()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/csv")
            self.send_header("Content-Disposition", 'attachment; filename="fee_collections.csv"')
            self.end_headers()
            self.wfile.write(csv_data.encode("utf-8"))
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Path not found.")

    def do_POST(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
            return

        try:
            if path == "/api/exec":
                try:
                    from web_terminal.shell import RealTerminalEngine
                except ImportError:
                    proj_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    for p in (proj_root, os.path.join(proj_root, "src")):
                        if p not in sys.path:
                            sys.path.insert(0, p)
                    from web_terminal.shell import RealTerminalEngine

                session_id = payload.get("session_id", "default")
                if not hasattr(FeeServerHandler, "_term_sessions"):
                    FeeServerHandler._term_sessions = {}
                if session_id not in FeeServerHandler._term_sessions:
                    FeeServerHandler._term_sessions[session_id] = RealTerminalEngine()

                shell = FeeServerHandler._term_sessions[session_id]
                cmd = payload.get("cmd", "")
                result = shell.execute(cmd)
                self._send_json(result)
                return

            if path == "/api/students":
                new_stu = Student(
                    student_id=payload["student_id"],
                    first_name=payload["first_name"],
                    last_name=payload["last_name"],
                    class_id=int(payload["class_id"]),
                    parent_name=payload["parent_name"],
                    parent_email=payload["parent_email"],
                    parent_phone=payload["parent_phone"],
                    is_transport_enrolled=bool(payload.get("is_transport_enrolled", False)),
                    is_hostel_enrolled=bool(payload.get("is_hostel_enrolled", False)),
                    status=StudentStatus.ACTIVE,
                )
                created = self.service.add_student(new_stu)
                self._send_json({"status": "success", "student_id": created.student_id}, status=HTTPStatus.CREATED)
                return

            if path == "/api/invoices/generate":
                inv = self.service.generate_student_invoice(
                    student_id=payload["student_id"],
                    academic_year=payload.get("academic_year", "2026-2027"),
                    term=FeeTerm(payload.get("term", "TERM_1")),
                )
                self._send_json({"status": "success", "invoice_number": inv.invoice_number, "id": inv.id})
                return

            if path == "/api/payments":
                amount = Decimal(str(payload["amount"]))
                payment, receipt = self.service.record_payment(
                    invoice_id=int(payload["invoice_id"]),
                    amount=amount,
                    payment_method=PaymentMethod(payload.get("payment_method", "CASH")),
                    transaction_id=payload.get("transaction_id", "COUNTER-CASH"),
                    cashier_name=payload.get("cashier_name", "Counter Cashier"),
                )
                self._send_json(
                    {
                        "status": "success",
                        "payment": {
                            "payment_ref": payment.payment_ref,
                            "amount": float(payment.amount),
                        },
                        "receipt": {
                            "receipt_number": receipt.receipt_number,
                            "receipt_hash": receipt.receipt_hash,
                        },
                    }
                )
                return

            self.send_error(HTTPStatus.NOT_FOUND, "Route not found.")
        except Exception as e:
            self._send_json({"error": str(e)}, status=HTTPStatus.BAD_REQUEST)

    def _send_json(self, data: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        raw = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def run_server(
    host: Optional[str] = None,
    port: Optional[int] = None,
    db_path: Optional[str] = None,
) -> None:
    host = host or os.environ.get("HOST", "127.0.0.1")
    if port is None:
        port = int(os.environ.get("PORT", 8000))
    service = SchoolFeeService(db_path=db_path)
    # Ensure database schema and seed data exist
    conn = service._get_connection()
    try:
        initialize_schema(conn)
        seed_sample_data(conn)
    finally:
        conn.close()

    def handler_factory(*args, **kwargs):
        return FeeServerHandler(*args, service=service, **kwargs)

    server = ThreadingHTTPServer((host, port), handler_factory)
    print(f"\n🚀 Delhi Public Academy Fee System Web Dashboard & API running at:")
    print(f"   👉 http://{host}:{port}/")
    print(f"   (Press Ctrl+C to stop the server)\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
        server.server_close()
