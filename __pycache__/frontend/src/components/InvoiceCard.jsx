import React from "react";

export default function InvoiceCard({ invoice }) {

    return (
        <div className="invoice-card">
            <h3>Invoice: {invoice.invoice_id}</h3>

            <p>
                Status:{" "}
                {invoice.is_valid ? (
                    <span className="valid">VALID</span>
                ) : (
                    <span className="invalid">INVALID</span>
                )}
            </p>

            {invoice.errors.length > 0 ? (
                <ul className="error-list">
                    {invoice.errors.map((err, idx) => (
                        <li key={idx}>{err}</li>
                    ))}
                </ul>
            ) : (
                <p>No errors 🎉</p>
            )}
        </div>
    );
}
