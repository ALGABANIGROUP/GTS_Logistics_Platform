// frontend/src/pages/ai-bots/AIDocumentsManagerPanel.jsx
/**
 * Documents Manager Bot Control Panel - Main Route
 * Advanced document management with AI capabilities
 */
import React from 'react';
import DocumentsManagerPanel from '../../components/bots/panels/documents-manager/DocumentsManagerPanel';

const AIDocumentsManagerPanel = () => {
    return (
        <div style={{ width: `100%`, height: `100%`, overflow: 'auto' }}>
            <DocumentsManagerPanel />
        </div>
    );
};

export default AIDocumentsManagerPanel;
