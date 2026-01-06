export const API_BASE = "http://127.0.0.1:8000";

export async function uploadPDFs(files) {
    const formData = new FormData();
    for (let file of files) {
        formData.append("files", file);
    }

    const response = await fetch(`${API_BASE}/extract-and-validate-pdfs`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
}
