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
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Greenvale Academy — Fee Management System</title>
<style>
  :root {
    --primary: #0f766e;
    --primary-hover: #115e59;
    --primary-light: #ccfbf1;
    --bg-base: #f8fafc;
    --card-bg: #ffffff;
    --text-main: #0f172a;
    --text-muted: #64748b;
    --border-color: #e2e8f0;
    --success: #16a34a;
    --warning: #ca8a04;
    --danger: #dc2626;
    --danger-light: #fee2e2;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background-color: var(--bg-base);
    color: var(--text-main);
    line-height: 1.5;
  }
  .layout { display: flex; min-height: 100vh; }
  
  /* Sidebar */
  .sidebar {
    width: 260px;
    background: #0f172a;
    color: #f8fafc;
    display: flex;
    flex-direction: column;
    padding: 1.5rem 1rem;
    flex-shrink: 0;
  }
  .brand {
    font-size: 1.25rem;
    font-weight: 700;
    color: #2dd4bf;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .nav-menu { list-style: none; display: flex; flex-direction: column; gap: 0.25rem; }
  .nav-item {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    color: #94a3b8;
    text-decoration: none;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
  }
  .nav-item:hover, .nav-item.active {
    background: #1e293b;
    color: #38bdf8;
  }
  .nav-item.active {
    background: var(--primary);
    color: #ffffff;
  }

  /* Main Container */
  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
  }
  .topbar {
    background: var(--card-bg);
    border-bottom: 1px solid var(--border-color);
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .page-title { font-size: 1.35rem; font-weight: 700; color: var(--text-main); }
  .content-area { padding: 2rem; }

  /* KPI Grid */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }
  .kpi-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }
  .kpi-label { font-size: 0.85rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; }
  .kpi-value { font-size: 1.75rem; font-weight: 700; margin-top: 0.5rem; color: var(--primary); }

  /* Cards & Tables */
  .card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.25rem;
  }
  .card-title { font-size: 1.1rem; font-weight: 600; }
  
  table { width: 100%; border-collapse: collapse; text-align: left; }
  th {
    background: #f1f5f9;
    padding: 0.75rem 1rem;
    font-size: 0.8rem;
    text-transform: uppercase;
    color: var(--text-muted);
    border-bottom: 1px solid var(--border-color);
  }
  td {
    padding: 0.85rem 1rem;
    border-bottom: 1px solid var(--border-color);
    font-size: 0.9rem;
  }
  tr:hover td { background-color: #f8fafc; }

  /* Badges */
  .status-badge {
    display: inline-block;
    padding: 0.25rem 0.65rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
  }
  .badge-paid { background: #dcfce7; color: #15803d; }
  .badge-unpaid { background: #fef3c7; color: #b45309; }
  .badge-partial { background: #e0f2fe; color: #0369a1; }
  .badge-overdue { background: #fee2e2; color: #b91c1c; }

  /* Buttons */
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    border: none;
    transition: background 0.15s;
    text-decoration: none;
  }
  .btn-primary { background: var(--primary); color: #ffffff; }
  .btn-primary:hover { background: var(--primary-hover); }
  .btn-outline { background: transparent; border: 1px solid var(--border-color); color: var(--text-main); }
  .btn-outline:hover { background: #f1f5f9; }
  .btn-sm { padding: 0.25rem 0.6rem; font-size: 0.75rem; }

  /* Modal */
  .modal-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(2px);
    z-index: 100;
    justify-content: center;
    align-items: center;
  }
  .modal {
    background: #ffffff;
    border-radius: 12px;
    width: 90%;
    max-width: 550px;
    padding: 2rem;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  }
  .form-group { margin-bottom: 1rem; }
  .form-label { display: block; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.35rem; color: #334155; }
  .form-control {
    width: 100%;
    padding: 0.6rem 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    font-size: 0.9rem;
  }

  .tab-pane { display: none; }
  .tab-pane.active { display: block; }
</style>
</head>
<body>
<div class="layout">
  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="brand">🎓 Delhi Public Academy</div>
    <div style="font-size: 0.72rem; color: #94a3b8; margin-top: -1.5rem; margin-bottom: 1.5rem; padding-left: 0.25rem;">CBSE Affiliated • Fee Accounts</div>
    <ul class="nav-menu">
      <li class="nav-item active" onclick="switchTab('dashboard')">📊 Accounts Dashboard</li>
      <li class="nav-item" onclick="switchTab('students')">🧑‍🎓 Student Directory</li>
      <li class="nav-item" onclick="switchTab('invoices')">🧾 Fee Invoices & Dues</li>
      <li class="nav-item" onclick="switchTab('terminal')">💳 Fee Counter Terminal</li>
      <li class="nav-item" onclick="switchTab('defaulters')">⚠️ Overdue Defaulters</li>
      <li class="nav-item" onclick="switchTab('reports')">📈 Financial Reports</li>
    </ul>
  </aside>

  <!-- Main Container -->
  <main class="main-content">
    <header class="topbar">
      <div>
        <div class="page-title" id="page-title">Accounts Dashboard</div>
        <div style="font-size: 0.8rem; color: #64748b;">Delhi Public Academy, New Delhi — Session 2026-2027</div>
      </div>
      <div>
        <button class="btn btn-primary" onclick="openPaymentModal()">+ Collect Fee (Counter)</button>
      </div>
    </header>

    <div class="content-area">
      <!-- 1. DASHBOARD TAB -->
      <section id="pane-dashboard" class="tab-pane active">
        <div class="kpi-grid">
          <div class="kpi-card">
            <div class="kpi-label">Active Enrolled Students</div>
            <div class="kpi-value" id="kpi-students">...</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Total Fee Collected</div>
            <div class="kpi-value" id="kpi-collected" style="color: var(--success);">...</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Outstanding Balance</div>
            <div class="kpi-value" id="kpi-outstanding" style="color: var(--danger);">...</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Overdue Defaulters</div>
            <div class="kpi-value" id="kpi-defaulters">...</div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="card-title">Recent Fee Collections & Receipts</div>
            <button class="btn btn-outline btn-sm" onclick="loadDashboard()">Refresh</button>
          </div>
          <table id="tbl-recent-payments">
            <thead>
              <tr><th>Receipt / Ref #</th><th>Invoice #</th><th>Amount (₹)</th><th>Payment Mode</th><th>Txn / UTR No</th><th>Date</th><th>Cashier</th></tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </section>

      <!-- 2. STUDENTS TAB -->
      <section id="pane-students" class="tab-pane">
        <div class="card">
          <div class="card-header">
            <div class="card-title">Enrolled Students (Scholar Register)</div>
            <button class="btn btn-primary btn-sm" onclick="openStudentModal()">+ Enroll New Student</button>
          </div>
          <table id="tbl-students">
            <thead>
              <tr><th>Admission No</th><th>Student Name</th><th>Class & Sec</th><th>Parent Name & Phone</th><th>Opted Facilities</th><th>Status</th><th>Actions</th></tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </section>

      <!-- 3. INVOICES TAB -->
      <section id="pane-invoices" class="tab-pane">
        <div class="card">
          <div class="card-header">
            <div class="card-title">Student Fee Invoices & Quarterly Dues</div>
            <div style="display: flex; gap: 0.5rem;">
              <button class="btn btn-primary btn-sm" onclick="openBatchModal()">Batch Issue Class Invoices</button>
            </div>
          </div>
          <table id="tbl-invoices">
            <thead>
              <tr><th>Bill / Inv #</th><th>Student Name</th><th>Class</th><th>Fee Term</th><th>Due Date</th><th>Payable (₹)</th><th>Paid (₹)</th><th>Balance (₹)</th><th>Status</th><th>Action</th></tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </section>

      <!-- 4. CASHIER TERMINAL TAB -->
      <section id="pane-terminal" class="tab-pane">
        <div class="card" style="max-width: 620px; margin: 0 auto;">
          <div class="card-header">
            <div>
              <div class="card-title">Fee Collection Counter</div>
              <div style="font-size: 0.8rem; color: #64748b;">Instant fee collection, UTR logging & digital receipt issuance</div>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Select Student / Pending Bill</label>
            <select id="terminal-invoice-select" class="form-control" onchange="terminalInvoiceChanged()"></select>
          </div>
          <div id="terminal-invoice-info" style="display: none; background: #f8fafc; border: 1px solid var(--border-color); border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem;">
            <div><strong>Student Name:</strong> <span id="term-stu-name"></span></div>
            <div><strong>Outstanding Due:</strong> <span id="term-stu-bal" style="color: var(--danger); font-weight: 700;"></span></div>
          </div>
          <div class="form-group">
            <label class="form-label">Payment Amount (₹)</label>
            <input type="number" step="1" id="terminal-amount" class="form-control" placeholder="0.00">
          </div>
          <div class="form-group">
            <label class="form-label">Payment Mode</label>
            <select id="terminal-method" class="form-control">
              <option value="UPI">UPI (Google Pay / PhonePe / Paytm / BHIM)</option>
              <option value="CASH">Cash at Fee Counter</option>
              <option value="NET_BANKING">Net Banking / NEFT / IMPS</option>
              <option value="CHEQUE_DD">Cheque / Demand Draft (DD)</option>
              <option value="CARD">POS Debit / Credit Card</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Transaction Reference (UTR No / Cheque No / VPA)</label>
            <input type="text" id="terminal-tx" class="form-control" placeholder="e.g. UPI Ref / UTR No: 202604011234 or Cheque: 442101">
          </div>
          <button class="btn btn-primary" style="width: 100%; justify-content: center; padding: 0.75rem; font-size: 1rem;" onclick="submitTerminalPayment()">Process Collection & Print Official Receipt</button>
        </div>
      </section>

      <!-- 5. DEFAULTERS TAB -->
      <section id="pane-defaulters" class="tab-pane">
        <div class="card">
          <div class="card-header">
            <div>
              <div class="card-title">Fee Defaulters & Overdue Invoices</div>
              <div style="font-size: 0.8rem; color: #64748b;">Students with overdue quarterly fee payments</div>
            </div>
            <a href="/api/export/defaulters.csv" class="btn btn-outline btn-sm">📥 Export Defaulters CSV</a>
          </div>
          <table id="tbl-defaulters">
            <thead>
              <tr><th>Invoice #</th><th>Student Name</th><th>Class</th><th>Parent Contact</th><th>Due Date</th><th>Days Overdue</th><th>Balance Due (₹)</th></tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </section>

      <!-- 6. ACCOUNTING TAB -->
      <section id="pane-reports" class="tab-pane">
        <div class="card">
          <div class="card-header">
            <div class="card-title">Cashier Daily Collection Register</div>
            <a href="/api/export/collection.csv" class="btn btn-outline btn-sm">📥 Export Collection CSV</a>
          </div>
          <table id="tbl-all-collections">
            <thead>
              <tr><th>Payment Ref</th><th>Invoice #</th><th>Amount (₹)</th><th>Mode</th><th>Txn / UTR No</th><th>Date & Time</th><th>Cashier</th></tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </section>
    </div>
  </main>
</div>

<!-- Enroll Student Modal -->
<div id="modal-student" class="modal-overlay">
  <div class="modal">
    <div class="card-title" style="margin-bottom: 1rem;">Enroll New Student (Scholar Register)</div>
    <div class="form-group">
      <label class="form-label">Admission / S.R. Number</label>
      <input type="text" id="stu-id" class="form-control" placeholder="ADM-2026-006">
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
      <div class="form-group">
        <label class="form-label">First Name</label>
        <input type="text" id="stu-first" class="form-control" placeholder="e.g. Ananya">
      </div>
      <div class="form-group">
        <label class="form-label">Last Name</label>
        <input type="text" id="stu-last" class="form-control" placeholder="e.g. Sharma">
      </div>
    </div>
    <div class="form-group">
      <label class="form-label">Class & Section</label>
      <select id="stu-class" class="form-control"></select>
    </div>
    <div class="form-group">
      <label class="form-label">Father / Mother / Guardian Name</label>
      <input type="text" id="stu-parent" class="form-control" placeholder="e.g. Ramesh Sharma">
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
      <div class="form-group">
        <label class="form-label">Parent Email ID</label>
        <input type="email" id="stu-email" class="form-control" placeholder="parent@example.com">
      </div>
      <div class="form-group">
        <label class="form-label">Parent Mobile No</label>
        <input type="tel" id="stu-phone" class="form-control" placeholder="+91 98765 43210">
      </div>
    </div>
    <div style="display: flex; gap: 1.5rem; margin-bottom: 1.5rem; background: #f8fafc; padding: 0.75rem; border-radius: 6px;">
      <label style="cursor: pointer;"><input type="checkbox" id="stu-transport"> 🚌 School Bus Transport</label>
      <label style="cursor: pointer;"><input type="checkbox" id="stu-hostel"> 🏠 Hostel & Mess</label>
    </div>
    <div style="display: flex; justify-content: flex-end; gap: 0.5rem;">
      <button class="btn btn-outline" onclick="closeModals()">Cancel</button>
      <button class="btn btn-primary" onclick="submitStudent()">Save & Enroll Student</button>
    </div>
  </div>
</div>

<script>
let currentInvoices = [];

function switchTab(tabId) {
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  
  const target = document.getElementById('pane-' + tabId);
  if (target) target.classList.add('active');

  const titles = {
    dashboard: 'Accounts Dashboard',
    students: 'Student Enrollment Directory',
    invoices: 'Fee Invoicing & Dues',
    terminal: 'Cashier Payment Terminal',
    defaulters: 'Overdue Fee Defaulters',
    reports: 'Financial Accounting & Reports'
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
  (repData.records || []).slice(0, 5).forEach(r => {
    tbody.innerHTML += `<tr>
      <td><strong>${r.payment_ref}</strong></td>
      <td>#${r.invoice_id}</td>
      <td>₹${parseFloat(r.amount).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
      <td><span class="status-badge badge-paid">${r.payment_method}</span></td>
      <td>${r.transaction_id || 'CASH-COUNTER'}</td>
      <td>${r.payment_date}</td>
      <td>${r.cashier_name}</td>
    </tr>`;
  });
}

async function loadStudents() {
  const res = await fetch('/api/students');
  const list = await res.json();
  const tbody = document.querySelector('#tbl-students tbody');
  tbody.innerHTML = '';
  list.forEach(s => {
    tbody.innerHTML += `<tr>
      <td><strong>${s.student_id}</strong></td>
      <td>${s.first_name} ${s.last_name}</td>
      <td>${s.class_name}</td>
      <td>${s.parent_phone}</td>
      <td>${s.is_transport_enrolled ? '🚌 Bus ' : ''}${s.is_hostel_enrolled ? '🏠 Hostel' : ''}</td>
      <td><span class="status-badge badge-paid">${s.status}</span></td>
      <td><button class="btn btn-outline btn-sm" onclick="generateInvoiceForStudent('${s.student_id}')">Issue Invoice</button></td>
    </tr>`;
  });
}

async function loadInvoices() {
  const res = await fetch('/api/invoices');
  currentInvoices = await res.json();
  const tbody = document.querySelector('#tbl-invoices tbody');
  tbody.innerHTML = '';
  currentInvoices.forEach(i => {
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
      <td style="font-weight: 700; color: ${i.balance_amount > 0 ? 'var(--danger)' : 'var(--success)'};">₹${parseFloat(i.balance_amount).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
      <td><span class="status-badge ${badge}">${i.status}</span></td>
      <td>${i.balance_amount > 0 ? `<button class="btn btn-primary btn-sm" onclick="paySpecificInvoice(${i.id})">Collect</button>` : '✓ Settled'}</td>
    </tr>`;
  });
}

async function loadTerminal() {
  const res = await fetch('/api/invoices?status=UNPAID');
  const unpaid = await res.json();
  const sel = document.getElementById('terminal-invoice-select');
  sel.innerHTML = '<option value="">-- Choose student with pending dues --</option>';
  unpaid.forEach(inv => {
    sel.innerHTML += `<option value="${inv.id}" data-name="${inv.student_name}" data-bal="${inv.balance_amount}">${inv.invoice_number} — ${inv.student_name} (Due: ₹${parseFloat(inv.balance_amount).toLocaleString('en-IN')})</option>`;
  });
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
    alert('Please select an invoice and enter a valid positive payment amount.');
    return;
  }

  const res = await fetch('/api/payments', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      invoice_id: parseInt(invId),
      amount: parseFloat(amount),
      payment_method: method,
      transaction_id: tx,
      cashier_name: 'Counter Cashier'
    })
  });

  const data = await res.json();
  if (res.ok) {
    alert('Payment processed successfully! Receipt: ' + data.receipt.receipt_number);
    window.open('/api/receipts/' + data.receipt.receipt_number + '/html', '_blank');
    loadTerminal();
    loadDashboard();
  } else {
    alert('Payment error: ' + (data.error || 'Unknown failure'));
  }
}

async function loadDefaulters() {
  const res = await fetch('/api/defaulters');
  const list = await res.json();
  const tbody = document.querySelector('#tbl-defaulters tbody');
  tbody.innerHTML = '';
  list.forEach(d => {
    tbody.innerHTML += `<tr>
      <td><strong>${d.invoice_number}</strong></td>
      <td>${d.student_name}</td>
      <td>${d.class_name}</td>
      <td>${d.parent_phone}</td>
      <td>${d.due_date}</td>
      <td><span class="status-badge badge-overdue">${d.days_overdue} days</span></td>
      <td style="font-weight: 700; color: var(--danger);">₹${parseFloat(d.balance_due).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
    </tr>`;
  });
}

async function loadReports() {
  const res = await fetch('/api/reports/collection');
  const data = await res.json();
  const tbody = document.querySelector('#tbl-all-collections tbody');
  tbody.innerHTML = '';
  (data.records || []).forEach(r => {
    tbody.innerHTML += `<tr>
      <td><strong>${r.payment_ref}</strong></td>
      <td>#${r.invoice_id}</td>
      <td>₹${parseFloat(r.amount).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
      <td><span class="status-badge badge-paid">${r.payment_method}</span></td>
      <td>${r.transaction_id || 'CASH-COUNTER'}</td>
      <td>${r.payment_date}</td>
      <td>${r.cashier_name}</td>
    </tr>`;
  });
}

function paySpecificInvoice(invId) {
  switchTab('terminal');
  const sel = document.getElementById('terminal-invoice-select');
  sel.value = invId;
  terminalInvoiceChanged();
}

async function generateInvoiceForStudent(studentId) {
  if (!confirm('Generate Term-1 2026-2027 invoice for student ' + studentId + '?')) return;
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
    alert('Invoice issued: ' + data.invoice_number);
    loadStudents();
  } else {
    alert('Error: ' + data.error);
  }
}

function openPaymentModal() {
  switchTab('terminal');
}

async function openStudentModal() {
  const res = await fetch('/api/classes');
  const classes = await res.json();
  const sel = document.getElementById('stu-class');
  sel.innerHTML = '';
  classes.forEach(c => sel.innerHTML += `<option value="${c.id}">${c.name}</option>`);
  document.getElementById('modal-student').style.display = 'flex';
}

function closeModals() {
  document.querySelectorAll('.modal-overlay').forEach(m => m.style.display = 'none');
}

async function submitStudent() {
  const payload = {
    student_id: document.getElementById('stu-id').value,
    first_name: document.getElementById('stu-first').value,
    last_name: document.getElementById('stu-last').value,
    class_id: parseInt(document.getElementById('stu-class').value),
    parent_name: document.getElementById('stu-parent').value,
    parent_email: document.getElementById('stu-email').value,
    parent_phone: document.getElementById('stu-phone').value,
    is_transport_enrolled: document.getElementById('stu-transport').checked,
    is_hostel_enrolled: document.getElementById('stu-hostel').checked
  };

  const res = await fetch('/api/students', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (res.ok) {
    closeModals();
    loadStudents();
    loadDashboard();
  } else {
    const err = await res.json();
    alert('Failed to save student: ' + err.error);
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


def run_server(host: str = "127.0.0.1", port: int = 8000, db_path: Optional[str] = None) -> None:
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
