// src/components/panels/MonitoredContextPanel.jsx
import React from 'react';
import LoadingBlock from '../LoadingBlock';

const MonitoredContextPanel = ({ context, isProcessing, isSystemReady }) => {
    return (
        <div className="panel context-panel">
            <h2 className="panel-title">Monitored Context</h2>
            <LoadingBlock loading={isProcessing} message="Collecting context observations...">
                {isSystemReady && context ? (
                    <div>
                        <div className="metrics-list">
                            <div className="metric-item">
                                <span className="metric-label">Air Quality Index (AQI)</span>
                                <span className="metric-value color-aqi">{context.air_quality_index}</span>
                            </div>
                            <div className="metric-item">
                                <span className="metric-label">Problem Complexity</span>
                                <span className="metric-value color-complexity">{context.problem_complexity}</span>
                            </div>
                            <div className="metric-item">
                                <span className="metric-label">SLA Priority</span>
                                <span className="metric-value color-sla">{context.sla_priority}</span>
                            </div>
                            <div className="metric-item">
                                <span className="metric-label">Qiskit Queue Time</span>
                                <span className="metric-value">{context.qiskit_queue_time ?? 'N/A'} s</span>
                            </div>
                            <div className="metric-item">
                                <span className="metric-label">User Profile</span>
                                <span className="metric-value">{context.user_profile ?? 'N/A'}</span>
                            </div>
                            <div className="metric-item">
                                <span className="metric-label">Scenario</span>
                                <span className="metric-value">{context.scenario_name ?? 'N/A'}</span>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="p-4 text-center text-gray-400 text-sm">No monitored context is available.</div>
                )}
            </LoadingBlock>
        </div>
    );
};

export default MonitoredContextPanel;
