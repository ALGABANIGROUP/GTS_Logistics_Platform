// src/components/bots/panels/documents-manager/DocumentUploader.jsx
import React, { useState, useCallback } from 'react';
import { documentService } from '../../../../services/documentService';
import './DocumentUploader.css';

const DocumentUploader = ({ onUploadSuccess }) => {
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [documentType, setDocumentType] = useState('document');
    const [errorMessage, setErrorMessage] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    const supportedDocumentTypes = [
        { id: 'bill_of_lading', name: 'Bill of Lading' },
        { id: 'commercial_invoice', name: 'Commercial Invoice' },
        { id: 'packing_list', name: 'Packing List' },
        { id: 'certificate_of_origin', name: 'Certificate of Origin' },
        { id: 'insurance_certificate', name: 'Insurance Certificate' },
        { id: 'customs_declaration', name: 'Customs Declaration' },
        { id: 'other', name: 'Other Document' }
    ];

    const handleDragOver = (e) => {
        e.preventDefault();
        e.currentTarget.classList.add('active');
    };

    const handleDragLeave = (e) => {
        e.currentTarget.classList.remove('active');
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.currentTarget.classList.remove('active');
        const files = Array.from(e.dataTransfer.files);
        handleFileSelect(files);
    };

    const handleFileSelect = (files) => {
        const newFiles = files.map(file => ({
            file,
            id: Date.now() + performance.now(),
            name: file.name,
            size: (file.size / 1024 / 1024).toFixed(2) + ' MB',
            type: documentType,
            status: 'pending'
        }));

        setUploadedFiles(prev => [...prev, ...newFiles]);
        setErrorMessage('');
    };

    const handleFileInput = (e) => {
        const files = Array.from(e.target.files);
        handleFileSelect(files);
    };

    const handleUpload = async () => {
        if (uploadedFiles.length === 0) {
            setErrorMessage('Please select files to upload');
            return;
        }

        setUploading(true);
        setProgress(0);
        setErrorMessage('');
        setSuccessMessage('');

        try {
            const filesToUpload = uploadedFiles.filter(f => f.status === 'pending' || f.status === 'failed');
            const totalFiles = filesToUpload.length;
            let successCount = 0;

            for (let i = 0; i < totalFiles; i++) {
                const fileItem = filesToUpload[i];

                // Update status to uploading
                setUploadedFiles(prev =>
                    prev.map(f =>
                        f.id === fileItem.id ? { ...f, status: 'uploading' } : f
                    )
                );

                try {
                    // Call real backend API
                    const result = await documentService.uploadDocument(
                        fileItem.file,
                        documentType,
                        { fileName: fileItem.name }
                    );

                    // Update status to uploaded
                    setUploadedFiles(prev =>
                        prev.map(f =>
                            f.id === fileItem.id
                                ? {
                                    ...f,
                                    status: 'uploaded',
                                    uploadId: result.id,
                                    uploadTime: new Date().toLocaleTimeString()
                                }
                                : f
                        )
                    );

                    successCount++;

                    // Update progress
                    setProgress(Math.round(((i + 1) / totalFiles) * 100));

                    // Notify parent component
                    if (onUploadSuccess) {
                        onUploadSuccess(result);
                    }

                } catch (error) {
                    console.error(`Upload failed for ${fileItem.name}:`, error);
                    setUploadedFiles(prev =>
                        prev.map(f =>
                            f.id === fileItem.id
                                ? { ...f, status: 'failed', error: error.message }
                                : f
                        )
                    );
                    setErrorMessage(`Failed to upload ${fileItem.name}: ${error.message}`);
                }
            }

            if (successCount > 0) {
                setSuccessMessage(` Successfully uploaded ${successCount} file(s)`);
            }

        } catch (error) {
            console.error('Upload error:', error);
            setErrorMessage('Upload failed: ' + error.message);
        } finally {
            setUploading(false);
        }
    };

    const handleRemoveFile = (id) => {
        setUploadedFiles(prev => prev.filter(f => f.id !== id));
    };

    const clearAll = () => {
        setUploadedFiles([]);
        setProgress(0);
        setErrorMessage('');
        setSuccessMessage('');
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'pending':
                return '';
            case 'uploading':
                return '';
            case 'uploaded':
                return '';
            case 'processing':
                return '';
            case 'failed':
                return '';
            default:
                return '';
        }
    };

    return (
        <div className="document-uploader">
            <div className="uploader-header">
                <h2> Upload Documents</h2>
                <p>Upload real documents for processing and management</p>
            </div>

            {/* Error Message */}
            {errorMessage && (
                <div className="error-banner">
                    <span> {errorMessage}</span>
                    <button onClick={() => setErrorMessage('')}></button>
                </div>
            )}

            {/* Success Message */}
            {successMessage && (
                <div className="success-banner">
                    <span>{successMessage}</span>
                    <button onClick={() => setSuccessMessage('')}></button>
                </div>
            )}

            {/* Upload Settings */}
            <div className="upload-settings">
                <div className="setting-group">
                    <label>Document Type</label>
                    <select
                        value={documentType}
                        onChange={(e) => setDocumentType(e.target.value)}
                        disabled={uploading}
                    >
                        {supportedDocumentTypes.map(type => (
                            <option key={type.id} value={type.id}>
                                {type.name}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Drop Zone */}
            <div
                className="dropzone"
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
            >
                <div className="dropzone-content">
                    <div className="dropzone-icon"></div>
                    <h3>Drag & Drop Documents Here</h3>
                    <p>or</p>
                    <label className="browse-button">
                        <span>Browse Files</span>
                        <input
                            type="file"
                            multiple
                            onChange={handleFileInput}
                            disabled={uploading}
                            accept=".pdf,.jpg,.jpeg,.png,.xlsx,.csv,.docx,.doc,.txt,.gif,.bmp,.tiff"
                        />
                    </label>
                    <div className="supported-formats">
                        Supported: PDF, JPG, PNG, Excel, CSV, Word, TXT
                    </div>
                    <div className="max-size">Max: 50MB per file</div>
                </div>
            </div>

            {/* Progress Bar */}
            {uploading && (
                <div className="progress-container">
                    <div className="progress-bar">
                        <div
                            className="progress-fill"
                            style={{ width: `${progress}%` }}
                        >
                            <span className="progress-text">{progress}%</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Uploaded Files List */}
            {uploadedFiles.length > 0 && (
                <div className="upload-queue">
                    <h3> Files ({uploadedFiles.length})</h3>

                    <div className="file-list">
                        {uploadedFiles.map((file) => (
                            <div key={file.id} className={`file-item file-${file.status}`}>
                                <div className="file-info">
                                    <span className="file-icon">{getStatusIcon(file.status)}</span>
                                    <div className="file-details">
                                        <div className="file-name">{file.name}</div>
                                        <div className="file-meta">
                                            <span className="file-size">{file.size}</span>
                                            <span className="file-type">{file.type}</span>
                                            {file.status === 'failed' && (
                                                <span className="error-text">{file.error}</span>
                                            )}
                                            {file.uploadTime && (
                                                <span className="upload-time">{file.uploadTime}</span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                                <div className="file-actions">
                                    {file.status === 'pending' && (
                                        <button
                                            className="remove-btn"
                                            onClick={() => handleRemoveFile(file.id)}
                                            disabled={uploading}
                                        >
                                             Remove
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="upload-controls">
                        <button
                            className="cancel-btn"
                            onClick={clearAll}
                            disabled={uploading}
                        >
                             Clear All
                        </button>
                        <button
                            className="upload-btn"
                            onClick={handleUpload}
                            disabled={uploading || uploadedFiles.length === 0}
                        >
                            {uploading ? ` Uploading... ${progress}%` : ' Upload Documents'}
                        </button>
                    </div>
                </div>
            )}

            <div className="upload-tips">
                <h4> Tips:</h4>
                <ul>
                    <li>Real files are saved to server storage</li>
                    <li>Supports: PDF, Images, Excel, CSV, Word, Text</li>
                    <li>Maximum 50MB per file</li>
                    <li>All uploads are encrypted and secure</li>
                </ul>
            </div>
        </div>
    );
};

export default DocumentUploader;
