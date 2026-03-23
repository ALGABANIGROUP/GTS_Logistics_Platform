// src/components/bots/panels/customer-service/CallManager.jsx
import React, { useState, useEffect } from 'react';
import { customerServiceAPI } from '../../../../services/customerService';
import './CallManager.css';

const CallManager = ({ onNotification }) => {
    const [activeCalls, setActiveCalls] = useState([]);
    const [selectedCall, setSelectedCall] = useState(null);
    const [callHistory, setCallHistory] = useState([]);
    const [dialerOpen, setDialerOpen] = useState(false);
    const [dialNumber, setDialNumber] = useState('');
    const [callStats, setCallStats] = useState({
        totalCalls: 0,
        avgDuration: '0m',
        answeredRate: '0%',
        satisfaction: '0%'
    });
    const [recordingActive, setRecordingActive] = useState(false);
    const [holdActive, setHoldActive] = useState(false);
    const [showDTMF, setShowDTMF] = useState(false);

    useEffect(() => {
        loadCallData();
        const interval = setInterval(loadCallData, 10000);
        return () => clearInterval(interval);
    }, []);

    const loadCallData = async () => {
        try {
            const [calls, history, stats] = await Promise.all([
                customerServiceAPI.getActiveCalls(),
                customerServiceAPI.getCallHistory(),
                customerServiceAPI.getCallStats()
            ]);

            setActiveCalls(calls);
            setCallHistory(history);
            setCallStats(stats);
        } catch (error) {
            console.error('Failed to load call data:', error);
        }
    };

    const makeCall = async () => {
        if (!dialNumber.trim()) return;

        try {
            const newCall = {
                id: Date.now(),
                number: dialNumber,
                duration: '00:00',
                status: 'dialing',
                timestamp: new Date().toLocaleTimeString()
            };

            setActiveCalls([...activeCalls, newCall]);
            setSelectedCall(newCall);
            setDialNumber('');
            setDialerOpen(false);
            onNotification(`Calling ${dialNumber}`, '');

            // Simulate call connection
            setTimeout(() => {
                setActiveCalls(prev =>
                    prev.map(call =>
                        call.id === newCall.id ? { ...call, status: 'connected' } : call
                    )
                );
                setSelectedCall(prev => prev ? { ...prev, status: 'connected' } : null);
            }, 3000);
        } catch (error) {
            console.error('Failed to make call:', error);
        }
    };

    const endCall = async (callId) => {
        try {
            setActiveCalls(prev => prev.filter(call => call.id !== callId));
            if (selectedCall?.id === callId) {
                setSelectedCall(null);
            }
            onNotification('Call ended', '');
        } catch (error) {
            console.error('Failed to end call:', error);
        }
    };

    const transferCall = async () => {
        if (!selectedCall) return;
        try {
            await customerServiceAPI.transferCall(selectedCall.id, 'agent_001');
            onNotification(`Call transferred to agent`, '');
        } catch (error) {
            console.error('Failed to transfer call:', error);
        }
    };

    const toggleRecording = async () => {
        if (!selectedCall) return;
        try {
            if (!recordingActive) {
                await customerServiceAPI.startRecording(selectedCall.id);
                onNotification('Call recording started', '');
            } else {
                onNotification('Call recording stopped', '');
            }
            setRecordingActive(!recordingActive);
        } catch (error) {
            console.error('Failed to toggle recording:', error);
        }
    };

    const toggleHold = async () => {
        try {
            setHoldActive(!holdActive);
            onNotification(holdActive ? 'Call resumed' : 'Call on hold', '');
        } catch (error) {
            console.error('Failed to toggle hold:', error);
        }
    };

    const sendDTMF = (digit) => {
        if (!selectedCall) return;
        try {
            onNotification(`Sent: ${digit}`, '');
        } catch (error) {
            console.error('Failed to send DTMF:', error);
        }
    };

    const dtmfPad = [
        ['1', '2', '3'],
        ['4', '5', '6'],
        ['7', '8', '9'],
        ['*', '0', '#']
    ];

    return (
        <div className="call-manager">
            <div className="call-manager-grid">
                {/* Calls Panel */}
                <div className="calls-panel">
                    <div className="panel-header">
                        <h3> Active Calls</h3>
                        <button
                            className="new-call-btn"
                            onClick={() => setDialerOpen(true)}
                        >
                             New Call
                        </button>
                    </div>

                    <div className="active-calls-list">
                        {activeCalls.length > 0 ? (
                            activeCalls.map((call) => (
                                <div
                                    key={call.id}
                                    className={`call-item ${selectedCall?.id === call.id ? 'active' : ''} ${call.status}`}
                                    onClick={() => setSelectedCall(call)}
                                >
                                    <div className="call-info">
                                        <div className="call-number">{call.number}</div>
                                        <div className="call-status">{call.status}</div>
                                    </div>
                                    <div className="call-duration">{call.duration}</div>
                                    <button
                                        className="end-call-btn"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            endCall(call.id);
                                        }}
                                    >
                                        
                                    </button>
                                </div>
                            ))
                        ) : (
                            <div className="empty-state">No active calls</div>
                        )}
                    </div>

                    {/* Dialer Modal */}
                    {dialerOpen && (
                        <div className="dialer-modal">
                            <div className="dialer-content">
                                <h3>Make a Call</h3>
                                <input
                                    type="tel"
                                    value={dialNumber}
                                    onChange={(e) => setDialNumber(e.target.value)}
                                    placeholder="Enter phone number"
                                    className="dialer-input"
                                    autoFocus
                                />
                                <div className="dialer-buttons">
                                    <button
                                        className="call-btn"
                                        onClick={makeCall}
                                        disabled={!dialNumber.trim()}
                                    >
                                         Call
                                    </button>
                                    <button
                                        className="cancel-btn"
                                        onClick={() => {
                                            setDialerOpen(false);
                                            setDialNumber('');
                                        }}
                                    >
                                         Cancel
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Stats */}
                    <div className="call-stats">
                        <div className="stat">
                            <span className="label">Total Calls</span>
                            <span className="value">{callStats.totalCalls}</span>
                        </div>
                        <div className="stat">
                            <span className="label">Avg Duration</span>
                            <span className="value">{callStats.avgDuration}</span>
                        </div>
                        <div className="stat">
                            <span className="label">Answered Rate</span>
                            <span className="value">{callStats.answeredRate}</span>
                        </div>
                        <div className="stat">
                            <span className="label">Satisfaction</span>
                            <span className="value">{callStats.satisfaction}</span>
                        </div>
                    </div>
                </div>

                {/* Call Controls */}
                <div className="call-controls-panel">
                    {selectedCall ? (
                        <>
                            <div className="current-call">
                                <h3>Current Call</h3>
                                <div className="call-details">
                                    <div className="detail">
                                        <span className="label">Number:</span>
                                        <span className="value">{selectedCall.number}</span>
                                    </div>
                                    <div className="detail">
                                        <span className="label">Status:</span>
                                        <span className={`value ${selectedCall.status}`}>{selectedCall.status}</span>
                                    </div>
                                    <div className="detail">
                                        <span className="label">Duration:</span>
                                        <span className="value">{selectedCall.duration}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Call Controls */}
                            <div className="controls-section">
                                <h4>Call Controls</h4>
                                <div className="controls-grid">
                                    <button
                                        className={`control-btn ${recordingActive ? 'active' : ''}`}
                                        onClick={toggleRecording}
                                        title="Toggle Recording"
                                    >
                                        {recordingActive ? '' : ''} Record
                                    </button>
                                    <button
                                        className={`control-btn ${holdActive ? 'active' : ''}`}
                                        onClick={toggleHold}
                                        title="Hold Call"
                                    >
                                         Hold
                                    </button>
                                    <button
                                        className="control-btn"
                                        onClick={transferCall}
                                        title="Transfer Call"
                                    >
                                         Transfer
                                    </button>
                                    <button
                                        className="control-btn danger"
                                        onClick={() => selectedCall && endCall(selectedCall.id)}
                                        title="End Call"
                                    >
                                         End
                                    </button>
                                </div>
                            </div>

                            {/* DTMF Pad */}
                            <div className="dtmf-section">
                                <button
                                    className="dtmf-toggle"
                                    onClick={() => setShowDTMF(!showDTMF)}
                                >
                                    {showDTMF ? '' : ''} DTMF Keypad
                                </button>
                                {showDTMF && (
                                    <div className="dtmf-pad">
                                        {dtmfPad.map((row, rowIdx) => (
                                            <div key={rowIdx} className="dtmf-row">
                                                {row.map((digit) => (
                                                    <button
                                                        key={digit}
                                                        className="dtmf-btn"
                                                        onClick={() => sendDTMF(digit)}
                                                    >
                                                        {digit}
                                                    </button>
                                                ))}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </>
                    ) : (
                        <div className="empty-state">
                            <span className="icon"></span>
                            <h3>No Active Call</h3>
                            <p>Select a call or start a new one</p>
                        </div>
                    )}
                </div>

                {/* Call History */}
                <div className="call-history-panel">
                    <h3> Call History</h3>
                    <div className="history-list">
                        {callHistory.length > 0 ? (
                            callHistory.map((call) => (
                                <div key={call.id} className="history-item">
                                    <div className="history-icon">
                                        {call.type === 'inbound' ? '' : ''}
                                    </div>
                                    <div className="history-content">
                                        <div className="history-number">{call.number}</div>
                                        <div className="history-time">{call.timestamp}</div>
                                        <div className="history-duration">{call.duration}</div>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="empty-state">No call history</div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CallManager;
