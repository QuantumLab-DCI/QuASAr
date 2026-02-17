// src/components/panels/MetricsPanel.jsx
import React from 'react';
import LoadingBlock from '../LoadingBlock';

const MetricsPanel = ({ contexto, isProcessing, isSystemReady }) => {
    return (
        <div className="panel context-panel">
            <h2 className="panel-title">Sensores del Entorno</h2>
            <LoadingBlock loading={isProcessing} message="Leyendo sensores...">
                {isSystemReady && contexto ? (
                    <div>
                        <div className="metrics-list">
                            <div className="metric-item">
                                <span className="metric-label">Calidad Aire (ICA)</span>
                                <span className="metric-value color-ica">{contexto.calidad_aire_ica}</span>
                            </div>
                            <div className="metric-item">
                                <span className="metric-label">Complejidad (CP)</span>
                                <span className="metric-value color-cp">{contexto.complejidad_problema_cp}</span>
                            </div>
                            <div className="metric-item">
                                <span className="metric-label">SLA Prioridad</span>
                                <span className="metric-value color-sla">{contexto.prioridad_sla}</span>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="p-4 text-center text-gray-400 text-sm">Sin datos.</div>
                )}
            </LoadingBlock>
        </div>
    );
};

export default MetricsPanel;
