import React, { useState } from "react";
import UploadBox from "./components/UploadBox";
import InvoiceCard from "./components/InvoiceCard";

function App() {
  const [resultData, setResultData] = useState(null);

  return (
    <div className="container">
      <h1>Invoice QC Console</h1>

      <UploadBox setResultData={setResultData} />

      {resultData && (
        <>
          {/* Show extraction errors if any */}
          {resultData.extracted && resultData.extracted.some(item => item.error) && (
            <>
              <h2>Extraction Errors</h2>
              <div className="error-box">
                {resultData.extracted
                  .filter(item => item.error)
                  .map((item, idx) => (
                    <p key={idx} className="error-message">
                      {item.error}
                    </p>
                  ))}
              </div>
            </>
          )}

          <div className="summary-card">
            <div className="summary-item">
              <strong>{resultData.validation.summary.total_invoices}</strong>
              <span>Total Invoices</span>
            </div>
            <div className="summary-item">
              <strong style={{color: '#22543d'}}>{resultData.validation.summary.valid_invoices}</strong>
              <span>Valid Invoices</span>
            </div>
            <div className="summary-item">
              <strong style={{color: '#742a2a'}}>{resultData.validation.summary.invalid_invoices}</strong>
              <span>Invalid Invoices</span>
            </div>
          </div>

          {resultData.validation.extraction_errors && (
            <div className="error-box">
              <p><strong>All extractions failed:</strong></p>
              {resultData.validation.extraction_errors.map((err, idx) => (
                <p key={idx} className="error-message">{err}</p>
              ))}
            </div>
          )}

          {/* Show extracted data info for debugging */}
          {resultData.extracted && resultData.extracted[0] && !resultData.extracted[0].error && (
            <div className="extraction-details">
              <h3>📋 Extraction Details</h3>
              
              <div className="extraction-grid">
                <div>
                  <h4>Invoice Fields</h4>
                  <table>
                    <tbody>
                      <tr><td><strong>Invoice Number:</strong></td><td>{resultData.extracted[0].invoice_number || <span className="field-missing">❌ Missing</span>}</td></tr>
                      <tr><td><strong>Order Number:</strong></td><td>{resultData.extracted[0].order_number || <span className="field-missing">❌ Missing</span>}</td></tr>
                      <tr><td><strong>Order Reference:</strong></td><td>{resultData.extracted[0].order_reference || <span className="field-optional">⚠️ Not found</span>}</td></tr>
                      <tr><td><strong>Invoice Date:</strong></td><td>{resultData.extracted[0].invoice_date || <span className="field-missing">❌ Missing</span>}</td></tr>
                      <tr><td><strong>Seller Name:</strong></td><td>{resultData.extracted[0].seller_name || <span className="field-missing">❌ Missing</span>}</td></tr>
                      <tr><td><strong>Seller Address:</strong></td><td>{resultData.extracted[0].seller_address || <span className="field-optional">⚠️ Not found</span>}</td></tr>
                      <tr><td><strong>Buyer Name:</strong></td><td>{resultData.extracted[0].buyer_name || <span className="field-missing">❌ Missing</span>}</td></tr>
                      <tr><td><strong>Buyer Address:</strong></td><td>{resultData.extracted[0].buyer_address || <span className="field-optional">⚠️ Not found</span>}</td></tr>
                      <tr><td><strong>Delivery Date:</strong></td><td>{resultData.extracted[0].delivery_date || <span className="field-optional">⚠️ Not found</span>}</td></tr>
                      <tr><td><strong>Payment Terms:</strong></td><td>{resultData.extracted[0].payment_terms || <span className="field-optional">⚠️ Not found</span>}</td></tr>
                      <tr><td><strong>Currency:</strong></td><td>{resultData.extracted[0].currency || <span className="field-optional">⚠️ Not found</span>}</td></tr>
                    </tbody>
                  </table>
                </div>
                
                <div>
                  <h4>Financial Fields</h4>
                  <table>
                    <tbody>
                      <tr><td><strong>Net Total:</strong></td><td>{resultData.extracted[0].net_total !== null && resultData.extracted[0].net_total !== undefined ? <span className="field-found">€{resultData.extracted[0].net_total}</span> : <span className="field-missing">❌ Missing</span>}</td></tr>
                      <tr><td><strong>Tax Amount:</strong></td><td>{resultData.extracted[0].tax_amount !== null && resultData.extracted[0].tax_amount !== undefined ? <span className="field-found">€{resultData.extracted[0].tax_amount}</span> : <span className="field-missing">❌ Missing</span>}</td></tr>
                      <tr><td><strong>Gross Total:</strong></td><td>{resultData.extracted[0].gross_total !== null && resultData.extracted[0].gross_total !== undefined ? <span className="field-found">€{resultData.extracted[0].gross_total}</span> : <span className="field-missing">❌ Missing</span>}</td></tr>
                      <tr><td><strong>Line Items:</strong></td><td>
                        {resultData.extracted[0].line_items?.length > 0 ? (
                          <span className="field-found">✅ {resultData.extracted[0].line_items.length} item(s)</span>
                        ) : (
                          <span className="field-missing">❌ 0 items (Required)</span>
                        )}
                      </td></tr>
                    </tbody>
                  </table>
                  
                  {resultData.extracted[0].line_items && resultData.extracted[0].line_items.length > 0 && (
                    <details>
                      <summary>View Line Items ({resultData.extracted[0].line_items.length})</summary>
                      <div className="line-items-list">
                        {resultData.extracted[0].line_items.map((item, idx) => (
                          <div key={idx} className="line-item">
                            <strong>#{item.position}</strong> {item.description} - 
                            Qty: {item.quantity} {item.unit} - 
                            Price: €{item.unit_price} - 
                            Total: €{item.line_total}
                            {item.conversion && <span className="conversion"> ({item.conversion})</span>}
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              </div>
              
              {resultData.extracted[0]._debug_text_sample && (
                <details>
                  <summary>🔍 Show PDF Text Sample (for debugging extraction patterns)</summary>
                  <pre>
                    {resultData.extracted[0]._debug_text_sample}
                  </pre>
                </details>
              )}
              
              <details>
                <summary>📄 Show Full Extracted Data (JSON)</summary>
                <pre>
                  {JSON.stringify(resultData.extracted[0], null, 2)}
                </pre>
              </details>
            </div>
          )}

          <h2>Invoices</h2>

          {resultData.validation.invoices && resultData.validation.invoices.length > 0 ? (
            resultData.validation.invoices.map((inv, idx) => (
              <InvoiceCard key={idx} invoice={inv} />
            ))
          ) : (
            <p>No invoices to display</p>
          )}
        </>
      )}
    </div>
  );
}

export default App;
