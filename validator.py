from typing import List, Dict, Any, Tuple
from datetime import datetime
import re


class InvoiceValidator:

    def __init__(self):
        pass

    def validate_invoices(self, invoices: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = []
        error_counts = {}
        seen_combinations = set()  # For duplicate detection

        for inv in invoices:
            invoice_result = self.validate_single(inv, seen_combinations)
            results.append(invoice_result)

            # Count errors for summary
            for err in invoice_result["errors"]:
                error_counts[err] = error_counts.get(err, 0) + 1

        summary = {
            "total_invoices": len(invoices),
            "valid_invoices": sum(1 for r in results if r["is_valid"]),
            "invalid_invoices": sum(1 for r in results if not r["is_valid"]),
            "error_counts": error_counts
        }

        return {
            "invoices": results,
            "summary": summary
        }

    def validate_single(self, inv: Dict[str, Any], seen_combinations: set = None) -> Dict[str, Any]:
        errors = []

        # Run sets of rules
        errors += self.check_completeness(inv)
        errors += self.check_format(inv)
        errors += self.check_business_rules(inv)
        errors += self.check_anomaly_rules(inv)
        
        # Check for duplicates (order_number + invoice_date)
        if seen_combinations is not None:
            order_number = inv.get("order_number")
            invoice_date = inv.get("invoice_date")
            if order_number and invoice_date:
                combo = f"{order_number}|{invoice_date}"
                if combo in seen_combinations:
                    errors.append("anomaly: duplicate_invoice")
                else:
                    seen_combinations.add(combo)

        return {
            "invoice_id": inv.get("invoice_number") or inv.get("order_number") or "UNKNOWN",
            "is_valid": len(errors) == 0,
            "errors": errors
        }

    def check_completeness(self, inv):
        errors = []

        required_fields = [
            "order_number",
            "invoice_date",
            "seller_name",
            "buyer_name",
            "net_total",
            "tax_amount",
            "gross_total"
        ]

        for field in required_fields:
            if not inv.get(field):
                errors.append(f"missing_field: {field}")

        # At least 1 line item
        line_items = inv.get("line_items")
        if not line_items or (isinstance(line_items, list) and len(line_items) == 0):
            errors.append("missing_field: line_items")

        return errors
    def check_format(self, inv):
        errors = []

        # Currency must be EUR
        currency = inv.get("currency")
        if currency != "EUR":
            errors.append("invalid_currency: must be EUR")

        # Invoice date must be a valid date
        invoice_date = inv.get("invoice_date")
        if invoice_date:
            try:
                # Try to parse DD.MM.YYYY format
                datetime.strptime(invoice_date, "%d.%m.%Y")
            except (ValueError, TypeError):
                errors.append("invalid_date_format: invoice_date must be DD.MM.YYYY")

        # Number validations
        for key in ["net_total", "tax_amount", "gross_total"]:
            value = inv.get(key)
            if value is None:
                continue
            try:
                float(value)
            except (ValueError, TypeError):
                errors.append(f"invalid_number: {key}")

        # Tax amount must be >= 0
        tax_amount = inv.get("tax_amount")
        if tax_amount is not None:
            try:
                if float(tax_amount) < 0:
                    errors.append("invalid_tax_amount: tax_amount must be >= 0")
            except (ValueError, TypeError):
                pass  # Already caught by invalid_number check above

        return errors
    def check_business_rules(self, inv):
        errors = []

        net = inv.get("net_total")
        tax = inv.get("tax_amount")
        gross = inv.get("gross_total")

        # Rule: gross_total = net_total + tax_amount
        if all(v is not None for v in [net, tax, gross]):
            if round(float(net) + float(tax), 2) != round(float(gross), 2):
                errors.append("business_rule_failed: totals_mismatch")

        # Rule: line item totals must sum = net total
        line_items = inv.get("line_items", [])
        if line_items and net is not None:
            # Only sum items that have line_total
            line_totals = [item.get("line_total") for item in line_items if item.get("line_total") is not None]
            if line_totals:
                sum_lines = round(sum(float(t) for t in line_totals), 2)
                if sum_lines != round(float(net), 2):
                    errors.append("business_rule_failed: line_items_net_mismatch")

        # Rule: quantity * unit_price = line_total
        for item in line_items:
            q = item.get("quantity")
            u = item.get("unit_price")
            t = item.get("line_total")
            
            # Skip if any required field is missing
            if q is None or u is None or t is None:
                continue

            if round(float(q) * float(u), 2) != round(float(t), 2):
                errors.append("business_rule_failed: line_total_calculation_error")
                break

        # Rule: delivery_date >= invoice_date OR delivery_date = "sofort"
        delivery_date = inv.get("delivery_date")
        invoice_date = inv.get("invoice_date")
        if delivery_date and invoice_date:
            if delivery_date.lower() != "sofort":
                try:
                    inv_dt = datetime.strptime(invoice_date, "%d.%m.%Y")
                    del_dt = datetime.strptime(delivery_date, "%d.%m.%Y")
                    if del_dt < inv_dt:
                        errors.append("business_rule_failed: delivery_date_before_invoice_date")
                except (ValueError, TypeError):
                    # If dates can't be parsed, skip this check (format errors handled elsewhere)
                    pass

        return errors

    def check_anomaly_rules(self, inv):
        errors = []

        # Negative totals
        net_total = inv.get("net_total")
        gross_total = inv.get("gross_total")
        
        if net_total is not None and float(net_total) < 0:
            errors.append("anomaly: negative_net_total")

        if gross_total is not None and float(gross_total) < 0:
            errors.append("anomaly: negative_gross_total")

        # Discount validation in payment_terms
        payment_terms = inv.get("payment_terms", "")
        if payment_terms and "skonto" in payment_terms.lower():
            # Extract percentage from payment terms (e.g., "2,0% Skonto")
            skonto_match = re.search(r"(\d+[,\.]\d+)\s*%", payment_terms, re.IGNORECASE)
            if skonto_match:
                try:
                    percentage = float(skonto_match.group(1).replace(",", "."))
                    if percentage > 100:
                        errors.append("anomaly: discount_percentage_exceeds_100")
                except (ValueError, TypeError):
                    errors.append("anomaly: invalid_discount_format")

        return errors
