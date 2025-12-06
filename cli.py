import json
import typer
from pathlib import Path

from extractor import InvoiceExtractor
from validator import InvoiceValidator

app = typer.Typer(help="Invoice Extraction & Validation CLI Tool")


# ------------------------------
# Command: extract
# ------------------------------
@app.command()
def extract(
    pdf_dir: str = typer.Option(..., help="Directory containing PDF invoices"),
    output: str = typer.Option("extracted_invoices.json", help="Where to save extracted JSON"),
):
    """
    Extract invoice data from all PDFs in a folder.
    """
    extractor = InvoiceExtractor()
    pdf_dir_path = Path(pdf_dir)

    if not pdf_dir_path.exists():
        typer.echo(f"❌ PDF directory not found: {pdf_dir}")
        raise typer.Exit(code=1)

    all_data = []

    typer.echo(f"🔍 Extracting invoices from: {pdf_dir}")

    for pdf in pdf_dir_path.glob("*.pdf"):
        try:
            typer.echo(f"📄 Processing: {pdf.name}")
            data = extractor.extract_from_pdf(str(pdf))
            all_data.append(data)
        except Exception as e:
            typer.echo(f"⚠️ Failed to extract {pdf.name}: {e}")

    # Save output JSON
    with open(output, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4)

    typer.echo(f"✅ Extraction complete. Saved to: {output}")


# ------------------------------
# Command: validate
# ------------------------------
@app.command()
def validate(
    input: str = typer.Option(..., help="Input JSON with extracted invoices"),
    report: str = typer.Option("validation_report.json", help="Output validation report file"),
):
    """
    Validate invoices from extracted JSON.
    """

    validator = InvoiceValidator()

    typer.echo("🔍 Validating invoices...")

    with open(input, "r", encoding="utf-8") as f:
        invoices = json.load(f)

    results = validator.validate_invoices(invoices)

    with open(report, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    typer.echo(f"✅ Validation complete. Report saved to: {report}")

    # Human summary
    summary = results["summary"]
    typer.echo(f"\n📊 Summary:")
    typer.echo(f"   Total invoices : {summary['total_invoices']}")
    typer.echo(f"   Valid invoices : {summary['valid_invoices']}")
    typer.echo(f"   Invalid invoices : {summary['invalid_invoices']}")


# ------------------------------
# Command: full-run (extract + validate)
# ------------------------------
@app.command()
def full_run(
    pdf_dir: str = typer.Option(..., help="Directory containing PDF invoices"),
    report: str = typer.Option("validation_report.json", help="Final validation report"),
):
    """
    End-to-end: Extract + Validate
    """
    extractor = InvoiceExtractor()
    validator = InvoiceValidator()

    pdf_dir_path = Path(pdf_dir)

    if not pdf_dir_path.exists():
        typer.echo(f"❌ PDF directory not found: {pdf_dir}")
        raise typer.Exit(code=1)

    all_data = []

    typer.echo(f"🚀 Running full extraction + validation pipeline")

    for pdf in pdf_dir_path.glob("*.pdf"):
        try:
            typer.echo(f"📄 Extracting: {pdf.name}")
            data = extractor.extract_from_pdf(str(pdf))
            all_data.append(data)
        except Exception as e:
            typer.echo(f"⚠️ Failed to extract {pdf.name}: {e}")

    results = validator.validate_invoices(all_data)

    with open(report, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    typer.echo(f"📊 Summary:")
    summary = results["summary"]
    typer.echo(f"   Total invoices : {summary['total_invoices']}")
    typer.echo(f"   Valid invoices : {summary['valid_invoices']}")
    typer.echo(f"   Invalid invoices : {summary['invalid_invoices']}")


# ------------------------------
# Entry point
# ------------------------------
if __name__ == "__main__":
    app()
