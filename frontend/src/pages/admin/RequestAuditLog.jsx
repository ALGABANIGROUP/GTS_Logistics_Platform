import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axiosClient from '../../api/axiosClient';

export default function RequestAuditLog() {
    const { requestId } = useParams();
    const navigate = useNavigate();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchAuditLog = async () => {
            setLoading(true);
            setError('');
            try {
                const res = await axiosClient.get(`/api/v1/admin/portal/requests/${requestId}/audit-log`);
                setData(res.data);
            } catch (e) {
                setError(e?.response?.data?.detail || e.message || 'Failed to load audit log');
            } finally {
                setLoading(false);
            }
        };

        if (requestId) {
            fetchAuditLog();
        }
    }, [requestId]);

    const formatDate = (dateStr) => {
        if (!dateStr) return 'Unknown';
        const date = new Date(dateStr);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    };

    const getActionIcon = (action) => {
        switch (action) {
            case 'request_created':
                return '??';
            case 'approved':
            case 'request_approved':
                return '?';
            case 'denied':
            case 'rejected':
            case 'request_rejected':
                return '?';
            case 'email_verified':
                return '??';
            case 'access_granted':
                return '??';
            default:
                return '??';
        }
    };

    const getActionColor = (action) => {
        switch (action) {
            case 'request_created':
                return 'bg-blue-50 border-blue-300';
            case 'approved':
            case 'request_approved':
            case 'access_granted':
            case 'email_verified':
                return 'bg-green-50 border-green-300';
            case 'denied':
            case 'rejected':
            case 'request_rejected':
                return 'bg-red-50 border-red-300';
            default:
                return 'bg-gray-50 border-gray-300';
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6">
                <div className="mb-4">
                    <button
                        onClick={() => navigate(-1)}
                        className="text-blue-600 hover:underline"
                    >
                        ← Back
                    </button>
                </div>
                <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                    {error}
                </div>
            </div>
        );
    }

    if (!data) {
        return (
            <div className="p-6">
                <div className="text-center py-12">
                    <p className="text-gray-600">No audit log found</p>
                </div>
            </div>
        );
    }

    const request = data.request || {};
    const auditLog = data.audit_log || [];

    return (
        <div className="p-6">
            <div className="mb-6">
                <button
                    onClick={() => navigate(-1)}
                    className="text-blue-600 hover:underline mb-4"
                >
                    ← Back to Requests
                </button>

                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <h1 className="text-3xl font-bold text-gray-900 mb-4">Request Audit Log</h1>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        <div className="p-4 bg-gray-50 rounded-lg">
                            <p className="text-xs text-gray-600 uppercase font-semibold">Request ID</p>
                            <p className="text-lg font-bold text-gray-900 font-mono">{request.id}</p>
                        </div>
                        <div className="p-4 bg-gray-50 rounded-lg">
                            <p className="text-xs text-gray-600 uppercase font-semibold">Applicant</p>
                            <p className="text-lg font-bold text-gray-900">{request.full_name}</p>
                            <p className="text-sm text-gray-600">{request.email}</p>
                        </div>
                        <div className="p-4 bg-gray-50 rounded-lg">
                            <p className="text-xs text-gray-600 uppercase font-semibold">Current Status</p>
                            <p className={`text-lg font-bold capitalize ${request.status === 'approved' ? 'text-green-600' :
                                    (request.status === 'rejected' || request.status === 'denied') ? 'text-red-600' :
                                        request.status === 'pending' ? 'text-yellow-600' :
                                            'text-gray-600'
                                }`}>
                                {request.status}
                            </p>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                        <div>
                            <p className="text-gray-600 text-xs uppercase font-semibold">Company</p>
                            <p className="font-medium">{request.company}</p>
                        </div>
                        <div>
                            <p className="text-gray-600 text-xs uppercase font-semibold">System</p>
                            <p className="font-medium capitalize">{request.system}</p>
                        </div>
                        <div>
                            <p className="text-gray-600 text-xs uppercase font-semibold">Country</p>
                            <p className="font-medium">{request.country}</p>
                        </div>
                        <div>
                            <p className="text-gray-600 text-xs uppercase font-semibold">Submitted</p>
                            <p className="font-medium text-xs">{formatDate(request.created_at)}</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-6">Activity Timeline</h2>

                {auditLog.length === 0 ? (
                    <div className="text-center py-12">
                        <p className="text-gray-600">No audit entries found</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {auditLog.map((entry, idx) => (
                            <div
                                key={entry.id || idx}
                                className={`p-4 rounded-lg border-2 ${getActionColor(entry.action)}`}
                            >
                                <div className="flex items-start gap-4">
                                    <div className="text-2xl mt-1">{getActionIcon(entry.action)}</div>

                                    <div className="flex-1">
                                        <div className="flex items-center justify-between mb-2">
                                            <h3 className="font-bold text-gray-900 capitalize">
                                                {entry.action.replace(/_/g, ' ')}
                                            </h3>
                                            <span className="text-xs text-gray-500">
                                                {formatDate(entry.created_at)}
                                            </span>
                                        </div>

                                        <p className="text-sm text-gray-600 mb-2">
                                            <span className="font-semibold">Actor:</span> {entry.actor || 'System'}
                                        </p>

                                        {entry.ip_address && (
                                            <p className="text-xs text-gray-500 mb-2">
                                                IP: <code className="bg-gray-200 px-1 rounded">{entry.ip_address}</code>
                                            </p>
                                        )}

                                        {entry.details && (
                                            <div className="mt-3 p-3 bg-gray-100 rounded text-sm">
                                                <p className="font-semibold text-gray-700 mb-2">Details:</p>
                                                <pre className="text-xs text-gray-600 overflow-x-auto">
                                                    {JSON.stringify(entry.details, null, 2)}
                                                </pre>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="mt-6 p-4 bg-blue-50 border border-blue-300 rounded-lg text-sm text-blue-900">
                <p>📋 Total actions logged: <strong>{auditLog.length}</strong></p>
                <p className="mt-1">🔒 All actions are recorded for compliance and security purposes.</p>
            </div>
        </div>
    );
}
