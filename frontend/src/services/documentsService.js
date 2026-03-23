import documentService from "./documentService";

const formatSize = (bytes) => {
    if (!bytes) return "0 KB";
    if (typeof bytes === "string") return bytes;
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    return `${(kb / 1024).toFixed(2)} MB`;
};

const normalizeDocument = (doc) => ({
    id: doc.id,
    name: doc.name,
    type: doc.type || "document",
    status: doc.status || "uploaded",
    size: formatSize(doc.size),
    bytes: doc.size || 0,
    uploaded: doc.uploaded || (doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : "N/A"),
    uploaded_at: doc.uploaded_at,
    shipment: doc.shipment || null,
    extractedFields: Object.keys(doc.extracted_data || (doc.ocr || {}).extracted_data || {}).length,
    accuracy: (() => {
        const raw = doc.accuracy ?? (doc.ocr || {}).accuracy ?? 0;
        const numeric = Number(raw);
        return numeric <= 1 ? numeric * 100 : numeric;
    })(),
    processed: doc.processed || (doc.ocr ? "Just now" : "Pending"),
    pages: doc.pages || 1,
    priority: doc.priority || (doc.requires_signature ? "high" : "normal"),
    extracted_data: doc.extracted_data || (doc.ocr || {}).extracted_data || {},
    ocr: doc.ocr || null,
    compliance: doc.compliance || null,
    signature: doc.signature || null,
    requires_signature: Boolean(doc.requires_signature),
});

class DocumentsService {
    async getDashboard() {
        const data = await documentService.getDashboard();
        return {
            stats: data.stats || { total: 0, processed: 0, pending: 0, storage: "0 MB" },
            documents: (data.documents || []).map(normalizeDocument),
            activities: data.activities || [],
            processingQueue: (data.processing_queue || []).map((item) => ({
                ...item,
                name: item.name || item.document,
            })),
        };
    }

    async listDocuments() {
        const data = await documentService.getDocuments(1, 200);
        return (data.documents || []).map(normalizeDocument);
    }

    async getProcessingQueue() {
        const dashboard = await this.getDashboard();
        return dashboard.processingQueue || [];
    }

    async getProcessedDocuments(limit = 20) {
        const data = await documentService.getDocuments(1, 200);
        return (data.documents || [])
            .filter((doc) => Boolean(doc.ocr))
            .slice(0, limit)
            .map(normalizeDocument);
    }

    async triggerQuickAction(actionId) {
        if (actionId === "scan") {
            const data = await documentService.getExpiringDocuments(30);
            return { ok: true, items: data.documents || [] };
        }
        if (actionId === "process") {
            const queue = await this.getProcessingQueue();
            return this.processAll(queue);
        }
        return { ok: true, action: actionId };
    }

    async runCompliance(docIds = []) {
        const results = await Promise.all(docIds.map((id) => documentService.checkCompliance(id)));
        return results || [];
    }

    async processAll(queue = []) {
        const ids = queue.map((item) => item.id);
        const results = await Promise.all(ids.map((id) => documentService.processOCR(id)));
        return { ok: true, results };
    }

    async processSingle(docId) {
        return documentService.processOCR(docId);
    }

    async saveOcrConfig(config) {
        try {
            localStorage.setItem("documents_ocr_config", JSON.stringify(config));
        } catch (_) {
            // Ignore storage failures.
        }
        return { ok: true, config };
    }

    async analyzeContract(docId) {
        return documentService.analyzeContract(docId);
    }

    async signDocument(docId, signerId, signerName = null, signerEmail = null) {
        return documentService.signDocument(docId, signerId, signerName, signerEmail);
    }

    async verifyDocument(docId) {
        return documentService.verifyDocument(docId);
    }
}

export default new DocumentsService();
