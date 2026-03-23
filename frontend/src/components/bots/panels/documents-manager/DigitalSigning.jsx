import React, { useEffect, useRef, useState } from 'react';
import documentsService from '../../../../services/documentsService';
import './DigitalSigning.css';

const CURRENT_SIGNER = {
    id: 'documents.manager',
    name: 'Documents Manager',
    email: 'documents.manager@gts.local',
};

const DigitalSigning = () => {
    const canvasRef = useRef(null);
    const [isDrawing, setIsDrawing] = useState(false);
    const [signatureMode, setSignatureMode] = useState('draw');
    const [documents, setDocuments] = useState([]);
    const [verificationLog, setVerificationLog] = useState([]);
    const [busyDocumentId, setBusyDocumentId] = useState(null);

    useEffect(() => {
        loadDocuments();
    }, []);

    const loadDocuments = async () => {
        try {
            const data = await documentsService.listDocuments();
            setDocuments(data);
        } catch (error) {
            console.error('Failed to load signing documents:', error);
            setDocuments([]);
        }
    };

    const startDrawing = (e) => {
        if (!canvasRef.current) return;
        setIsDrawing(true);
        const ctx = canvasRef.current.getContext('2d');
        const rect = canvasRef.current.getBoundingClientRect();
        ctx.beginPath();
        ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
    };

    const draw = (e) => {
        if (!isDrawing || !canvasRef.current) return;
        const ctx = canvasRef.current.getContext('2d');
        const rect = canvasRef.current.getBoundingClientRect();
        ctx.lineWidth = 2;
        ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
        ctx.stroke();
    };

    const stopDrawing = () => setIsDrawing(false);

    const clearSignature = () => {
        if (!canvasRef.current) return;
        const ctx = canvasRef.current.getContext('2d');
        ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
    };

    const signDocument = async (documentId) => {
        setBusyDocumentId(documentId);
        try {
            await documentsService.signDocument(
                documentId,
                CURRENT_SIGNER.id,
                CURRENT_SIGNER.name,
                CURRENT_SIGNER.email,
            );
            await loadDocuments();
        } catch (error) {
            console.error('Failed to sign document:', error);
        } finally {
            setBusyDocumentId(null);
        }
    };

    const verifyDocument = async (documentId) => {
        setBusyDocumentId(documentId);
        try {
            const result = await documentsService.verifyDocument(documentId);
            setVerificationLog((prev) => [
                {
                    id: `${documentId}_${Date.now()}`,
                    documentId,
                    message: result.message,
                    verifiedAt: result.verified_at,
                    isVerified: result.is_verified,
                },
                ...prev,
            ]);
        } catch (error) {
            console.error('Failed to verify document:', error);
        } finally {
            setBusyDocumentId(null);
        }
    };

    const pendingSignatures = documents.filter((doc) => doc.requires_signature || !doc.signature);
    const signedDocuments = documents.filter((doc) => doc.signature);

    return (
        <div className="digital-signing">
            <div className="signing-header">
                <h2>Digital Signing & Verification</h2>
                <p>HMAC-backed document signatures with verification status and audit history.</p>
            </div>

            <div className="signing-methods">
                <h3>Signing Methods</h3>
                <div className="methods-tabs">
                    <button className={`method-btn ${signatureMode === 'draw' ? 'active' : ''}`} onClick={() => setSignatureMode('draw')}>
                        Draw Signature
                    </button>
                    <button className={`method-btn ${signatureMode === 'type' ? 'active' : ''}`} onClick={() => setSignatureMode('type')}>
                        Type Signature
                    </button>
                    <button className={`method-btn ${signatureMode === 'upload' ? 'active' : ''}`} onClick={() => setSignatureMode('upload')}>
                        Upload Signature
                    </button>
                </div>
            </div>

            {signatureMode === 'draw' && (
                <div className="signature-canvas-section">
                    <h3>Signature Pad</h3>
                    <canvas
                        ref={canvasRef}
                        width={500}
                        height={200}
                        onMouseDown={startDrawing}
                        onMouseMove={draw}
                        onMouseUp={stopDrawing}
                        onMouseLeave={stopDrawing}
                        className="signature-canvas"
                    />
                    <div className="canvas-controls">
                        <button className="clear-btn" onClick={clearSignature}>Clear</button>
                    </div>
                </div>
            )}

            {signatureMode === 'type' && (
                <div className="signature-type-section">
                    <h3>Signature Identity</h3>
                    <input type="text" className="signature-input" value={CURRENT_SIGNER.name} readOnly />
                    <div className="signature-preview">
                        <p className="signature-text">{CURRENT_SIGNER.name}</p>
                    </div>
                </div>
            )}

            {signatureMode === 'upload' && (
                <div className="signature-upload-section">
                    <h3>Signature Asset</h3>
                    <div className="upload-area">
                        <p>Document signatures are generated from the active signer identity and file hash.</p>
                    </div>
                </div>
            )}

            <div className="pending-signatures">
                <h3>Pending Signatures</h3>
                <div className="pending-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Document</th>
                                <th>Type</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {pendingSignatures.length === 0 ? (
                                <tr>
                                    <td colSpan="4">No pending signatures</td>
                                </tr>
                            ) : (
                                pendingSignatures.map((item) => (
                                    <tr key={item.id}>
                                        <td>{item.name}</td>
                                        <td>{item.type}</td>
                                        <td><span className="status-badge pending">{item.status}</span></td>
                                        <td>
                                            <button
                                                className="action-btn small"
                                                onClick={() => signDocument(item.id)}
                                                disabled={busyDocumentId === item.id}
                                            >
                                                {busyDocumentId === item.id ? 'Signing...' : 'Sign'}
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="signed-documents">
                <h3>Signed Documents</h3>
                <div className="signed-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Document</th>
                                <th>Signer</th>
                                <th>Signed Date</th>
                                <th>Verified</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {signedDocuments.length === 0 ? (
                                <tr>
                                    <td colSpan="5">No signed documents yet</td>
                                </tr>
                            ) : (
                                signedDocuments.map((doc) => (
                                    <tr key={doc.id} className="signed-row verified">
                                        <td>{doc.name}</td>
                                        <td>{doc.signature?.signed_document?.signer_name || 'Unknown'}</td>
                                        <td>{doc.signature?.signed_document?.signed_at?.slice(0, 10) || 'N/A'}</td>
                                        <td>
                                            <span className="verify-badge verified">
                                                Verified candidate
                                            </span>
                                        </td>
                                        <td>
                                            <button
                                                className="action-btn small verify"
                                                onClick={() => verifyDocument(doc.id)}
                                                disabled={busyDocumentId === doc.id}
                                            >
                                                {busyDocumentId === doc.id ? 'Verifying...' : 'Verify'}
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="verification-logs">
                <h3>Verification Audit Trail</h3>
                <div className="logs-list">
                    {verificationLog.length === 0 ? (
                        <div className="log-item">
                            <div className="log-content">
                                <div className="log-title">No verification events yet</div>
                            </div>
                        </div>
                    ) : (
                        verificationLog.map((item) => (
                            <div key={item.id} className="log-item">
                                <div className="log-content">
                                    <div className="log-title">{item.message}</div>
                                    <div className="log-timestamp">{item.verifiedAt}</div>
                                </div>
                                <div className="log-hash">{item.isVerified ? 'VALID' : 'INVALID'}</div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            <div className="signing-stats">
                <h3>Signing Statistics</h3>
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-info">
                            <div className="stat-label">Total Signed</div>
                            <div className="stat-value">{signedDocuments.length}</div>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-info">
                            <div className="stat-label">Pending</div>
                            <div className="stat-value">{pendingSignatures.length}</div>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-info">
                            <div className="stat-label">Verified Checks</div>
                            <div className="stat-value">{verificationLog.filter((item) => item.isVerified).length}</div>
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-info">
                            <div className="stat-label">Issues</div>
                            <div className="stat-value">{verificationLog.filter((item) => !item.isVerified).length}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DigitalSigning;
