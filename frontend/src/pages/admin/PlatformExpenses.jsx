import { useState, useEffect } from "react";
import axiosClient from "../../api/axiosClient";
import { useCurrencyStore } from "../../stores/useCurrencyStore";

const CATEGORIES = [
    { value: "database", label: "🗄️ Database", color: "bg-blue-500/20 text-blue-300" },
    { value: "hosting", label: "☁️ Hosting", color: "bg-purple-500/20 text-purple-300" },
    { value: "domain", label: "🌐 Domain", color: "bg-green-500/20 text-green-300" },
    { value: "phone", label: "📞 Phone", color: "bg-yellow-500/20 text-yellow-300" },
    { value: "virtual_office", label: "🏢 Virtual Office", color: "bg-pink-500/20 text-pink-300" },
    { value: "api_services", label: "🔌 API Services", color: "bg-indigo-500/20 text-indigo-300" },
    { value: "cloud_storage", label: "💾 Cloud Storage", color: "bg-cyan-500/20 text-cyan-300" },
    { value: "email_service", label: "✉️ Email Service", color: "bg-orange-500/20 text-orange-300" },
    { value: "sms_service", label: "💬 SMS Service", color: "bg-lime-500/20 text-lime-300" },
    { value: "payment_gateway", label: "💳 Payment Gateway", color: "bg-emerald-500/20 text-emerald-300" },
    { value: "monitoring", label: "📊 Monitoring", color: "bg-rose-500/20 text-rose-300" },
    { value: "security", label: "🔒 Security", color: "bg-red-500/20 text-red-300" },
    { value: "backup", label: "💿 Backup", color: "bg-slate-500/20 text-slate-300" },
    { value: "cdn", label: "🚀 CDN", color: "bg-violet-500/20 text-violet-300" },
    { value: "other", label: "📦 Other", color: "bg-gray-500/20 text-gray-300" },
];

const BILLING_FREQUENCIES = [
    { value: "monthly", label: "Monthly" },
    { value: "quarterly", label: "Quarterly" },
    { value: "yearly", label: "Yearly" },
    { value: "one_time", label: "One-Time" },
];


const filterExpenses = (items, category, paid) => {
    let filtered = items || [];
    if (category) {
        filtered = filtered.filter((item) => item.category === category);
    }
    if (paid !== "") {
        const shouldBePaid = paid === "true";
        filtered = filtered.filter((item) => item.is_paid === shouldBePaid);
    }
    return filtered;
};

const isImportedId = (id) => String(id).includes("|");

const computeSummary = (items) => {
    const total = items.reduce((sum, item) => sum + Number(item.amount || 0), 0);
    const paid = items.reduce((sum, item) => sum + (item.is_paid ? Number(item.amount || 0) : 0), 0);
    const pending = total - paid;
    const recurringMonthly = items
        .filter((item) => item.is_recurring && item.billing_frequency === "monthly")
        .reduce((sum, item) => sum + Number(item.amount || 0), 0);

    return {
        total,
        paid,
        pending,
        recurring_monthly: recurringMonthly,
    };
};

export default function PlatformExpenses() {
    const { currency } = useCurrencyStore();
    const [expenses, setExpenses] = useState([]);
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [filterCategory, setFilterCategory] = useState("");
    const [filterPaid, setFilterPaid] = useState("");
    const [uploadingFile, setUploadingFile] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [deletedInvoices, setDeletedInvoices] = useState(() => {
        // Load deleted invoices from localStorage
        try {
            const saved = localStorage.getItem("deleted_invoices");
            return saved ? JSON.parse(saved) : [];
        } catch {
            return [];
        }
    });
    const [selectedIds, setSelectedIds] = useState([]);
    const [feedback, setFeedback] = useState(null);
    const [confirmAction, setConfirmAction] = useState(null);

    const [form, setForm] = useState({
        category: "database",
        service_name: "",
        vendor: "",
        description: "",
        amount: "",
        currency: currency || "USD",
        billing_frequency: "monthly",
        is_recurring: true,
        invoice_number: "",
        invoice_url: "",
        billing_date: new Date().toISOString().split("T")[0],
        due_date: "",
        paid_date: "",
        is_paid: false,
        is_active: true,
        notes: "",
    });

    useEffect(() => {
        fetchExpenses();
        fetchSummary();
    }, [filterCategory, filterPaid, deletedInvoices]);

    useEffect(() => {
        if (!editingId && currency) {
            setForm((prev) => ({ ...prev, currency }));
        }
    }, [currency, editingId]);

    const fetchExpenses = async () => {
        try {
            const res = await axiosClient.get(`/api/v1/platform/expenses`);
            let expenses = res.data || [];

            // Filter out deleted invoices
            expenses = expenses.filter(exp => !deletedInvoices.includes(exp.id));

            // Apply filters locally after fetching
            expenses = filterExpenses(expenses, filterCategory, filterPaid);
            setExpenses(expenses);
        } catch (err) {
            setExpenses([]);
        } finally {
            setLoading(false);
        }
    };

    const fetchSummary = async () => {
        try {
            const res = await axiosClient.get("/api/v1/platform/expenses/summary");
            if (typeof res.data?.total === "number") {
                setSummary(res.data);
                return;
            }

            // Fallback: compute from list payload if provided
            const activeExpenses = (res.data.expenses || []).filter(exp => !deletedInvoices.includes(exp.id));
            setSummary(computeSummary(activeExpenses));
        } catch (err) {
            setSummary(computeSummary([]));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const payload = {
                ...form,
                amount: parseFloat(form.amount),
                billing_date: new Date(form.billing_date).toISOString(),
                due_date: form.due_date ? new Date(form.due_date).toISOString() : null,
                paid_date: form.paid_date ? new Date(form.paid_date).toISOString() : null,
            };

            if (editingId) {
                await axiosClient.put(`/api/v1/platform/expenses/${editingId}`, payload);
            } else {
                await axiosClient.post("/api/v1/platform/expenses", payload);
            }

            resetForm();
            fetchExpenses();
            fetchSummary();
            setFeedback({ type: "success", message: editingId ? "Expense updated successfully." : "Expense created successfully." });
        } catch (err) {
            console.error("Failed to save expense:", err);
            setFeedback({ type: "error", message: "Failed to save expense." });
        }
    };

    const handleEdit = (expense) => {
        // Prevent editing imported invoices
        if (isImportedId(expense.id)) {
            setFeedback({
                type: "info",
                message: "Imported invoices are read-only. You can view details, download files, and upload extra attachments only.",
            });
            return;
        }

        setEditingId(expense.id);
        setForm({
            category: expense.category,
            service_name: expense.service_name,
            vendor: expense.vendor,
            description: expense.description || "",
            amount: expense.amount.toString(),
            currency: expense.currency,
            billing_frequency: expense.billing_frequency,
            is_recurring: expense.is_recurring,
            invoice_number: expense.invoice_number || "",
            invoice_url: expense.invoice_url || "",
            billing_date: expense.billing_date.split("T")[0],
            due_date: expense.due_date ? expense.due_date.split("T")[0] : "",
            paid_date: expense.paid_date ? expense.paid_date.split("T")[0] : "",
            is_paid: expense.is_paid,
            is_active: expense.is_active,
            notes: expense.notes || "",
        });
        setShowModal(true);
    };

    const toggleSelectItem = (id) => {
        setSelectedIds((prev) =>
            prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
        );
    };

    const handleSelectAll = () => {
        if (selectedIds.length === expenses.length) {
            setSelectedIds([]);
        } else {
            setSelectedIds(expenses.map((exp) => exp.id));
        }
    };

    const handleDeleteSelected = async () => {
        if (selectedIds.length === 0) {
            setFeedback({ type: "error", message: "Please select expenses to delete." });
            return;
        }
        setConfirmAction({
            kind: "bulk-delete",
            title: "Delete selected expenses?",
            message: `This will remove ${selectedIds.length} selected expense(s).`,
        });
    };

    const runDeleteSelected = async () => {
        let deletedCount = 0;
        let newDeletedList = [...deletedInvoices]; // Start with current deleted list

        for (const id of selectedIds) {
            // Check if this is an imported invoice (contains vendor|number format)
            if (isImportedId(id)) {
                // Add to deleted invoices list (only if not already deleted)
                if (!newDeletedList.includes(id)) {
                    newDeletedList.push(id);
                    deletedCount++;
                }
            } else {
                try {
                    await axiosClient.delete(`/api/v1/platform/expenses/${id}`);
                    deletedCount++;
                } catch (err) {
                    console.error("Failed to delete expense:", err);
                }
            }
        }

        // Update state and localStorage once with all deletions
        setDeletedInvoices(newDeletedList);
        localStorage.setItem("deleted_invoices", JSON.stringify(newDeletedList));
        setSelectedIds([]);
        fetchExpenses();
        fetchSummary();
        setFeedback({ type: "success", message: `${deletedCount} expense(s) deleted successfully.` });
    };

    const handleDelete = async (id) => {
        setConfirmAction({
            kind: "single-delete",
            id,
            title: "Delete this expense?",
            message: "This action cannot be undone.",
        });
    };

    const runDelete = async (id) => {
        // Check if this is an imported invoice (contains vendor|number format)
        if (isImportedId(id)) {
            // Add to deleted invoices list
            const newDeleted = [...deletedInvoices, id];
            setDeletedInvoices(newDeleted);
            localStorage.setItem("deleted_invoices", JSON.stringify(newDeleted));

            // Refresh the list
            fetchExpenses();
            fetchSummary();
            setFeedback({ type: "success", message: "Expense deleted successfully." });
            return;
        }

        try {
            await axiosClient.delete(`/api/v1/platform/expenses/${id}`);
            fetchExpenses();
            fetchSummary();
            setFeedback({ type: "success", message: "Expense deleted successfully." });
        } catch (err) {
            console.error("Failed to delete expense:", err);
            setFeedback({ type: "error", message: "Failed to delete expense." });
        }
    };

    const handleFileUpload = async (expenseId, file) => {
        if (!file) return;

        setUploadingFile(true);
        try {
            const formData = new FormData();
            formData.append("file", file);

            await axiosClient.post(`/api/v1/platform/expenses/${expenseId}/upload`, formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            setFeedback({ type: "success", message: "File uploaded successfully." });
            fetchExpenses();
        } catch (err) {
            console.error("Failed to upload file:", err);
            setFeedback({ type: "error", message: err.response?.data?.detail || "Failed to upload file." });
        } finally {
            setUploadingFile(false);
            setSelectedFile(null);
        }
    };

    const handleFileDownload = async (expenseId) => {
        try {
            const expense = expenses.find(exp => exp.id === expenseId);
            if (!expense) {
                setFeedback({ type: "error", message: "Expense not found." });
                return;
            }

            // If it's an invoice URL from the API
            if (expense.invoice_url) {
                if (expense.invoice_url.startsWith("/api/")) {
                    // API endpoint - download as blob
                    const response = await axiosClient.get(expense.invoice_url, {
                        responseType: "blob",
                    });
                    const url = window.URL.createObjectURL(new Blob([response.data]));
                    const link = document.createElement("a");
                    link.href = url;
                    link.setAttribute("download", `${expense.invoice_number}.pdf`);
                    document.body.appendChild(link);
                    link.click();
                    window.URL.revokeObjectURL(url);
                    link.remove();
                } else {
                    // Direct URL or file path - open in new tab
                    window.open(expense.invoice_url, "_blank");
                }
                return;
            }

            // Fallback to attachment endpoint
            const response = await axiosClient.get(`/api/v1/platform/expenses/${expenseId}/download`, {
                responseType: "blob",
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement("a");
            link.href = url;
            link.setAttribute("download", `expense_${expenseId}_attachment`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error("Failed to download file:", err);
            setFeedback({ type: "error", message: "Failed to download file." });
        }
    };

    const handleFileDelete = async (expenseId) => {
        // Prevent deleting imported invoice files
        if (isImportedId(expenseId)) {
            setFeedback({
                type: "info",
                message: "Invoice files from documentation are read-only and cannot be deleted.",
            });
            return;
        }

        setConfirmAction({
            kind: "attachment-delete",
            id: expenseId,
            title: "Delete this attachment?",
            message: "The uploaded file will be removed from this expense.",
        });
    };

    const runFileDelete = async (expenseId) => {
        try {
            await axiosClient.delete(`/api/v1/platform/expenses/${expenseId}/attachment`);
            setFeedback({ type: "success", message: "Attachment deleted." });
            fetchExpenses();
        } catch (err) {
            console.error("Failed to delete attachment:", err);
            setFeedback({ type: "error", message: "Failed to delete attachment." });
        }
    };

    const handleAIExtract = async (files) => {
        if (!files || files.length === 0) {
            setFeedback({ type: "error", message: "Please select at least one file." });
            return;
        }

        if (files.length > 30) {
            setFeedback({ type: "error", message: "Maximum 30 files allowed. Please select fewer files." });
            return;
        }

        setUploadingFile(true);
        try {
            const formData = new FormData();
            // Append all files
            for (let i = 0; i < files.length; i++) {
                formData.append("files", files[i]);
            }

            const response = await axiosClient.post("/api/v1/platform/expenses/extract-invoice", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            if (response.data.success && response.data.results) {
                const results = response.data.results;
                const successfulResults = results.filter((r) => r.success);

                if (successfulResults.length > 0) {
                    // For multiple files, show a summary
                    if (successfulResults.length === 1) {
                        const extracted = successfulResults[0].extracted_data;
                        // Auto-populate form with single result
                        setForm((prev) => ({
                            ...prev,
                            service_name: extracted.service_name || prev.service_name,
                            vendor: extracted.vendor || prev.vendor,
                            amount: extracted.amount?.toString() || prev.amount,
                            currency: extracted.currency || prev.currency,
                            invoice_number: extracted.invoice_number || prev.invoice_number,
                            billing_date: extracted.billing_date || prev.billing_date,
                            due_date: extracted.due_date || prev.due_date,
                            description: extracted.description || prev.description,
                            category: extracted.category || prev.category,
                            billing_frequency: extracted.billing_frequency || prev.billing_frequency,
                            is_recurring: typeof extracted.is_recurring === "boolean" ? extracted.is_recurring : prev.is_recurring,
                        }));
                        setFeedback({ type: "success", message: `Invoice extracted from "${successfulResults[0].filename}". Review and save it.` });
                    } else {
                        // Multiple files - show summary
                        setFeedback({
                            type: "success",
                            message: `Extracted ${successfulResults.length} of ${files.length} invoices. Review the console output for all extracted data.`,
                        });
                        console.log("=== EXTRACTED INVOICE DATA ===");
                        successfulResults.forEach((result, idx) => {
                            console.log(`\n${idx + 1}. ${result.filename}:`);
                            console.log(result.extracted_data);
                        });
                        console.log("\n=== END EXTRACTED DATA ===");
                    }
                } else {
                    setFeedback({ type: "error", message: `Failed to extract data from ${files.length} file(s). Check file quality.` });
                }
            } else if (response.data.results) {
                const failed = response.data.results.filter((r) => !r.success);
                const firstError = failed[0]?.error;
                setFeedback({ type: "error", message: firstError || "No data extracted. Please check file quality or try a different file." });
            } else {
                setFeedback({ type: "error", message: "Extraction failed. Please try again or fill the form manually." });
            }
        } catch (err) {
            console.error("AI extraction failed:", err);
            setFeedback({ type: "error", message: err.response?.data?.detail || "AI extraction failed. Please fill manually." });
        } finally {
            setUploadingFile(false);
        }
    };

    const resetForm = () => {
        setEditingId(null);
        setShowModal(false);
        setForm({
            category: "database",
            service_name: "",
            vendor: "",
            description: "",
            amount: "",
            currency: "USD",
            billing_frequency: "monthly",
            is_recurring: true,
            invoice_number: "",
            invoice_url: "",
            billing_date: new Date().toISOString().split("T")[0],
            due_date: "",
            paid_date: "",
            is_paid: false,
            is_active: true,
            notes: "",
        });
    };

    const getCategoryStyle = (category) => {
        const cat = CATEGORIES.find((c) => c.value === category);
        return cat ? cat.color : "bg-gray-500/20 text-gray-300";
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-950 flex items-center justify-center">
                <div className="text-white">Loading...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-950 p-6">
            <div className="max-w-7xl mx-auto">
                {feedback && (
                    <div
                        className={`mb-4 rounded-lg border px-4 py-3 text-sm flex items-center justify-between gap-3 ${
                            feedback.type === "success"
                                ? "border-emerald-400/40 bg-emerald-500/10 text-emerald-200"
                                : feedback.type === "info"
                                    ? "border-blue-400/40 bg-blue-500/10 text-blue-200"
                                    : "border-rose-400/40 bg-rose-500/10 text-rose-200"
                        }`}
                    >
                        <span>{feedback.message}</span>
                        <button type="button" onClick={() => setFeedback(null)} className="text-current/80 hover:text-current">
                            Dismiss
                        </button>
                    </div>
                )}

                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-2xl font-bold text-white">💰 Platform Infrastructure Expenses</h1>
                        <p className="text-white/60 text-sm mt-1">Manage hosting, databases, domains, and services</p>
                    </div>
                    <button
                        onClick={() => setShowModal(true)}
                        className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium transition"
                    >
                        + Add Expense
                    </button>
                </div>

                {/* Summary Cards */}
                {summary && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                        <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                            <div className="text-white/60 text-xs font-medium mb-1">Total Expenses</div>
                            <div className="text-2xl font-bold text-white">{summary.total === 0 ? "N/A" : `$${summary.total.toLocaleString()}`}</div>
                        </div>
                        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-4">
                            <div className="text-emerald-300/80 text-xs font-medium mb-1">Paid</div>
                            <div className="text-2xl font-bold text-emerald-300">{summary.paid === 0 ? "N/A" : `$${summary.paid.toLocaleString()}`}</div>
                        </div>
                        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
                            <div className="text-yellow-300/80 text-xs font-medium mb-1">Pending</div>
                            <div className="text-2xl font-bold text-yellow-300">{summary.pending === 0 ? "N/A" : `$${summary.pending.toLocaleString()}`}</div>
                        </div>
                        <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4">
                            <div className="text-purple-300/80 text-xs font-medium mb-1">Monthly Recurring</div>
                            <div className="text-2xl font-bold text-purple-300">{summary.recurring_monthly === 0 ? "N/A" : `$${summary.recurring_monthly.toLocaleString()}`}</div>
                        </div>
                    </div>
                )}

                {/* Filters */}
                <div className="flex gap-3 mb-4 flex-wrap items-center">
                    <select
                        value={filterCategory}
                        onChange={(e) => setFilterCategory(e.target.value)}
                        className="px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm"
                    >
                        <option value="">All Categories</option>
                        {CATEGORIES.map((cat) => (
                            <option key={cat.value} value={cat.value}>
                                {cat.label}
                            </option>
                        ))}
                    </select>
                    <select
                        value={filterPaid}
                        onChange={(e) => setFilterPaid(e.target.value)}
                        className="px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm"
                    >
                        <option value="">All Status</option>
                        <option value="true">Paid</option>
                        <option value="false">Pending</option>
                    </select>
                    {selectedIds.length > 0 && (
                        <button
                            onClick={handleDeleteSelected}
                            className="px-4 py-2 rounded-lg bg-rose-500 text-white text-sm font-medium hover:bg-rose-600 transition-colors ml-auto flex items-center gap-2"
                        >
                            🗑️ Delete {selectedIds.length}
                        </button>
                    )}
                </div>

                {/* Expenses Table */}
                <div className="bg-white/5 border border-white/10 rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-white/5 border-b border-white/10">
                                <tr>
                                    <th className="px-4 py-3 text-center text-xs font-medium text-white/80 w-12">
                                        <input
                                            type="checkbox"
                                            checked={expenses.length > 0 && selectedIds.length === expenses.length}
                                            onChange={handleSelectAll}
                                            className="rounded w-4 h-4 cursor-pointer"
                                            title="Select All"
                                        />
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-white/80">Service</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-white/80">Category</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-white/80">Vendor</th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-white/80">Amount</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-white/80">Frequency</th>
                                    <th className="px-4 py-3 text-center text-xs font-medium text-white/80">Status</th>
                                    <th className="px-4 py-3 text-center text-xs font-medium text-white/80">Attachment</th>
                                    <th className="px-4 py-3 text-center text-xs font-medium text-white/80">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/10">
                                {expenses.length === 0 ? (
                                    <tr>
                                        <td colSpan="9" className="px-4 py-8 text-center text-white/60">
                                            No expenses found. Add your first expense to get started.
                                        </td>
                                    </tr>
                                ) : (
                                    expenses.map((exp) => (
                                        <tr key={exp.id} className={`hover:bg-white/5 ${selectedIds.includes(exp.id) ? 'bg-blue-500/10' : ''}`}>
                                            <td className="px-4 py-3 text-center">
                                                <input
                                                    type="checkbox"
                                                    checked={selectedIds.includes(exp.id)}
                                                    onChange={() => toggleSelectItem(exp.id)}
                                                    className="rounded w-4 h-4 cursor-pointer"
                                                />
                                            </td>
                                            <td className="px-4 py-3">
                                                <div className="text-white font-medium text-sm">{exp.service_name}</div>
                                                {exp.description && (
                                                    <div className="text-white/50 text-xs mt-0.5">{exp.description}</div>
                                                )}
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className={`inline-flex px-2 py-1 rounded text-xs font-medium ${getCategoryStyle(exp.category)}`}>
                                                    {CATEGORIES.find((c) => c.value === exp.category)?.label || exp.category}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 text-white/80 text-sm">{exp.vendor}</td>
                                            <td className="px-4 py-3 text-right text-white font-medium">
                                                {exp.amount === 0 ? "N/A" : `$${exp.amount.toLocaleString()} ${exp.currency}`}
                                            </td>
                                            <td className="px-4 py-3 text-white/70 text-sm capitalize">{exp.billing_frequency}</td>
                                            <td className="px-4 py-3 text-center">
                                                {exp.is_paid ? (
                                                    <span className="inline-flex px-2 py-1 rounded text-xs font-medium bg-emerald-500/20 text-emerald-300">
                                                        ✓ Paid
                                                    </span>
                                                ) : (
                                                    <span className="inline-flex px-2 py-1 rounded text-xs font-medium bg-yellow-500/20 text-yellow-300">
                                                        Pending
                                                    </span>
                                                )}
                                            </td>
                                            <td className="px-4 py-3 text-center">
                                                {exp.attachment_path ? (
                                                    <div className="flex items-center justify-center gap-1">
                                                        <button
                                                            onClick={() => handleFileDownload(exp.id)}
                                                            className="px-2 py-1 rounded text-xs bg-green-500/20 text-green-300 hover:bg-green-500/30"
                                                            title="Download"
                                                        >
                                                            📥
                                                        </button>
                                                        <button
                                                            onClick={() => handleFileDelete(exp.id)}
                                                            className="px-2 py-1 rounded text-xs bg-rose-500/20 text-rose-300 hover:bg-rose-500/30"
                                                            title="Delete attachment"
                                                        >
                                                            🗑️
                                                        </button>
                                                    </div>
                                                ) : exp.invoice_url ? (
                                                    // Show download button for imported invoices
                                                    <button
                                                        onClick={() => handleFileDownload(exp.id)}
                                                        className="px-2 py-1 rounded text-xs bg-green-500/20 text-green-300 hover:bg-green-500/30"
                                                        title="Download Invoice"
                                                    >
                                                        📥 Invoice
                                                    </button>
                                                ) : (
                                                    // Show upload button for new expenses
                                                    <label className="cursor-pointer">
                                                        <input
                                                            type="file"
                                                            className="hidden"
                                                            accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.xls,.xlsx,.txt"
                                                            onChange={(e) => {
                                                                if (e.target.files && e.target.files[0]) {
                                                                    handleFileUpload(exp.id, e.target.files[0]);
                                                                }
                                                            }}
                                                            disabled={uploadingFile}
                                                        />
                                                        <span className="inline-flex px-2 py-1 rounded text-xs bg-blue-500/20 text-blue-300 hover:bg-blue-500/30">
                                                            {uploadingFile ? "⏳" : "📎 Upload"}
                                                        </span>
                                                    </label>
                                                )}
                                            </td>
                                            <td className="px-4 py-3 text-center">
                                                <div className="flex items-center justify-center gap-2">
                                                    <button
                                                        onClick={() => handleEdit(exp)}
                                                        disabled={isImportedId(exp.id)}
                                                        className={`px-2 py-1 rounded text-xs ${isImportedId(exp.id) ? 'bg-blue-500/10 text-blue-500/50 cursor-not-allowed' : 'bg-blue-500/20 text-blue-300 hover:bg-blue-500/30'}`}
                                                        title={isImportedId(exp.id) ? "Imported data is read-only" : "Edit"}
                                                    >
                                                        Edit
                                                    </button>
                                                    <button
                                                        onClick={() => handleDelete(exp.id)}
                                                        className="px-2 py-1 rounded text-xs bg-rose-500/20 text-rose-300 hover:bg-rose-500/30"
                                                        title="Delete"
                                                    >
                                                        Delete
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
                    <div className="bg-slate-900 border border-white/10 rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                        <div className="sticky top-0 bg-slate-900 border-b border-white/10 px-6 py-4 flex items-center justify-between">
                            <h2 className="text-xl font-bold text-white">
                                {editingId ? "Edit Expense" : "Add New Expense"}
                            </h2>
                            <button onClick={resetForm} className="text-white/60 hover:text-white">✕</button>
                        </div>

                        <form onSubmit={handleSubmit} className="p-6 space-y-4">
                            {/* AI Invoice Extraction Section */}
                            {!editingId && (
                                <div className="bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/20 rounded-lg p-4 mb-6">
                                    <div className="flex items-start gap-3">
                                        <div className="text-3xl">🤖</div>
                                        <div className="flex-1">
                                            <h3 className="text-sm font-semibold text-white mb-1">AI Invoice Extraction - Batch Processing</h3>
                                            <p className="text-xs text-white/60 mb-1">
                                                Upload up to <strong>30 invoices</strong> at once (PDF, PNG, JPG, Excel, Word)
                                            </p>
                                            <p className="text-xs text-white/50 mb-3">
                                                📁 Supported: .pdf .png .jpg .xls .xlsx .doc .docx
                                            </p>
                                            <label className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-purple-500 to-blue-500 text-white font-medium cursor-pointer hover:opacity-90 transition-opacity">
                                                <input
                                                    type="file"
                                                    className="hidden"
                                                    accept=".png,.jpg,.jpeg,.pdf,.xls,.xlsx,.doc,.docx"
                                                    multiple
                                                    onChange={(e) => {
                                                        if (e.target.files && e.target.files.length > 0) {
                                                            handleAIExtract(Array.from(e.target.files));
                                                        }
                                                    }}
                                                    disabled={uploadingFile}
                                                />
                                                {uploadingFile ? (
                                                    <>
                                                        <span className="animate-spin">⏳</span>
                                                        <span>Extracting...</span>
                                                    </>
                                                ) : (
                                                    <>
                                                        <span>🔍</span>
                                                        <span>Select Invoices (Max 30)</span>
                                                    </>
                                                )}
                                            </label>
                                            <p className="text-xs text-white/40 mt-2">
                                                💡 Tip: Hold Ctrl/Cmd to select multiple files
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            )}

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-white/80 mb-1">Category *</label>
                                    <select
                                        value={form.category}
                                        onChange={(e) => setForm({ ...form, category: e.target.value })}
                                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
                                        required
                                    >
                                        {CATEGORIES.map((cat) => (
                                            <option key={cat.value} value={cat.value}>
                                                {cat.label}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-white/80 mb-1">Service Name *</label>
                                    <input
                                        type="text"
                                        value={form.service_name}
                                        onChange={(e) => setForm({ ...form, service_name: e.target.value })}
                                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
                                        placeholder="e.g., PostgreSQL Database"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-white/80 mb-1">Vendor *</label>
                                    <input
                                        type="text"
                                        value={form.vendor}
                                        onChange={(e) => setForm({ ...form, vendor: e.target.value })}
                                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
                                        placeholder="e.g., Render.com"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-white/80 mb-1">Amount *</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        value={form.amount}
                                        onChange={(e) => setForm({ ...form, amount: e.target.value })}
                                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
                                        placeholder="0.00"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-white/80 mb-1">Billing Frequency</label>
                                    <select
                                        value={form.billing_frequency}
                                        onChange={(e) => setForm({ ...form, billing_frequency: e.target.value })}
                                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
                                    >
                                        {BILLING_FREQUENCIES.map((freq) => (
                                            <option key={freq.value} value={freq.value}>
                                                {freq.label}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-white/80 mb-1">Invoice Date *</label>
                                    <input
                                        type="date"
                                        value={form.billing_date}
                                        onChange={(e) => setForm({ ...form, billing_date: e.target.value })}
                                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-white/80 mb-1">Invoice Number</label>
                                    <input
                                        type="text"
                                        value={form.invoice_number}
                                        onChange={(e) => setForm({ ...form, invoice_number: e.target.value })}
                                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-white/80 mb-1">Due Date</label>
                                    <input
                                        type="date"
                                        value={form.due_date}
                                        onChange={(e) => setForm({ ...form, due_date: e.target.value })}
                                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-white/80 mb-1">Description</label>
                                <textarea
                                    value={form.description}
                                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                                    className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
                                    rows="2"
                                    placeholder="Additional details..."
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-white/80 mb-1">Notes</label>
                                <textarea
                                    value={form.notes}
                                    onChange={(e) => setForm({ ...form, notes: e.target.value })}
                                    className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white"
                                    rows="2"
                                    placeholder="Internal notes..."
                                />
                            </div>

                            <div className="flex gap-4">
                                <label className="flex items-center gap-2 text-white/80">
                                    <input
                                        type="checkbox"
                                        checked={form.is_recurring}
                                        onChange={(e) => setForm({ ...form, is_recurring: e.target.checked })}
                                        className="rounded"
                                    />
                                    <span className="text-sm">Recurring</span>
                                </label>

                                <label className="flex items-center gap-2 text-white/80">
                                    <input
                                        type="checkbox"
                                        checked={form.is_paid}
                                        onChange={(e) => setForm({ ...form, is_paid: e.target.checked })}
                                        className="rounded"
                                    />
                                    <span className="text-sm">Paid</span>
                                </label>

                                <label className="flex items-center gap-2 text-white/80">
                                    <input
                                        type="checkbox"
                                        checked={form.is_active}
                                        onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                                        className="rounded"
                                    />
                                    <span className="text-sm">Active Service</span>
                                </label>
                            </div>

                            <div className="flex gap-3 pt-4">
                                <button
                                    type="submit"
                                    className="flex-1 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium"
                                >
                                    {editingId ? "Update Expense" : "Create Expense"}
                                </button>
                                <button
                                    type="button"
                                    onClick={resetForm}
                                    className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-white"
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {confirmAction && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
                    <div className="bg-slate-900 border border-white/10 rounded-lg w-full max-w-md p-6">
                        <h2 className="text-lg font-bold text-white">{confirmAction.title}</h2>
                        <p className="mt-2 text-sm text-white/60">{confirmAction.message}</p>
                        <div className="mt-6 flex justify-end gap-3">
                            <button
                                type="button"
                                onClick={() => setConfirmAction(null)}
                                className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-white"
                            >
                                Cancel
                            </button>
                            <button
                                type="button"
                                onClick={async () => {
                                    const action = confirmAction;
                                    setConfirmAction(null);
                                    if (action.kind === "bulk-delete") {
                                        await runDeleteSelected();
                                        return;
                                    }
                                    if (action.kind === "attachment-delete") {
                                        await runFileDelete(action.id);
                                        return;
                                    }
                                    await runDelete(action.id);
                                }}
                                className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white"
                            >
                                Confirm
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
