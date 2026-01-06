import React, { useState } from "react";
import { uploadPDFs } from "../api";

export default function UploadBox({ setResultData }) {
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    async function handleSubmit() {
        if (selectedFiles.length === 0) {
            alert("Please upload at least one PDF");
            return;
        }

        setIsLoading(true);
        try {
            const result = await uploadPDFs(selectedFiles);
            setResultData(result);
        } catch (error) {
            alert("Error uploading files: " + error.message);
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <div className="upload-box">
            <h2>Upload Invoice PDFs</h2>
            <input
                type="file"
                multiple
                accept="application/pdf"
                onChange={(e) => setSelectedFiles(Array.from(e.target.files || []))}
            />
            <button onClick={handleSubmit} disabled={isLoading}>
                {isLoading ? "Uploading..." : "Submit"}
            </button>
        </div>
    );
}
