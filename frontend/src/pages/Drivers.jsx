import React, { useEffect, useMemo, useState } from "react";
import axiosClient from "../api/axiosClient";
import { useAuth } from "../contexts/AuthContext.jsx";

const emptyCreateForm = {
  full_name: "",
  email: "",
  phone_number: "",
  password: "",
  is_active: true,
};

export default function Drivers() {
  const { permissions } = useAuth();
  const canManage = useMemo(
    () => Array.isArray(permissions) && permissions.includes("drivers.manage"),
    [permissions]
  );

  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [createForm, setCreateForm] = useState({ ...emptyCreateForm });
  const [editing, setEditing] = useState(null);
  const [editForm, setEditForm] = useState({ ...emptyCreateForm });
  const [isSaving, setIsSaving] = useState(false);

  const loadDrivers = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await axiosClient.get("/api/v1/drivers");
      const list = res?.data?.drivers || [];
      setDrivers(Array.isArray(list) ? list : []);
    } catch (err) {
      setError(
        err?.normalized?.detail ||
          err?.response?.data?.detail ||
          err?.message ||
          "Failed to load drivers."
      );
      setDrivers([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDrivers();
  }, []);

  const handleCreate = async () => {
    if (!createForm.email.trim()) {
      setError("Email is required.");
      return;
    }
    setIsSaving(true);
    setError("");
    try {
      await axiosClient.post("/api/v1/drivers", {
        full_name: createForm.full_name || undefined,
        email: createForm.email.trim(),
        phone_number: createForm.phone_number || undefined,
        password: createForm.password || undefined,
        is_active: createForm.is_active,
      });
      setCreateForm({ ...emptyCreateForm });
      await loadDrivers();
    } catch (err) {
      setError(
        err?.normalized?.detail ||
          err?.response?.data?.detail ||
          err?.message ||
          "Failed to create driver."
      );
    } finally {
      setIsSaving(false);
    }
  };

  const handleEditStart = (driver) => {
    setEditing(driver);
    setEditForm({
      full_name: driver.full_name || "",
      email: driver.email || "",
      phone_number: driver.phone_number || "",
      password: "",
      is_active: Boolean(driver.is_active),
    });
  };

  const handleEditCancel = () => {
    setEditing(null);
    setEditForm({ ...emptyCreateForm });
  };

  const handleUpdate = async () => {
    if (!editing) return;
    if (!editForm.email.trim()) {
      setError("Email is required.");
      return;
    }

    setIsSaving(true);
    setError("");
    try {
      await axiosClient.patch(`/api/v1/drivers/${editing.id}`, {
        full_name: editForm.full_name || undefined,
        email: editForm.email.trim(),
        phone_number: editForm.phone_number || undefined,
        password: editForm.password || undefined,
        is_active: editForm.is_active,
      });
      handleEditCancel();
      await loadDrivers();
    } catch (err) {
      setError(
        err?.normalized?.detail ||
          err?.response?.data?.detail ||
          err?.message ||
          "Failed to update driver."
      );
    } finally {
      setIsSaving(false);
    }
  };

  const handleToggleActive = async (driver) => {
    setIsSaving(true);
    setError("");
    try {
      await axiosClient.patch(`/api/v1/drivers/${driver.id}`, {
        is_active: !driver.is_active,
      });
      await loadDrivers();
    } catch (err) {
      setError(
        err?.normalized?.detail ||
          err?.response?.data?.detail ||
          err?.message ||
          "Failed to update driver status."
      );
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="glass-page p-6 space-y-6">
      <div className="flex items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Drivers</h1>
          <div className="text-sm text-slate-400">Dispatcher / Fleet</div>
        </div>
      </div>

      {error ? (
        <div className="rounded-lg border border-rose-400/30 bg-rose-500/10 p-3 text-sm text-rose-100">
          {error}
        </div>
      ) : null}

      {canManage ? (
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4 space-y-3">
          <div className="text-sm font-semibold text-slate-200">Create driver</div>
          <div className="grid gap-3 sm:grid-cols-2">
            <input
              value={createForm.full_name}
              onChange={(e) => setCreateForm((prev) => ({ ...prev, full_name: e.target.value }))}
              placeholder="Full name"
              className="rounded-lg border border-slate-700/60 bg-slate-900/40 px-3 py-2 text-sm text-slate-100"
            />
            <input
              value={createForm.email}
              onChange={(e) => setCreateForm((prev) => ({ ...prev, email: e.target.value }))}
              placeholder="Email"
              className="rounded-lg border border-slate-700/60 bg-slate-900/40 px-3 py-2 text-sm text-slate-100"
            />
            <input
              value={createForm.phone_number}
              onChange={(e) => setCreateForm((prev) => ({ ...prev, phone_number: e.target.value }))}
              placeholder="Phone number"
              className="rounded-lg border border-slate-700/60 bg-slate-900/40 px-3 py-2 text-sm text-slate-100"
            />
            <input
              value={createForm.password}
              onChange={(e) => setCreateForm((prev) => ({ ...prev, password: e.target.value }))}
              placeholder="Password (optional)"
              type="password"
              className="rounded-lg border border-slate-700/60 bg-slate-900/40 px-3 py-2 text-sm text-slate-100"
            />
          </div>
          <button
            type="button"
            onClick={handleCreate}
            disabled={isSaving}
            className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500 disabled:opacity-60"
          >
            {isSaving ? "Saving..." : "Create"}
          </button>
        </div>
      ) : null}

      {editing ? (
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4 space-y-3">
          <div className="text-sm font-semibold text-slate-200">
            Edit: {editing.email}
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <input
              value={editForm.full_name}
              onChange={(e) => setEditForm((prev) => ({ ...prev, full_name: e.target.value }))}
              placeholder="Full name"
              className="rounded-lg border border-slate-700/60 bg-slate-900/40 px-3 py-2 text-sm text-slate-100"
            />
            <input
              value={editForm.email}
              onChange={(e) => setEditForm((prev) => ({ ...prev, email: e.target.value }))}
              placeholder="Email"
              className="rounded-lg border border-slate-700/60 bg-slate-900/40 px-3 py-2 text-sm text-slate-100"
            />
            <input
              value={editForm.phone_number}
              onChange={(e) => setEditForm((prev) => ({ ...prev, phone_number: e.target.value }))}
              placeholder="Phone number"
              className="rounded-lg border border-slate-700/60 bg-slate-900/40 px-3 py-2 text-sm text-slate-100"
            />
            <input
              value={editForm.password}
              onChange={(e) => setEditForm((prev) => ({ ...prev, password: e.target.value }))}
              placeholder="New password (optional)"
              type="password"
              className="rounded-lg border border-slate-700/60 bg-slate-900/40 px-3 py-2 text-sm text-slate-100"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={handleUpdate}
              disabled={isSaving}
              className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500 disabled:opacity-60"
            >
              {isSaving ? "Saving..." : "Save"}
            </button>
            <button
              type="button"
              onClick={handleEditCancel}
              className="rounded-lg border border-slate-600/60 px-4 py-2 text-sm text-slate-200"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : null}

      <div className="rounded-2xl border border-white/10 bg-white/5 p-4 space-y-3">
        <div className="text-sm font-semibold text-slate-200">Driver list</div>
        {loading ? (
          <div className="text-sm text-slate-400">Loading drivers...</div>
        ) : drivers.length === 0 ? (
          <div className="text-sm text-slate-400">No drivers found.</div>
        ) : (
          <div className="space-y-2">
            {drivers.map((driver) => (
              <div
                key={driver.id}
                className="flex flex-wrap items-start justify-between gap-3 rounded-lg border border-white/10 bg-slate-900/50 p-3"
              >
                <div>
                  <div className="text-sm font-semibold text-slate-100">
                    {driver.full_name || driver.email}
                  </div>
                  <div className="text-xs text-slate-400">{driver.email}</div>
                  <div className="mt-1 text-xs text-slate-500">
                    {driver.phone_number ? `Phone: ${driver.phone_number}` : "No phone"}
                    {" · "}
                    {driver.is_active ? "Active" : "Inactive"}
                  </div>
                </div>
                {canManage ? (
                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => handleEditStart(driver)}
                      className="rounded-lg border border-slate-600/60 px-3 py-1 text-xs text-slate-200 hover:bg-slate-800/60"
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      onClick={() => handleToggleActive(driver)}
                      disabled={isSaving}
                      className="rounded-lg border border-slate-600/60 px-3 py-1 text-xs text-slate-200 hover:bg-slate-800/60 disabled:opacity-60"
                    >
                      {driver.is_active ? "Deactivate" : "Activate"}
                    </button>
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
