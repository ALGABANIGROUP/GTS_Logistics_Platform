import { readAuthToken } from "../utils/authStorage";
import { API_BASE_URL } from "../config/env";

const API_ENDPOINT = `${API_BASE_URL}/api/v1/documents`;

const getToken = () => readAuthToken();

const authHeaders = (extra = {}) => ({
    Authorization: `Bearer ${getToken()}`,
    ...extra,
});

const normalizeAccuracy = (value) => {
    const numeric = Number(value ?? 0);
    if (numeric <= 1) return Math.round(numeric * 1000) / 10;
    return Math.round(numeric * 10) / 10;
};

export const documentService = {
    async uploadDocument(file, documentType = "document", metadata = {}) {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("document_type", documentType);
        if (Object.keys(metadata).length > 0) {
            formData.append("metadata", JSON.stringify(metadata));
        }

        const response = await fetch(`${API_ENDPOINT}/upload`, {
            method: "POST",
            body: formData,
            headers: authHeaders(),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || "Upload failed");
        }

        return response.json();
    },

    async uploadDocuments(files, metadata = {}) {
        const formData = new FormData();
        files.forEach((file) => formData.append("files", file));
        if (Object.keys(metadata).length > 0) {
            formData.append("metadata", JSON.stringify(metadata));
        }

        const response = await fetch(`${API_ENDPOINT}/batch/upload`, {
            method: "POST",
            body: formData,
            headers: authHeaders(),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || "Batch upload failed");
        }

        return response.json();
    },

    async getDocuments(page = 1, limit = 50, filters = {}) {
        const params = new URLSearchParams({
            page: String(page),
            limit: String(limit),
            ...Object.fromEntries(
                Object.entries(filters || {}).filter(([, value]) => value !== undefined && value !== null && value !== "")
            ),
        });

        const response = await fetch(`${API_ENDPOINT}/?${params.toString()}`, {
            headers: authHeaders(),
        });

        if (!response.ok) {
            throw new Error("Failed to fetch documents");
        }

        const result = await response.json();
        return {
            documents: result.documents || [],
            total: result.total || 0,
            page: result.page || page,
            limit: result.limit || limit,
        };
    },

    async getDocumentById(id) {
        const response = await fetch(`${API_ENDPOINT}/${id}`, {
            headers: authHeaders(),
        });

        if (!response.ok) {
            throw new Error("Failed to fetch document");
        }

        return response.json();
    },

    async deleteDocument(id) {
        const response = await fetch(`${API_ENDPOINT}/${id}`, {
            method: "DELETE",
            headers: authHeaders(),
        });

        if (!response.ok) {
            throw new Error("Delete failed");
        }

        return response.json();
    },

    async downloadDocument(id) {
        const response = await fetch(`${API_ENDPOINT}/${id}/download`, {
            method: "POST",
            headers: authHeaders(),
        });

        if (!response.ok) {
            throw new Error("Download failed");
        }

        return response.blob();
    },

    async processOCR(documentId, language = "eng") {
        const response = await fetch(`${API_ENDPOINT}/${documentId}/ocr`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...authHeaders(),
            },
            body: JSON.stringify({ language }),
        });

        if (!response.ok) {
            throw new Error("OCR processing failed");
        }

        const result = await response.json();
        return {
            ...result,
            accuracy: normalizeAccuracy(result.accuracy),
        };
    },

    async checkCompliance(documentId) {
        const response = await fetch(`${API_ENDPOINT}/${documentId}/compliance`, {
            method: "POST",
            headers: authHeaders(),
        });

        if (!response.ok) {
            throw new Error("Compliance check failed");
        }

        return response.json();
    },

    async analyzeContract(documentId) {
        const response = await fetch(`${API_ENDPOINT}/${documentId}/analyze-contract`, {
            method: "POST",
            headers: authHeaders(),
        });

        if (!response.ok) {
            throw new Error("Contract analysis failed");
        }

        return response.json();
    },

    async signDocument(documentId, signerId, signerName = null, signerEmail = null) {
        const response = await fetch(`${API_ENDPOINT}/${documentId}/sign`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...authHeaders(),
            },
            body: JSON.stringify({
                signer_id: signerId,
                signer_name: signerName,
                signer_email: signerEmail,
            }),
        });

        if (!response.ok) {
            throw new Error("Document signing failed");
        }

        return response.json();
    },

    async verifyDocument(documentId) {
        const response = await fetch(`${API_ENDPOINT}/${documentId}/verify`, {
            headers: authHeaders(),
        });

        if (!response.ok) {
            throw new Error("Document verification failed");
        }

        return response.json();
    },

    async getDocumentVersions(documentId) {
        const response = await fetch(`${API_ENDPOINT}/${documentId}/versions`, {
            headers: authHeaders(),
        });

        if (!response.ok) {
            throw new Error("Failed to fetch document versions");
        }

        return response.json();
    },

    async getDashboard() {
        const response = await fetch(`${API_ENDPOINT}/dashboard`, {
            headers: authHeaders(),
        });

        if (!response.ok) {
            throw new Error("Failed to fetch dashboard");
        }

        return response.json();
    },

    async getExpiringDocuments(days = 30) {
        const response = await fetch(`${API_ENDPOINT}/expiring?days=${days}`, {
            headers: authHeaders(),
        });

        if (!response.ok) {
            throw new Error("Failed to fetch expiring documents");
        }

        return response.json();
    },

    async searchDocuments(query) {
        const params = new URLSearchParams({ q: query });
        const response = await fetch(`${API_ENDPOINT}/search?${params.toString()}`, {
            headers: authHeaders(),
        });

        if (!response.ok) {
            throw new Error("Search failed");
        }

        return response.json();
    },
};

export default documentService;
