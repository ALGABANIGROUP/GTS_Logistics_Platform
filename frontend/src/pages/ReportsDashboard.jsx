import React, { useEffect, useMemo, useState } from "react";
import axiosClient from "../api/axiosClient";
import { useReportsStore } from "../stores/useReportsStore";
import { useAuthStore } from "../stores/useAuthStore";

const STATUS_LABELS = {
  draft: "Draft",
  active: "Active",
  archived: "Archived",
};

const DATE_PRESETS = [
  { value: "all", label: "All" },
  { value: "today", label: "Today" },
  { value: "week", label: "This Week" },
  { value: "month", label: "This Month" },
  { value: "year", label: "This Year" },
];

export default function ReportsDashboard() {
  const {
    reports,
    categories,
    stats,
    loading,
    favoriteReports,
    buildPreviewModel,
    fetchReports,
    createReport,
    updateReport,
    deleteReport,
    generateReport,
    exportReport,
    duplicateReport,
    toggleReportStatus,
  } = useReportsStore();

  const hasPermission = useAuthStore((state) => state.hasPermission);
  const canView = hasPermission?.("reports.view");
  const canCreate = hasPermission?.("reports.create");
  const canGenerate = hasPermission?.("reports.generate");
  const canExport = hasPermission?.("reports.export");
  const canDelete = hasPermission?.("reports.delete");
  const canUpdate = hasPermission?.("reports.edit") || hasPermission?.("reports.update");

  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState("grid");
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [selectedStatuses, setSelectedStatuses] = useState(["active"]);
  const [datePreset, setDatePreset] = useState("all");
  const [currentSort, setCurrentSort] = useState("updated");
  const [selectedReports, setSelectedReports] = useState(new Set());
  const [previewReport, setPreviewReport] = useState(null);
  const [editingReport, setEditingReport] = useState(null);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  const filteredReports = useMemo(() => {
    let filtered = [...reports];

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter((report) =>
        report.name.toLowerCase().includes(query) ||
        report.description.toLowerCase().includes(query) ||
        report.tags?.some((tag) => tag.toLowerCase().includes(query))
      );
    }

    if (selectedCategories.length > 0) {
      filtered = filtered.filter((report) => selectedCategories.includes(report.category));
    }

    if (selectedStatuses.length > 0) {
      filtered = filtered.filter((report) => selectedStatuses.includes(report.status));
    }

    if (datePreset !== "all") {
      const now = new Date();
      const cutoffDate = new Date();

      switch (datePreset) {
        case "today":
          cutoffDate.setDate(now.getDate() - 1);
          break;
        case "week":
          cutoffDate.setDate(now.getDate() - 7);
          break;
        case "month":
          cutoffDate.setMonth(now.getMonth() - 1);
          break;
        case "year":
          cutoffDate.setFullYear(now.getFullYear() - 1);
          break;
        default:
          break;
      }

      filtered = filtered.filter((report) => new Date(report.updatedAt) > cutoffDate);
    }

    filtered.sort((a, b) => {
      switch (currentSort) {
        case "name":
          return a.name.localeCompare(b.name, "en");
        case "created":
          return new Date(b.createdAt) - new Date(a.createdAt);
        case "category":
          return a.category.localeCompare(b.category, "en");
        case "generated":
          return (b.generationCount || 0) - (a.generationCount || 0);
        default:
          return new Date(b.updatedAt) - new Date(a.updatedAt);
      }
    });

    return filtered;
  }, [reports, searchQuery, selectedCategories, selectedStatuses, datePreset, currentSort]);

  const filteredFavoriteReports = useMemo(
    () => filteredReports.filter((r) => r.tags?.includes("favorite")),
    [filteredReports]
  );

  const allSelected = filteredReports.length > 0 && selectedReports.size === filteredReports.length;

  const handleQuickReport = async () => {
    if (!canCreate) return;
    await createReport({
      type: "predefined",
      template: "userActivity",
      status: "active",
      tags: ["favorite"],
    });
  };

  const handleCreateReport = async () => {
    if (!canCreate) return;
    const name = window.prompt("New Report Name", "New Report");
    if (!name) return;
    await createReport({ name, status: "draft", tags: ["custom"] });
  };

  const handlePreviewModel = () => {
    if (!canView) return;
    setPreviewReport(buildPreviewModel());
  };

  const handleView = async (report) => {
    if (!canView) return;
    try {
      const response = await axiosClient.get(`/api/v1/reports/view/${report.id}`);
      setPreviewReport(response.data);
    } catch (error) {
      console.warn("Live report preview failed, using local report card data:", error);
      setPreviewReport(report);
    }
  };

  const handleGenerate = async (report) => {
    if (!canGenerate) return;
    const data = await generateReport(report.id);
    setPreviewReport(data);
  };

  const handleExport = async (report, format) => {
    if (!canExport) return;
    const selectedFormat = format || window.prompt("Choose format: pdf / excel / csv / json", "excel");
    if (!selectedFormat) return;
    await exportReport(report.id, selectedFormat);
  };

  const handleToggleFavorite = async (report) => {
    if (!canUpdate) return;
    const tags = report.tags?.includes("favorite")
      ? report.tags.filter((tag) => tag !== "favorite")
      : [...(report.tags || []), "favorite"];
    await updateReport(report.id, { tags });
  };

  const handleDelete = async (report) => {
    if (!canDelete) return;
    if (window.confirm(`Are you sure you want to delete the report "${report.name}"?`)) {
      await deleteReport(report.id);
    }
  };

  const handleDuplicate = async (report) => {
    if (!canCreate) return;
    const newName = window.prompt("New copy name", `${report.name} (Copy)`);
    if (newName) {
      await duplicateReport(report.id, newName);
    }
  };

  const toggleSelectAll = () => {
    if (allSelected) {
      setSelectedReports(new Set());
    } else {
      setSelectedReports(new Set(filteredReports.map((report) => report.id)));
    }
  };

  const toggleSelect = (reportId) => {
    setSelectedReports((prev) => {
      const next = new Set(prev);
      if (next.has(reportId)) {
        next.delete(reportId);
      } else {
        next.add(reportId);
      }
      return next;
    });
  };

  const bulkGenerate = async () => {
    if (!canGenerate) return;
    for (const reportId of selectedReports) {
      await generateReport(reportId);
    }
    setSelectedReports(new Set());
  };

  const bulkExport = async () => {
    if (!canExport) return;
    const format = window.prompt("Choose format: pdf / excel / csv / json", "excel");
    if (!format) return;
    for (const reportId of selectedReports) {
      await exportReport(reportId, format);
    }
    setSelectedReports(new Set());
  };

  const bulkArchive = async () => {
    if (!canUpdate) return;
    for (const reportId of selectedReports) {
      await toggleReportStatus(reportId, "archived");
    }
    setSelectedReports(new Set());
  };

  const bulkDelete = async () => {
    if (!canDelete) return;
    if (!window.confirm(`Delete ${selectedReports.size} report(s)?`)) return;
    for (const reportId of selectedReports) {
      await deleteReport(reportId);
    }
    setSelectedReports(new Set());
  };

  const formatDate = (dateString) => {
    if (!dateString) return "—";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US");
  };

  const timeAgo = (dateString) => {
    if (!dateString) return "Never";
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return "Now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
    return `${Math.floor(diffDays / 30)}mo ago`;
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Reports Center</h1>
          <p className="text-slate-400">Advanced reports dashboard with filters and multi-format export</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleQuickReport}
            className={`glass-btn-secondary ${!canCreate ? "opacity-50 cursor-not-allowed" : ""}`}
            disabled={!canCreate}
          >
            Quick Report
          </button>
          <button
            onClick={handlePreviewModel}
            className={`glass-btn-secondary ${!canView ? "opacity-50 cursor-not-allowed" : ""}`}
            disabled={!canView}
          >
            Preview Model
          </button>
          <button
            onClick={handleCreateReport}
            className={`glass-btn-primary ${!canCreate ? "opacity-50 cursor-not-allowed" : ""}`}
            disabled={!canCreate}
          >
            Create New Report
          </button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div className="glass-card p-4">
          <div className="text-sm text-slate-400">Total Reports</div>
          <div className="text-2xl font-bold text-white">{stats.total}</div>
        </div>
        <div className="glass-card p-4">
          <div className="text-sm text-slate-400">Active</div>
          <div className="text-2xl font-bold text-emerald-400">{stats.active}</div>
        </div>
        <div className="glass-card p-4">
          <div className="text-sm text-slate-400">Scheduled</div>
          <div className="text-2xl font-bold text-blue-400">{stats.scheduled}</div>
        </div>
        <div className="glass-card p-4">
          <div className="text-sm text-slate-400">Favorites</div>
          <div className="text-2xl font-bold text-yellow-400">{favoriteReports().length}</div>
        </div>
      </div>

      <div className="glass-card p-4 space-y-4">
        <div className="flex flex-wrap gap-3">
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search for a report..."
            className="glass-input flex-1 min-w-[220px]"
          />
          <select
            value={currentSort}
            onChange={(e) => setCurrentSort(e.target.value)}
            className="glass-select"
          >
            <option value="updated">Last Updated</option>
            <option value="name">Name</option>
            <option value="created">Creation Date</option>
            <option value="category">Category</option>
            <option value="generated">Most Generated</option>
          </select>
          <button
            onClick={() => setViewMode(viewMode === "grid" ? "list" : "grid")}
            className="glass-btn-secondary"
          >
            {viewMode === "grid" ? "List View" : "Grid View"}
          </button>
        </div>

        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() =>
                setSelectedCategories((prev) =>
                  prev.includes(category.id)
                    ? prev.filter((id) => id !== category.id)
                    : [...prev, category.id]
                )
              }
              className={`px-3 py-1 rounded-full text-sm border transition ${selectedCategories.includes(category.id)
                ? "bg-blue-600 text-white border-blue-500"
                : "border-slate-500 text-slate-300"
                }`}
            >
              {category.name}
            </button>
          ))}
        </div>

        <div className="flex flex-wrap gap-2">
          {Object.keys(STATUS_LABELS).map((status) => (
            <button
              key={status}
              onClick={() =>
                setSelectedStatuses((prev) =>
                  prev.includes(status)
                    ? prev.filter((item) => item !== status)
                    : [...prev, status]
                )
              }
              className={`px-3 py-1 rounded-full text-sm border transition ${selectedStatuses.includes(status)
                ? "bg-white/10 text-white border-white/20"
                : "border-slate-600 text-slate-400"
                }`}
            >
              {STATUS_LABELS[status]}
            </button>
          ))}
        </div>

        <div className="flex flex-wrap gap-2">
          {DATE_PRESETS.map((preset) => (
            <button
              key={preset.value}
              onClick={() => setDatePreset(preset.value)}
              className={`px-3 py-1 rounded-full text-sm border transition ${datePreset === preset.value
                ? "bg-emerald-500/20 text-emerald-200 border-emerald-400/40"
                : "border-slate-600 text-slate-400"
                }`}
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="glass-card p-8 text-center text-slate-300">Loading reports...</div>
      ) : (
        <>
          {viewMode === "grid" ? (
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {filteredReports.map((report) => (
                <div key={report.id} className="glass-card p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-lg font-semibold text-white">{report.name}</div>
                      <div className="text-xs text-slate-400">{report.description || "—"}</div>
                    </div>
                    <span className="text-xs px-2 py-1 rounded-full bg-white/10 text-slate-200">
                      {STATUS_LABELS[report.status] || report.status}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2 text-xs">
                    <span className="px-2 py-1 rounded-full bg-blue-500/10 text-blue-200">
                      {categories.find((c) => c.id === report.category)?.name || report.category}
                    </span>
                    <span className="px-2 py-1 rounded-full bg-white/10 text-slate-300">
                      {report.type === "predefined" ? "Template" : "Custom"}
                    </span>
                    {report.tags?.map((tag) => (
                      <span key={tag} className="px-2 py-1 rounded-full bg-white/5 text-slate-400">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span>Last updated: {formatDate(report.updatedAt)}</span>
                    <span>Generated: {report.generationCount || 0}</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => handleView(report)}
                      className={`glass-btn-secondary text-sm ${!canView ? "opacity-50 cursor-not-allowed" : ""}`}
                      disabled={!canView}
                    >
                      View
                    </button>
                    <button
                      onClick={() => handleGenerate(report)}
                      className={`glass-btn-primary text-sm ${!canGenerate ? "opacity-50 cursor-not-allowed" : ""}`}
                      disabled={!canGenerate}
                    >
                      Generate
                    </button>
                    <button
                      onClick={() => handleExport(report)}
                      className={`glass-btn-secondary text-sm ${!canExport ? "opacity-50 cursor-not-allowed" : ""}`}
                      disabled={!canExport}
                    >
                      Export
                    </button>
                    <button
                      onClick={() => handleToggleFavorite(report)}
                      className={`glass-btn-secondary text-sm ${!canUpdate ? "opacity-50 cursor-not-allowed" : ""}`}
                      disabled={!canUpdate}
                    >
                      {report.tags?.includes("favorite") ? "Remove Favorite" : "Add Favorite"}
                    </button>
                    <button
                      onClick={() => handleDelete(report)}
                      className={`glass-btn-danger text-sm ${!canDelete ? "opacity-50 cursor-not-allowed" : ""}`}
                      disabled={!canDelete}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="glass-card overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-white/5 text-slate-300">
                  <tr>
                    <th className="px-4 py-3 text-right">
                      <input type="checkbox" checked={allSelected} onChange={toggleSelectAll} />
                    </th>
                    <th className="px-4 py-3 text-right">Report Name</th>
                    <th className="px-4 py-3 text-right">Category</th>
                    <th className="px-4 py-3 text-right">Status</th>
                    <th className="px-4 py-3 text-right">Last Updated</th>
                    <th className="px-4 py-3 text-right">Generated</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredReports.map((report) => (
                    <tr key={report.id} className="border-t border-white/5 hover:bg-white/5">
                      <td className="px-4 py-3">
                        <input
                          type="checkbox"
                          checked={selectedReports.has(report.id)}
                          onChange={() => toggleSelect(report.id)}
                        />
                      </td>
                      <td className="px-4 py-3 text-white">
                        <div className="font-semibold">{report.name}</div>
                        <div className="text-xs text-slate-400">{report.description || "—"}</div>
                      </td>
                      <td className="px-4 py-3 text-slate-300">
                        {categories.find((c) => c.id === report.category)?.name || report.category}
                      </td>
                      <td className="px-4 py-3 text-slate-300">{STATUS_LABELS[report.status] || report.status}</td>
                      <td className="px-4 py-3 text-slate-400">
                        <div>{formatDate(report.updatedAt)}</div>
                        <div className="text-xs">{timeAgo(report.updatedAt)}</div>
                      </td>
                      <td className="px-4 py-3 text-slate-400 text-center">{report.generationCount || 0}</td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex flex-wrap justify-end gap-2">
                          <button
                            onClick={() => handleView(report)}
                            className={`glass-btn-secondary text-xs ${!canView ? "opacity-50 cursor-not-allowed" : ""}`}
                            disabled={!canView}
                          >
                            View
                          </button>
                          <button
                            onClick={() => handleGenerate(report)}
                            className={`glass-btn-primary text-xs ${!canGenerate ? "opacity-50 cursor-not-allowed" : ""}`}
                            disabled={!canGenerate}
                          >
                            Generate
                          </button>
                          <button
                            onClick={() => handleExport(report)}
                            className={`glass-btn-secondary text-xs ${!canExport ? "opacity-50 cursor-not-allowed" : ""}`}
                            disabled={!canExport}
                          >
                            Export
                          </button>
                          <button
                            onClick={() => handleDuplicate(report)}
                            className={`glass-btn-secondary text-xs ${!canCreate ? "opacity-50 cursor-not-allowed" : ""}`}
                            disabled={!canCreate}
                          >
                            Duplicate
                          </button>
                          <button
                            onClick={() => handleDelete(report)}
                            className={`glass-btn-danger text-xs ${!canDelete ? "opacity-50 cursor-not-allowed" : ""}`}
                            disabled={!canDelete}
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {selectedReports.size > 0 && (
            <div className="fixed bottom-6 left-1/2 z-40 flex -translate-x-1/2 items-center gap-4 rounded-2xl bg-blue-600/90 px-6 py-3 text-white shadow-xl">
              <span>{selectedReports.size} reports selected</span>
              <button
                onClick={bulkGenerate}
                className={`glass-btn-secondary ${!canGenerate ? "opacity-50 cursor-not-allowed" : ""}`}
                disabled={!canGenerate}
              >
                Generate Selected
              </button>
              <button
                onClick={bulkExport}
                className={`glass-btn-secondary ${!canExport ? "opacity-50 cursor-not-allowed" : ""}`}
                disabled={!canExport}
              >
                Export Selected
              </button>
              <button
                onClick={bulkArchive}
                className={`glass-btn-secondary ${!canUpdate ? "opacity-50 cursor-not-allowed" : ""}`}
                disabled={!canUpdate}
              >
                Archive
              </button>
              <button
                onClick={bulkDelete}
                className={`glass-btn-danger ${!canDelete ? "opacity-50 cursor-not-allowed" : ""}`}
                disabled={!canDelete}
              >
                Delete Selected
              </button>
              <button onClick={() => setSelectedReports(new Set())} className="glass-btn-secondary">
                Deselect
              </button>
            </div>
          )}
        </>
      )}

      {previewReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="glass-card max-w-3xl w-full p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-white">Report Preview</h2>
              <button onClick={() => setPreviewReport(null)} className="glass-btn-secondary">
                Close
              </button>
            </div>
            <div className="space-y-2">
              <div className="text-lg text-white">{previewReport.report?.name || previewReport.name}</div>
              <div className="text-sm text-slate-400">{previewReport.report?.description || previewReport.description || "—"}</div>
              <div className="text-xs text-slate-500">Last generated: {formatDate(previewReport.lastGeneratedAt || previewReport.metadata?.generatedAt)}</div>
            </div>
            {previewReport.summary && (
              <div className="grid gap-3 md:grid-cols-2">
                {Object.values(previewReport.summary).map((metric) => (
                  <div key={metric.name} className="rounded-xl bg-white/5 p-3">
                    <div className="text-xs text-slate-400">{metric.name}</div>
                    <div className="text-lg text-white">
                      {metric.average?.toFixed?.(2) ?? metric.total ?? "—"}
                    </div>
                  </div>
                ))}
              </div>
            )}
            {previewReport.insights && previewReport.insights.length > 0 && (
              <div className="space-y-2">
                <div className="text-sm text-slate-300">Key Insights</div>
                <div className="space-y-2">
                  {previewReport.insights.map((insight, idx) => (
                    <div key={`${insight.metric}-${idx}`} className="rounded-lg bg-white/5 p-3 text-sm text-slate-200">
                      {insight.description}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {editingReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="glass-card max-w-lg w-full p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-white">Edit Report</h2>
              <button onClick={() => setEditingReport(null)} className="glass-btn-secondary">
                Close
              </button>
            </div>
            <div className="space-y-3">
              <input
                value={editingReport.name}
                onChange={(e) => setEditingReport({ ...editingReport, name: e.target.value })}
                className="glass-input"
                placeholder="Report Name"
              />
              <textarea
                value={editingReport.description}
                onChange={(e) => setEditingReport({ ...editingReport, description: e.target.value })}
                className="glass-textarea"
                rows={3}
                placeholder="Report Description"
              />
              <select
                value={editingReport.status}
                onChange={(e) => setEditingReport({ ...editingReport, status: e.target.value })}
                className="glass-select"
              >
                {Object.entries(STATUS_LABELS).map(([key, label]) => (
                  <option key={key} value={key}>
                    {label}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={() => setEditingReport(null)} className="glass-btn-secondary">
                Cancel
              </button>
              <button
                onClick={async () => {
                  await updateReport(editingReport.id, {
                    name: editingReport.name,
                    description: editingReport.description,
                    status: editingReport.status,
                  });
                  setEditingReport(null);
                }}
                className="glass-btn-primary"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
