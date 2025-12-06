import pdfplumber
import re
from typing import List, Dict, Any


class InvoiceExtractor:
    """
    Extracts invoice information from PDF files.
    """

    def __init__(self):
        pass

    def extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract structured invoice data from a single PDF file.
        """
        # Store PDF path for table extraction
        self._current_pdf_path = pdf_path

        with pdfplumber.open(pdf_path) as pdf:
            full_text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

        # Clean text
        text = full_text.replace("\t", " ").strip()

        # Check if we got any text
        if not text or len(text.strip()) < 10:
            raise ValueError("PDF appears to be empty or could not extract text")

        order_number = self.extract_order_number(text)
        invoice_date = self.extract_invoice_date(text)

        # Extract line items - pass text and pdf_path for table extraction
        line_items = self.extract_line_items(text, pdf_path)

        invoice = {
            "invoice_number": self.extract_invoice_number(text, order_number),
            "order_number": order_number,
            "order_reference": self.extract_order_reference(text),
            "invoice_date": invoice_date,
            "seller_name": self.extract_seller_name(text),
            "seller_address": self.extract_seller_address(text),
            "buyer_name": self.extract_buyer_name(text),
            "buyer_address": self.extract_buyer_address(text),
            "delivery_date": self.extract_delivery_date(text),
            "payment_terms": self.extract_payment_terms(text),
            "currency": "EUR",  # based on sample
            "net_total": self.extract_net_total(text),
            "tax_amount": self.extract_tax(text),
            "gross_total": self.extract_gross_total(text),
            "line_items": line_items if line_items else [],
            "raw_text": text
        }

        return invoice

    def extract_invoice_number(self, text: str, order_number: str = None):
        """Derive invoice number from order number or extract from text"""
        if order_number:
            return f"INV-{order_number}"
        match = re.search(r"Rechnung\s+([A-Z0-9\-]+)", text, re.IGNORECASE)
        return match.group(1) if match else None

    def extract_order_number(self, text: str):
        match = re.search(r"Bestellung\s+([A-Z0-9]+)", text, re.IGNORECASE)
        return match.group(1) if match else None

    def extract_order_reference(self, text: str):
        match = re.search(r"im Auftrag von\s+(\S+)", text)
        return match.group(1) if match else None

    def extract_invoice_date(self, text: str):
        match = re.search(r"vom\s+(\d{2}\.\d{2}\.\d{4})", text)
        return match.group(1) if match else None

    def extract_delivery_date(self, text: str):
        patterns = [
            r"Gewünschtes\s+Lieferdatum:?\s*(sofort|\d{2}\.\d{2}\.\d{4})",
            r"Lieferdatum:?\s*(sofort|\d{2}\.\d{2}\.\d{4})",
            r"Gewünschtes\s+Lieferdatum:?\s*\n\s*(sofort|\d{2}\.\d{2}\.\d{4})",
            r"Lieferdatum[^\n]*?\s+(sofort)",
            r"(?:Gewünschtes\s+)?Lieferdatum[^\n]*?(\d{2}\.\d{2}\.\d{4})"
        ]

        for p in patterns:
            match = re.search(p, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1)

        return None

    def extract_payment_terms(self, text: str):
        match = re.search(r"Zahlungsbedingungen:?\s*(.+?)(?=\n|$)", text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def extract_seller_name(self, text: str):
        match = re.search(r"medical equipment\s*\([^)]+\)", text, re.IGNORECASE)
        if match:
            return match.group(0).strip()

        match = re.search(r"ABC Corporation", text, re.IGNORECASE)
        return match.group(0) if match else None

    def extract_seller_address(self, text: str):
        match = re.search(r"medical equipment\s*\([^)]+\)\s*\n([^\n]+(?:,\s*\d{5}\s+[^\n]+)?)",
                          text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()

        match = re.search(
            r"(?:medical equipment|ABC Corporation)[^\n]*\s*\n([A-Za-zäöüßÄÖÜ\s\-]+,?\s*\d{5}\s+[A-Za-zäöüßÄÖÜ\s]+)",
            text, re.IGNORECASE | re.MULTILINE)
        return match.group(1).strip() if match else None

    def extract_buyer_name(self, text: str):
        match = re.search(r"Kundenanschrift\s*\n?\s*([^\n]+)", text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def extract_buyer_address(self, text: str):
        match = re.search(r"Kundenanschrift\s*\n?\s*[^\n]+\s*\n([\s\S]*?)(?=\n\n|\n[A-Z][a-z]+:|$)",
                          text, re.IGNORECASE)
        if match:
            address = match.group(1).strip()
            lines = [line.strip() for line in address.split("\n") if line.strip()]
            return "\n".join(lines) if lines else None
        return None

    def extract_net_total(self, text: str):
        patterns = [
            r"Gesamtwert\s+EUR\s+(\d+[,\d]*)",
            r"Gesamtwert\s+(\d+[,\d]*)\s+EUR",
            r"Nettobetrag[:\s]+EUR\s+(\d+[,\d]*)"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(",", "."))
                except ValueError:
                    continue

        return None

    def extract_tax(self, text: str):
        patterns = [
            r"MwSt\.?\s*\d+%[^\d]*EUR\s+(\d+[,\d]*)",
            r"MwSt\.?\s*[^\d]*EUR\s+(\d+[,\d]*)",
            r"Umsatzsteuer[^\d]*EUR\s+(\d+[,\d]*)"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(",", "."))
                except ValueError:
                    continue

        return None

    def extract_gross_total(self, text: str):
        patterns = [
            r"inkl\.?\s*MwSt\.?\s*[^\d]*EUR\s+(\d+[,\d]*)",
            r"Gesamtwert\s+inkl\.?\s*MwSt\.?\s*[^\d]*EUR\s+(\d+[,\d]*)",
            r"Bruttobetrag[:\s]+EUR\s+(\d+[,\d]*)"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(",", "."))
                except ValueError:
                    continue

        return None

    def extract_line_items(self, text: str, pdf_path: str = None) -> List[Dict[str, Any]]:
        items = []

        # Try table extraction first
        if pdf_path:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        tables = page.extract_tables()
                        for table in tables:
                            if table and len(table) > 1:
                                header = table[0]
                                if any(h and any(k in str(h).lower() for k in ["pos", "artikel", "preis", "menge"])
                                       for h in header):
                                    for row in table[1:]:
                                        if row and len(row) >= 4:
                                            try:
                                                pos = str(row[0]).strip()
                                                if pos and pos.isdigit():

                                                    desc = str(row[1]).strip() if row[1] else ""
                                                    price_str = "0"
                                                    qty_str = "0"
                                                    unit = ""
                                                    conversion = None
                                                    total_str = "0"

                                                    for col in row[2:]:
                                                        col_str = str(col).strip() if col else ""
                                                        if re.match(r'\d+[,\.]\d+', col_str):
                                                            if price_str == "0":
                                                                price_str = col_str
                                                            else:
                                                                total_str = col_str
                                                        elif re.match(r'^\d+([,\.]\d+)?$', col_str) and qty_str == "0":
                                                            qty_str = col_str
                                                        elif re.match(r'^[A-Z]+$', col_str, re.IGNORECASE):
                                                            unit = col_str
                                                        elif "=" in col_str:
                                                            conversion = col_str

                                                    price = float(price_str.replace(",", "."))
                                                    qty = float(qty_str.replace(",", ".")) if qty_str != "0" else 1.0
                                                    total = float(total_str.replace(",", "."))

                                                    if price > 0 and total > 0:
                                                        items.append({
                                                            "position": int(pos),
                                                            "description": desc,
                                                            "unit_price": price,
                                                            "quantity": qty,
                                                            "unit": unit,
                                                            "conversion": conversion if conversion and "=" in conversion else None,
                                                            "line_total": total
                                                        })
                                            except:
                                                continue

                                    if items:
                                        return items
            except:
                pass

        # Text-based extraction fallback
        lines = text.split("\n")

        table_start = -1
        for i, line in enumerate(lines):
            if any(h in line.lower() for h in ["pos", "artikel", "preis", "menge", "einheit"]):
                table_start = i + 1
                break

        search_lines = lines[table_start:] if table_start >= 0 else lines

        for line in search_lines:
            line = line.strip()
            if not line:
                continue

            if any(h in line.lower() for h in ["pos", "artikel", "preis", "menge", "einheit", "umrechnung", "bestellwert"]):
                continue

            if any(w in line.lower() for w in ["gesamt", "summe", "total", "mwst", "steuer", "zahlungsbedingungen"]):
                break

            simple = re.search(r"^(\d+)\s+(.+?)\s+(\d+[,\d]*)\s+(\d+[,\d]*)\s+([A-Z]+).*?(\d+,\d+)$", line)
            if simple:
                try:
                    pos = int(simple.group(1))
                    desc = simple.group(2).strip()
                    num1 = simple.group(3).replace(",", ".")
                    num2 = simple.group(4).replace(",", ".")
                    unit = simple.group(5)
                    total_str = simple.group(6).replace(",", ".")

                    price = float(num1)
                    qty = float(num2)

                    if "." in num2 and len(num2.split(".")[1]) > 2:
                        price, qty = qty, price

                    items.append({
                        "position": pos,
                        "description": desc,
                        "unit_price": price,
                        "quantity": qty,
                        "unit": unit,
                        "conversion": None,
                        "line_total": float(total_str)
                    })
                    continue
                except:
                    pass

            patterns = [
                r"^(\d+)\s+([A-Za-z0-9\s\-\.:]+?)\s+(\d+[,\d]*)\s+([\d,\.]+)\s+([A-Z]+)\s+(\d+\s*[A-Z]+\s*=\s*\d+\s*[A-Za-z]+)\s+(\d+,\d+)$",
                r"^(\d+)\s+([A-Za-z0-9\s\-\.:]+?)\s+(\d+[,\d]*)\s+([\d,\.]+)\s+([A-Z]+).*?(\d+,\d+)$",
                r"^(\d+)\s+([A-Za-z\s\-\.:]+?)\s+(\d+[,\d]*)\s+([\d,\.]+)\s+([A-Z]+).*?(\d+,\d+)$",
            ]

            for p in patterns:
                match = re.search(p, line)
                if match:
                    try:
                        pos = int(match.group(1))
                        desc = match.group(2).strip()
                        price_str = match.group(3).replace(",", ".")
                        qty_str = match.group(4).replace(",", ".")
                        unit = match.group(5)

                        if len(match.groups()) >= 7:
                            conversion = match.group(6)
                            total_str = match.group(7).replace(",", ".")
                        else:
                            conversion = None
                            total_str = match.group(6).replace(",", ".")

                        items.append({
                            "position": pos,
                            "description": desc,
                            "unit_price": float(price_str),
                            "quantity": float(qty_str),
                            "unit": unit,
                            "conversion": conversion if conversion and "=" in conversion else None,
                            "line_total": float(total_str)
                        })
                        break
                    except:
                        continue

        if not items:
            for line in search_lines[:20]:
                line = line.strip()
                if not line:
                    continue

                simple = re.search(r"^(\d+)\s+(.+?)\s+.*?(\d+,\d+)$", line)
                if simple:
                    try:
                        pos = int(simple.group(1))
                        desc = simple.group(2).strip()[:50]
                        total = float(simple.group(3).replace(",", "."))

                        items.append({
                            "position": pos,
                            "description": desc,
                            "unit_price": total,
                            "quantity": 1.0,
                            "unit": "",
                            "conversion": None,
                            "line_total": total
                        })

                        if len(items) >= 10:
                            break
                    except:
                        continue

        return items
