// src/components/bots/panels/system-admin/DataManagement.jsx
import React, { useState, useEffect } from 'react';
import { adminService } from '../../../../services/adminService';
import './DataManagement.css';

const DataManagement = ({ onNewNotification, refreshKey }) => {
    const [backups, setBackups] = useState([]);
    const [statistics, setStatistics] = useState(null);
    const [loading, setLoading] = useState(false);
    const [activeOperation, setActiveOperation] = useState(null);

    useEffect(() => {
        loadData();
    }, [refreshKey]);

    const loadData = async () => {
        setLoading(true);
        try {
            const [backupsList, stats] = await Promise.all([
                adminService.listBackups(),
                adminService.getDataUsageStatistics()
            ]);

            setBackups(backupsList.backups || []);
            setStatistics(stats);
        } catch (error) {
            console.error('Failed to load data:', error);
            onNewNotification('Failed to load data management info', '');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateBackup = async (backupType = 'full') => {
        if (!confirm(`Create ${backupType} backup? This may take a few minutes.`)) return;

        setActiveOperation('backup');
        try {
            const result = await adminService.createBackup(backupType);
            onNewNotification(`Backup started: ${result.backup_id}`, '');
            setTimeout(() => loadData(), 2000);
        } catch (error) {
            console.error('Failed to create backup:', error);
            onNewNotification('Failed to create backup', '');
        } finally {
            setActiveOperation(null);
        }
    };

    const handleCleanup = async () => {
        if (!confirm('Clean up temporary files older than 7 days?')) return;

        setActiveOperation('cleanup');
        try {
            const result = await adminService.cleanupTempFiles();
            onNewNotification(`Cleaned ${result.cleaned_files_count} files`, '');
        } catch (error) {
            console.error('Failed to cleanup:', error);
            onNewNotification('Failed to cleanup temp files', '');
        } finally {
            setActiveOperation(null);
        }
    };

    const handleOptimize = async () => {
        if (!confirm('Optimize database? This will run ANALYZE, REINDEX, and VACUUM operations.')) return;

        setActiveOperation('optimize');
        try {
            const result = await adminService.optimizeDatabase();
            onNewNotification('Database optimized successfully', '');
        } catch (error) {
            console.error('Failed to optimize:', error);
            onNewNotification('Failed to optimize database', '');
        } finally {
            setActiveOperation(null);
        }
    };

    if (loading) {
        return (
            <div className="data-loading">
                <div className="spinner-large"></div>
                <p>Loading data management...</p>
            </div>
        );
    }

    return (
        <div className="data-management">
            {/* Database Statistics */}
            {statistics && (
                <div className="data-stats-section">
                    <h2> Database Statistics</h2>
                    <div className="db-stats-grid">
                        <div className="db-stat-card">
                            <span className="stat-icon-db"></span>
                            <div className="stat-info-db">
                                <span className="stat-value-db">{statistics.database.size_gb} GB</span>
                                <span className="stat-label-db">Database Size</span>
                            </div>
                        </div>
                        <div className="db-stat-card">
                            <span className="stat-icon-db"></span>
                            <div className="stat-info-db">
                                <span className="stat-value-db">{statistics.database.users_count}</span>
                                <span className="stat-label-db">Users</span>
                            </div>
                        </div>
                        <div className="db-stat-card">
                            <span className="stat-icon-db"></span>
                            <div className="stat-info-db">
                                <span className="stat-value-db">{statistics.database.shipments_count}</span>
                                <span className="stat-label-db">Shipments</span>
                            </div>
                        </div>
                        <div className="db-stat-card">
                            <span className="stat-icon-db"></span>
                            <div className="stat-info-db">
                                <span className="stat-value-db">{statistics.database.customers_count}</span>
                                <span className="stat-label-db">Customers</span>
                            </div>
                        </div>
                    </div>

                    {/* Table Sizes */}
                    <div className="tables-section">
                        <h3>Table Sizes</h3>
                        <div className="tables-grid">
                            {statistics.tables && statistics.tables.slice(0, 8).map((table, index) => (
                                <div key={index} className="table-size-card">
                                    <div className="table-name">{table.table_name}</div>
                                    <div className="table-sizes">
                                        <span className="size-item">
                                            <span className="size-label">Total:</span>
                                            <span className="size-value">{table.total_size}</span>
                                        </span>
                                        <span className="size-item">
                                            <span className="size-label">Data:</span>
                                            <span className="size-value">{table.table_size}</span>
                                        </span>
                                        <span className="size-item">
                                            <span className="size-label">Index:</span>
                                            <span className="size-value">{table.index_size}</span>
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Operations Panel */}
            <div className="operations-panel">
                <h2> Database Operations</h2>
                <div className="operations-grid">
                    <div className="operation-card">
                        <div className="operation-icon"></div>
                        <h3>Create Backup</h3>
                        <p>Create a full database backup for disaster recovery</p>
                        <div className="operation-actions">
                            <button
                                className="btn-operation"
                                onClick={() => handleCreateBackup('full')}
                                disabled={activeOperation === 'backup'}
                            >
                                {activeOperation === 'backup' ? ' Creating...' : ' Full Backup'}
                            </button>
                            <button
                                className="btn-operation secondary"
                                onClick={() => handleCreateBackup('partial')}
                                disabled={activeOperation === 'backup'}
                            >
                                 Partial Backup
                            </button>
                        </div>
                    </div>

                    <div className="operation-card">
                        <div className="operation-icon"></div>
                        <h3>Cleanup Temp Files</h3>
                        <p>Remove temporary files older than 7 days</p>
                        <button
                            className="btn-operation"
                            onClick={handleCleanup}
                            disabled={activeOperation === 'cleanup'}
                        >
                            {activeOperation === 'cleanup' ? ' Cleaning...' : ' Clean Up'}
                        </button>
                    </div>

                    <div className="operation-card">
                        <div className="operation-icon"></div>
                        <h3>Optimize Database</h3>
                        <p>Run ANALYZE, REINDEX, and VACUUM operations</p>
                        <button
                            className="btn-operation"
                            onClick={handleOptimize}
                            disabled={activeOperation === 'optimize'}
                        >
                            {activeOperation === 'optimize' ? ' Optimizing...' : ' Optimize'}
                        </button>
                    </div>

                    <div className="operation-card">
                        <div className="operation-icon"></div>
                        <h3>Refresh Data</h3>
                        <p>Reload database statistics and backup list</p>
                        <button
                            className="btn-operation"
                            onClick={loadData}
                            disabled={loading}
                        >
                            {loading ? ' Loading...' : ' Refresh'}
                        </button>
                    </div>
                </div>
            </div>

            {/* Backups List */}
            <div className="backups-section">
                <h2> Backup History</h2>
                {backups.length === 0 ? (
                    <div className="empty-backups">
                        <span className="empty-icon"></span>
                        <h3>No Backups Found</h3>
                        <p>Create your first backup to see it here</p>
                    </div>
                ) : (
                    <div className="backups-list">
                        {backups.map((backup, index) => (
                            <div key={index} className="backup-card">
                                <div className="backup-header">
                                    <span className="backup-id">#{backup.backup_id}</span>
                                    <span className={`backup-status ${backup.status}`}>
                                        {backup.status}
                                    </span>
                                </div>
                                <div className="backup-details">
                                    <div className="backup-info-row">
                                        <span className="info-label">Type:</span>
                                        <span className="info-value">{backup.type}</span>
                                    </div>
                                    <div className="backup-info-row">
                                        <span className="info-label">Size:</span>
                                        <span className="info-value">{backup.size_mb} MB</span>
                                    </div>
                                    <div className="backup-info-row">
                                        <span className="info-label">Created:</span>
                                        <span className="info-value">
                                            {new Date(backup.timestamp).toLocaleString()}
                                        </span>
                                    </div>
                                    {backup.completed_at && (
                                        <div className="backup-info-row">
                                            <span className="info-label">Completed:</span>
                                            <span className="info-value">
                                                {new Date(backup.completed_at).toLocaleString()}
                                            </span>
                                        </div>
                                    )}
                                </div>
                                {backup.error && (
                                    <div className="backup-error">
                                        <span className="error-icon"></span>
                                        <span className="error-text">{backup.error}</span>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Best Practices */}
            <div className="best-practices">
                <h3> Best Practices</h3>
                <ul className="practices-list">
                    <li> Create regular backups (recommended: daily)</li>
                    <li> Store backups in a secure, offsite location</li>
                    <li> Test backup restoration periodically</li>
                    <li> Run database optimization monthly</li>
                    <li> Clean up temporary files weekly</li>
                    <li> Monitor database size growth trends</li>
                </ul>
            </div>
        </div>
    );
};

export default DataManagement;
