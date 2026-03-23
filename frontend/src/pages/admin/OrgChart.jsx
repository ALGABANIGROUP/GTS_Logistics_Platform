import React, { useEffect, useState } from "react";
import axiosClient from "@/api/axiosClient";
import { useRefreshSubscription } from "../../contexts/UiActionsContext.jsx";

const OrgChart = () => {
  const [tree, setTree] = useState([]);
  const [error, setError] = useState("");
  const [moveUnitId, setMoveUnitId] = useState("");
  const [moveParentId, setMoveParentId] = useState("");

  const loadTree = async () => {
    setError("");
    try {
      const res = await axiosClient.get("/api/v1/admin/org/tree");
      setTree(res.data?.data?.tree || []);
    } catch (err) {
      setError(err?.normalized?.detail || "Failed to load org chart.");
    }
  };

  useEffect(() => {
    loadTree();
  }, []);

  useRefreshSubscription(() => {
    loadTree();
  });

  const moveUnit = async () => {
    if (!moveUnitId) return;
    try {
      await axiosClient.post(
        `/api/v1/admin/org/units/${moveUnitId}/move`,
        null,
        { params: { parent_id: moveParentId ? Number(moveParentId) : null } }
      );
      setMoveUnitId("");
      setMoveParentId("");
      await loadTree();
    } catch (err) {
      setError(err?.normalized?.detail || "Failed to move org unit.");
    }
  };

  const renderNode = (node, depth = 0) => (
    <div key={node.id} style={{ marginLeft: depth * 16 }}>
      <div className="text-sm text-white">
        {node.name} <span className="text-xs text-slate-200">(ID: {node.id})</span>
      </div>
      {Array.isArray(node.children) &&
        node.children.map((child) => renderNode(child, depth + 1))}
    </div>
  );

  return (
    <div className="glass-page">
      <div className="glass-card">
        <h1 className="text-xl font-semibold text-white">Org Chart</h1>
        {error && <p className="mt-2 text-sm text-rose-200">{error}</p>}
        <div className="mt-4 space-y-2">{tree.map((node) => renderNode(node))}</div>
        <div className="mt-6 rounded border border-white/10 bg-white/5 p-3">
          <div className="text-sm font-semibold text-white">Move Org Unit</div>
          <div className="mt-2 flex flex-wrap gap-2">
            <input
              className="w-32 rounded border border-white/20 bg-black/30 px-2 py-1 text-xs text-white"
              placeholder="Unit ID"
              value={moveUnitId}
              onChange={(e) => setMoveUnitId(e.target.value)}
            />
            <input
              className="w-32 rounded border border-white/20 bg-black/30 px-2 py-1 text-xs text-white"
              placeholder="Parent ID (optional)"
              value={moveParentId}
              onChange={(e) => setMoveParentId(e.target.value)}
            />
            <button
              className="rounded border border-white/20 px-3 py-1 text-xs text-white hover:bg-white/10"
              onClick={moveUnit}
            >
              Move
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrgChart;
