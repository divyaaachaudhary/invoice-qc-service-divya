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

invoice-project/
│
│── extractor.py        # PDF → JSON
│── validator.py        # Apply rules
│── cli.py              # CLI interface
│── api.py              # FastAPI service
│
├── frontend/                 # React UI
│     ├── src/
│     ├── package.json
│     └── ...
├── README.md



---

# 4. Extraction Pipeline

### -Libraries used: `pdfplumber`

### ✔ Steps:
1. Load PDF pages  
2. Extract entire text  
3. Use regex patterns to match fields  
   - Invoice No → `(Invoice\s*(No|Number|#)[:]?\s*(\S+))`  
   - Dates → `\d{2}[./-]\d{2}[./-]\d{4}`  
4. Table-like parsing for line items  
5. Return JSON with missing fields marked `null`  

### -Output Example
```json
<img width="758" height="592" alt="image" src="https://github.com/user-attachments/assets/d06c4e7d-971f-4ea5-85df-a2e1451745ab" />

# 5. Validation Engine



