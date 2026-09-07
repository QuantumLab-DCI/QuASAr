import React from 'react';
import { Activity, Brain, GitMerge, Box, Info } from 'lucide-react';
import LoadingBlock from '../LoadingBlock';

const getPhaseIcon = (phase) => {
    if (phase === "MONITOR") return <Activity size={16} />;
    if (phase === "ANALYZE") return <Brain size={16} />;
    if (phase === "PLAN") return <GitMerge size={16} />;
    if (phase === "EXECUTE") return <Box size={16} />;
    return <Info size={16} />;
};

const AdaptationTracePanel = ({ mapekTrace, isProcessing }) => {
    return (
        <div className="panel mapek-panel">
            <h2 className="panel-title">Adaptation Trace</h2>
            <LoadingBlock loading={isProcessing} message="Recording MAPE-K events...">
                <div className="mapek-timeline">
                    {mapekTrace?.map((traceEvent, index) => (
                        <div key={index} className="mapek-step">
                            <div className="step-header">
                                <div className="step-meta">
                                    {getPhaseIcon(traceEvent.phase)}
                                    <span className="step-time">{traceEvent.timestamp}</span>
                                </div>
                                <span className={`step-badge phase-${traceEvent.phase.toLowerCase()}`}>
                                    {traceEvent.phase.charAt(0) + traceEvent.phase.slice(1).toLowerCase()}
                                </span>
                            </div>
                            <p className="step-msg">{traceEvent.message}</p>
                        </div>
                    ))}
                </div>
            </LoadingBlock>
        </div>
    );
};

export default AdaptationTracePanel;
