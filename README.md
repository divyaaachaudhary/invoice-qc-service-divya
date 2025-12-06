# Invoice QC Service – Divya

A complete end-to-end **Invoice Extraction & Quality Control System**, designed as part of the Software Engineer Intern (Data & Development) assignment.

This project processes invoice PDFs, extracts structured fields, validates them against business rules, and exposes both CLI and HTTP API interfaces.  
A React-based frontend UI is also included for internal QC workflows.

---

# 1. Overview

This system provides:

### -PDF → Structured JSON Extraction  
Using **pdfplumber** and rule-based parsing.

### -Validation Engine  
Schema checks + business rules + anomaly detection.

### -CLI Tool  
Run:  
- extraction only  
- validation only  
- full pipeline

### -FastAPI Backend  
Endpoints for validation, extraction, and health checks.

### -React Frontend (Bonus)  
A clean UI where users can upload PDFs and view:  
- Extracted invoice data  
- JSON output  
- Valid/Invalid status  
- Errors per invoice  

### -Designed for integration into larger document pipelines.

---

# 2. Schema & Validation Design

## **2.1 Invoice Schema**
| Field | Description |
|-------|-------------|
| `invoice_id` | Unique identifier extracted from PDF |
| `invoice_number` | Reference number of invoice |
| `invoice_date` | Issue date |
| `due_date` | Payment due date |
| `seller_name` | Seller company name |
| `buyer_name` | Buyer company name |
| `seller_address` | Seller address |
| `buyer_address` | Buyer address |
| `currency` | Currency symbol (INR/EUR/USD etc.) |
| `net_total` | Sum before tax |
| `tax_amount` | Tax applied |
| `gross_total` | Final payable amount |
| `line_items` | List of product/service entries |

### **Line Item Fields**
- `description`
- `quantity`
- `unit_price`
- `line_total`

---

# 2.2 Validation Rules

### -**Completeness Rules**
1. `invoice_number` must not be empty.  
2. `invoice_date` must be parseable as a valid date.  
3. `seller_name` and `buyer_name` must be present.

### -**Format Rules**
4. `currency` must be one of: `["INR", "USD", "EUR"]`.  
5. Amount fields must be numeric and non-negative.

### -**Business Rules**
6. `net_total + tax_amount` ≈ `gross_total` (tolerance: ±0.1).  
7. Sum of line item totals ≈ net_total.  

### -**Anomaly Rules**
8. Duplicate invoice check: `(invoice_number + seller_name + date)`  
9. Totals cannot be negative.

Each rule produces clear error messages like:

- `missing_field: buyer_name`  
- `business_rule_failed: totals_mismatch`

---

# 3. Architecture

PDFs → Extraction Module → invoice.json → Validation Module → Results → CLI/API/UI

 3.1 Folder Structure

 
 <img width="330" height="373" alt="Image" src="https://github.com/user-attachments/assets/d0dfc480-1b71-4697-b8c2-df0ea3d1d234" />

 ---

### 3.2 Component Breakdown

#### **1. Extraction Pipeline (PDF → JSON)**
**Location:** `invoice_qc/extractor.py`

Handles:
- Reading PDF files using `pdfplumber`
- Extracting full text from all pages
- Identifying fields using regex + text heuristics:
  - invoice number  
  - dates  
  - seller/buyer details  
  - totals  
- Parsing table-like sections for line items
- Normalizing dates and numeric fields
- Producing a clean structured invoice object

If a field is missing, it is set to `null` and validated later.

---

#### **2. Validation Core (JSON → QC Results)**
**Location:** `invoice_qc/validator.py`

Responsibilities:
- Schema completeness checks (invoice number, dates, names)
- Format validation (date parsing, numeric fields)
- Business rules:
  - `net_total + tax_amount ≈ gross_total`
  - Sum of line items ≈ net total
- Anomaly detection:
  - duplicates  
  - negative totals  
- Produces:
  - per-invoice validation result
  - aggregated summary with error counts

---

#### **3. CLI Tool**
**Location:** `invoice_qc/cli.py`

Provides a command-line interface to run the system:

- `extract` → PDFs → JSON
- `validate` → JSON → report
- `full-run` → end-to-end extraction + validation

Features:
- Argument parsing with `argparse`
- Human-readable summary output
- Ability to save JSON and report files
- Non-zero exit code for invalid invoices (pipeline-friendly)

---

#### **4. FastAPI Backend**
**Location:** `invoice_qc/api.py`

Exposes endpoints:

| Method | Route | Description |
|--------|--------|-------------|
| GET | `/health` | Health check |
| POST | `/validate-json` | Validate invoice JSON payload |
| POST | `/extract-and-validate-pdfs` | Upload PDFs → extract → validate |

Used by:
- frontend UI  
- external services  
- automated document pipelines  

---

#### **5. React Frontend (Bonus)**
**Location:** `frontend/`

A lightweight QC console that allows users to:

- Upload PDFs  
- Call backend to extract + validate  
- Display:
  - invoice fields  
  - raw JSON extraction  
  - valid/invalid status  
  - error messages  

Components:
- `UploadBox` — File upload + submit button  
- `InvoiceCard` — Shows invoice + validation results  

---

### 3.3 Data Flow (ASCII Diagram)

      ┌──────────────────┐
      │      PDFs        │
      └────────┬─────────┘
               │
               ▼
    ┌────────────────────────┐
    │   Extraction Module     │
    │  (pdfplumber + regex)   │
    └─────────┬──────────────┘
              │ JSON Output
              ▼
    ┌────────────────────────┐
    │     Validation Core     │
    │ (schema + rules engine) │
    └─────────┬──────────────┘
              │ QC Results

---

## 4. Setup & Installation

This section explains how to set up the complete system, including the Python backend, FastAPI server, CLI tools, and React frontend.

---

### 4.1 Requirements

- **Python 3.10+** (tested on Python 3.11 / 3.12 / 3.13)
- **Node.js 18+** (for the React frontend)
- Git

---

## 4.2 Setup-

```bash
git clone https://github.com/<your-username>/invoice-qc-service.git
cd invoice-qc-service
python -m venv venv
pip install -r requirements.txt
python api.py
cd frontend
npm install
npm run dev
```
The frontend will start at:

 -http://localhost:5173

Make sure the FastAPI server is running at:

-http://127.0.0.1:8000

---
## AI Usage Notes

I used AI tools (ChatGPT, GitHub Copilot, and Cursor) during development to accelerate parts of the project.  
Below is a clear summary of how AI supported the workflow.

### -Tools Used
- **ChatGPT** – for architecture guidance, regex suggestions, FastAPI scaffolding, and improving documentation.
- **GitHub Copilot** – for inline code suggestions while writing Python and JavaScript.
- **Cursor** – for refactoring, auto-completing repetitive code blocks, and quickly navigating large files.

### -Parts Where AI Helped
- Designing initial folder structure and project layout.
- Generating early regex patterns for invoice number, dates, totals, etc.
- Drafting the CLI skeleton using `argparse`.
- Creating initial FastAPI endpoint structure and request/response formats.
- Guiding the React component layout (UploadBox, InvoiceCard, JSON viewer).
- Summarizing documentation and writing parts of the README quickly.
- Suggesting validation rules and business logic ideas.

---
## Assumptions & Limitations

### -Assumptions
- PDFs are **text-based** (not scanned images). OCR was intentionally not implemented due to time constraints.
- Invoice layout follows a **semi-structured format** with identifiable labels (e.g., “Invoice No”, “Total”, “Date”).
- Currency is limited to a known set such as **INR, USD, EUR**.
- Dates in invoices use common formats like `DD-MM-YYYY`, `DD/MM/YYYY`, or `YYYY-MM-DD`.
- Line items appear in a **table-like format**, one per line.
- The extraction logic focuses on the provided sample invoices and similar formats.



