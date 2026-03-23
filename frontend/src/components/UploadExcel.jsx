import React, { useState } from "react";
import axiosClient from "../api/axiosClient";

const UploadExcel = () => {
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    if (!file) return alert("Please select a file first.");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axiosClient.post("/upload-excel", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      alert("✅ File uploaded and processed successfully!");
    } catch (err) {
      console.error("❌ Upload failed", err);
    }
  };

  return (
    <div className="space-y-4 p-4">
      <input type="file" accept=".xlsx" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload} className="bg-blue-600 text-white px-4 py-2 rounded">
        Upload Excel
      </button>
    </div>
  );
};

export default UploadExcel;
