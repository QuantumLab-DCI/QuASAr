// src/components/panels/MapekHistoryPanel.jsx
import React from 'react';
import { Activity, Brain, GitMerge, Box, CheckCircle, Info } from 'lucide-react';
import LoadingBlock from '../LoadingBlock';

const getPhaseIcon = (fase) => {
    if (fase.includes("MONITOR")) return <Activity size={16} />;
    if (fase.includes("ANÁLISIS")) return <Brain size={16} />;
    if (fase.includes("PLAN")) return <GitMerge size={16} />;
    if (fase.includes("EJECUCIÓN")) return <Box size={16} />;
    if (fase.includes("FIN")) return <CheckCircle size={16} />;
    return <Info size={16} />;
};

const MapekHistoryPanel = ({ mapekTrace, isProcessing }) => {
    return (
        <div className="panel mapek-panel">
            <h2 className="panel-title">🔄 Historial de Adaptación</h2>
            <LoadingBlock loading={isProcessing} message="Registrando eventos...">
                <div className="mapek-timeline">
                    {mapekTrace?.map((paso, index) => (
                        <div key={index} className="mapek-step">
                            <div className="step-header">
                                <div className="step-meta">
                                    {getPhaseIcon(paso.fase)}
                                    <span className="step-time">{paso.timestamp}</span>
                                </div>
                                <span className={`step-badge phase-${paso.fase.split(' ')[0].toLowerCase()}`}>
                                    {paso.fase}
                                </span>
                            </div>
                            <p className="step-msg">{paso.mensaje}</p>
                        </div>
                    ))}
                </div>
            </LoadingBlock>
        </div>
    );
};

export default MapekHistoryPanel;
