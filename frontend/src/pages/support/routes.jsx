/**
 * Support Routes Configuration
 * Support routes configuration
 */

import React from 'react';
import { Route } from 'react-router-dom';
import {
    SupportPage,
    CreateTicketPage,
    TicketDetailPage,
    KnowledgeBasePage,
    KnowledgeBaseArticlePage,
    AgentDashboardPage,
    AgentTicketPage,
    CreateArticlePage,
    SupportAdminDashboard
} from './index';

/**
 * Generate support routes for React Router
 * These routes are added to the main application
 */
export function getSupportRoutes() {
    return [
        // Customer Support Routes
        <Route key="support-list" path="/support/tickets" element={<SupportPage />} />,
        <Route key="support-create" path="/support/tickets/create" element={<CreateTicketPage />} />,
        <Route key="support-detail" path="/support/tickets/:ticketId" element={<TicketDetailPage />} />,

        // Knowledge Base Routes
        <Route key="kb-list" path="/support/knowledge-base" element={<KnowledgeBasePage />} />,
        <Route key="kb-article" path="/support/knowledge-base/:articleId" element={<KnowledgeBaseArticlePage />} />,
        <Route key="kb-create" path="/admin/knowledge-base/create" element={<CreateArticlePage />} />,

        // Agent Routes
        <Route key="agent-dashboard" path="/agent/dashboard" element={<AgentDashboardPage />} />,
        <Route key="agent-ticket" path="/agent/tickets/:ticketId" element={<AgentTicketPage />} />,

        // Admin Routes
        <Route key="admin-support" path="/admin/support" element={<SupportAdminDashboard />} />,
    ];
}

/**
 * Support Routes Summary:
 * 
 * Customer Routes:
 * - GET  /support/tickets           - List customer's tickets
 * - POST /support/tickets/create    - Create new ticket
 * - GET  /support/tickets/:ticketId - View ticket details
 * 
 * Knowledge Base Routes:
 * - GET  /support/knowledge-base           - Browse articles
 * - GET  /support/knowledge-base/:articleId - Read article
 * - POST /admin/knowledge-base/create      - Create article (admin)
 * 
 * Agent Routes:
 * - GET  /agent/dashboard              - Agent dashboard
 * - GET  /agent/tickets/:ticketId      - Edit/manage ticket
 * 
 * Admin Routes:
 * - GET  /admin/support                - Support admin dashboard
 */
