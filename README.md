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
