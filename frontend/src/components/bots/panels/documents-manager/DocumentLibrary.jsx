// src/components/bots/panels/documents-manager/DocumentLibrary.jsx
import React, { useState, useEffect } from 'react';
import { documentService } from '../../../../services/documentService';
import './DocumentLibrary.css';

const DocumentLibrary = ({ refreshTrigger }) => {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [selectedDocs, setSelectedDocs] = useState([]);
    const [viewMode, setViewMode] = useState('grid');
    const [sortBy, setSortBy] = useState('date_desc');
    const [currentPage, setCurrentPage] = useState(1);
    const [totalDocuments, setTotalDocuments] = useState(0);
    const [limit] = useState(50);

    useEffect(() => {
        loadDocuments();
    }, [currentPage, refreshTrigger]);

    const loadDocuments = async () => {
        setLoading(true);
        setErrorMessage('');
        try {
            const result = await documentService.getDocuments(currentPage, limit);
            if (result.documents) {
                setDocuments(result.documents);
                setTotalDocuments(result.total || 0);
            }
        } catch (error) {
            console.error('Error loading documents:', error);
            setErrorMessage('Failed to load documents: ' + error.message);
            setDocuments([]);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (docId) => {
        if (!window.confirm('Are you sure you want to delete this document?')) return;

        try {
            await documentService.deleteDocument(docId);
            setDocuments(prev => prev.filter(d => d.id !== docId));
            setErrorMessage('');
        } catch (error) {
            console.error('Delete error:', error);
            setErrorMessage('Failed to delete document: ' + error.message);
        }
    };

    const handleDownload = async (docId, docName) => {
        try {
            const blob = await documentService.downloadDocument(docId);
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = docName;
            link.click();
        } catch (error) {
            console.error('Download error:', error);
            setErrorMessage('Failed to download document: ' + error.message);
        }
    };

    const sortedDocuments = [...documents].sort((a, b) => {
        if (sortBy === 'name_asc') return a.name.localeCompare(b.name);
        if (sortBy === 'name_desc') return b.name.localeCompare(a.name);
        if (sortBy === 'date_asc') return new Date(a.uploaded_at) - new Date(b.uploaded_at);
        if (sortBy === 'date_desc') return new Date(b.uploaded_at) - new Date(a.uploaded_at);
        if (sortBy === 'size_asc') return a.size - b.size;
        if (sortBy === 'size_desc') return b.size - a.size;
        return 0;
    });

    const getStatusColor = (status) => {
        switch (status) {
            case 'uploaded':
                return '#10b981';
            case 'processing':
                return '#f59e0b';
            case 'failed':
                return '#ef4444';
            default:
                return '#6b7280';
        }
    };

    const formatDate = (dateString) => {
        try {
            return new Date(dateString).toLocaleDateString();
        } catch {
            return 'N/A';
        }
    };

    const formatFileSize = (bytes) => {
        if (!bytes) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    };

    return (
        <div className="document-library">
            <div className="library-header">
                <h3> Document Library</h3>
                <p>View and manage all uploaded documents</p>
            </div>

            {errorMessage && (
                <div className="error-banner">
                    <span> {errorMessage}</span>
                    <button onClick={() => setErrorMessage('')}></button>
                </div>
            )}

            {/* Controls */}
            <div className="library-controls">
                <div className="sort-control">
                    <label>Sort by:</label>
                    <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                        <option value="date_desc">Newest First</option>
                        <option value="date_asc">Oldest First</option>
                        <option value="name_asc">Name (A-Z)</option>
                        <option value="name_desc">Name (Z-A)</option>
                        <option value="size_desc">Largest First</option>
                        <option value="size_asc">Smallest First</option>
                    </select>
                </div>

                <div className="view-control">
                    <button
                        className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
                        onClick={() => setViewMode('grid')}
                        title="Grid View"
                    >
                         Grid
                    </button>
                    <button
                        className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
                        onClick={() => setViewMode('list')}
                        title="List View"
                    >
                         List
                    </button>
                </div>
            </div>

            {/* Documents Display */}
            {loading ? (
                <div className="loading-state">
                    <p> Loading documents...</p>
                </div>
            ) : sortedDocuments.length === 0 ? (
                <div className="empty-state">
                    <p> No documents found</p>
                    <p className="empty-subtitle">Upload some documents to get started</p>
                </div>
            ) : (
                <>
                    {viewMode === 'grid' ? (
                        <div className="documents-grid">
                            {sortedDocuments.map(doc => (
                                <div key={doc.id || doc.filename} className="document-card">
                                    <div className="card-header">
                                        <span className="doc-icon"></span>
                                        <span
                                            className="status-badge"
                                            style={{ backgroundColor: getStatusColor(doc.status || 'uploaded') }}
                                            title={doc.status || 'uploaded'}
                                        >
                                            {(doc.status && typeof doc.status === 'string') ? doc.status.charAt(0).toUpperCase() : 'U'}
                                        </span>
                                    </div>
                                    <div className="card-content">
                                        <h4 className="doc-name" title={doc.name || doc.filename}>{doc.name || doc.filename}</h4>
                                        <p className="doc-size">{formatFileSize(doc.size)}</p>
                                        <p className="doc-date">{formatDate(doc.uploaded_at)}</p>
                                    </div>
                                    <div className="card-actions">
                                        <button
                                            className="action-btn download-btn"
                                            onClick={() => handleDownload(doc.id, doc.name)}
                                            title="Download"
                                        >
                                            
                                        </button>
                                        <button
                                            className="action-btn delete-btn"
                                            onClick={() => handleDelete(doc.id)}
                                            title="Delete"
                                        >
                                            
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="documents-list">
                            <div className="list-header">
                                <div className="col col-name">Name</div>
                                <div className="col col-type">Type</div>
                                <div className="col col-size">Size</div>
                                <div className="col col-date">Date</div>
                                <div className="col col-status">Status</div>
                                <div className="col col-actions">Actions</div>
                            </div>
                            {sortedDocuments.map(doc => (
                                <div key={doc.id} className="list-row">
                                    <div className="col col-name">
                                        <span className="doc-icon"></span>
                                        <span title={doc.name}>{doc.name}</span>
                                    </div>
                                    <div className="col col-type">{doc.type || 'document'}</div>
                                    <div className="col col-size">{formatFileSize(doc.size)}</div>
                                    <div className="col col-date">{formatDate(doc.uploaded_at)}</div>
                                    <div className="col col-status">
                                        <span
                                            className="status-badge"
                                            style={{ backgroundColor: getStatusColor(doc.status) }}
                                        >
                                            {doc.status}
                                        </span>
                                    </div>
                                    <div className="col col-actions">
                                        <button
                                            className="action-btn"
                                            onClick={() => handleDownload(doc.id, doc.name)}
                                            title="Download"
                                        >
                                            
                                        </button>
                                        <button
                                            className="action-btn"
                                            onClick={() => handleDelete(doc.id)}
                                            title="Delete"
                                        >
                                            
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Pagination */}
                    {totalDocuments > limit && (
                        <div className="pagination">
                            <p>Showing {sortedDocuments.length} of {totalDocuments} documents</p>
                            <div className="pagination-buttons">
                                <button
                                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                    disabled={currentPage === 1}
                                >
                                     Previous
                                </button>
                                <span>Page {currentPage}</span>
                                <button
                                    onClick={() => setCurrentPage(p => p + 1)}
                                    disabled={currentPage * limit >= totalDocuments}
                                >
                                    Next 
                                </button>
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default DocumentLibrary;
