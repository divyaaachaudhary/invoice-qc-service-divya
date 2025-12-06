from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
import os
import tempfile
import shutil

from validator import InvoiceValidator
from extractor import InvoiceExtractor

app = FastAPI(
    title="Invoice QC Service",
    description="API for validating and extracting invoice data",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------
# 1. Health Check
# ------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# ------------------------------
# 2. Validate JSON (required)
# ------------------------------
@app.post("/validate-json")
def validate_json(invoices: List[dict]):
    """
    Accepts a list of invoices in JSON format and returns
    validation results + summary.
    """
    validator = InvoiceValidator()
    results = validator.validate_invoices(invoices)
    return results


# ----------------------------------------------
# 3. Extract + Validate PDFs (optional bonus)
# ----------------------------------------------
@app.post("/extract-and-validate-pdfs")
async def extract_and_validate_pdfs(files: List[UploadFile] = File(...)):
    """
    Accept multiple PDF uploads, extract invoice data,
    validate them, and return results.
    """
    try:
        extractor = InvoiceExtractor()
        validator = InvoiceValidator()

        extracted_data = []
        
        for file in files:
            tmp_path = None
            try:
                # Save uploaded file to a temp location
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    shutil.copyfileobj(file.file, tmp)
                    tmp_path = tmp.name

                # Extract invoice info
                data = extractor.extract_from_pdf(tmp_path)
                
                # Check if extraction returned valid data (at least some fields)
                if data and isinstance(data, dict):
                    # Save raw_text sample for debugging (first 1000 chars)
                    raw_text_sample = data.get("raw_text", "")[:1000] if data.get("raw_text") else None
                    # Remove raw_text from data before validation (too large)
                    data.pop("raw_text", None)
                    if raw_text_sample:
                        data["_debug_text_sample"] = raw_text_sample
                    extracted_data.append(data)
                else:
                    extracted_data.append({
                        "error": f"Extraction returned empty or invalid data for {file.filename}"
                    })
            except Exception as e:
                import traceback
                error_msg = f"Failed to extract from {file.filename}: {str(e)}"
                extracted_data.append({
                    "error": error_msg,
                    "traceback": traceback.format_exc()
                })
            finally:
                # Clean up temporary file
                if tmp_path:
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass

        # Validate extracted invoices (only validate successfully extracted ones)
        # Filter out items with "error" key
        valid_extracted = [data for data in extracted_data if "error" not in data and data]
        
        if valid_extracted:
            results = validator.validate_invoices(valid_extracted)
        else:
            # If no valid extractions, still return structure with error info
            results = {
                "invoices": [],
                "summary": {
                    "total_invoices": 0,
                    "valid_invoices": 0,
                    "invalid_invoices": 0,
                    "error_counts": {}
                }
            }
            
            # Add error information if all extractions failed
            if extracted_data and all("error" in data for data in extracted_data):
                results["extraction_errors"] = [data.get("error", "Unknown error") for data in extracted_data]

        # For debugging: include raw text from first successful extraction
        debug_info = {}
        if extracted_data and "error" not in extracted_data[0]:
            # Get a sample of the text (first 500 chars) for debugging
            if "raw_text" in extracted_data[0]:
                debug_info["sample_text"] = extracted_data[0]["raw_text"][:500]
        
        return {
            "extracted": extracted_data,
            "validation": results,
            "debug": debug_info if debug_info else None
        }
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
