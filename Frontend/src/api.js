// src/api.js
const API_URL = "http://localhost:8000"; // backend running in Docker

// Upload file (PDF or DOCX)
export async function uploadFileAPI(file) {
    try {
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch(`${API_URL}/upload/`, {
            method: "POST",
            body: formData,
        });

        if (!res.ok) throw new Error("Upload failed");
        return await res.json();
    } catch (err) {
        console.error("Upload error:", err);
        return { error: "Upload failed" };
    }
}

// Ask a question
export async function askAPI(query, top_k = 3) {
    try {
        const formData = new FormData();
        formData.append("query", query);
        formData.append("top_k", top_k);

        const res = await fetch(`${API_URL}/ask/`, {
            method: "POST",
            body: formData,
        });

        if (!res.ok) throw new Error("Query failed");
        return await res.json();
    } catch (err) {
        console.error("Ask error:", err);
        return { error: "Query failed" };
    }
}