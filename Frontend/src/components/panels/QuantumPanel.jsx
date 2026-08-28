// src/components/panels/QuantumPanel.jsx
import React from 'react';
import { Zap, Download, Maximize2 } from 'lucide-react';
import LoadingBlock from '../LoadingBlock';

const QuantumPanel = ({ estado, isProcessing, isSystemReady, onOpenModal, onDownload, API_URL }) => {
    return (
        <div className="panel quantum-panel">
            <h2 className="panel-title">
                <Zap className="icon text-yellow" /> Evidencia de Ejecución Cuántica
            </h2>
            <LoadingBlock loading={isProcessing} message="Compilando Circuito...">
                <div className="quantum-content">
                    {isSystemReady && estado?.evidencia_cuantica_url ? (
                        <div className="evidence-wrapper">
                            <div className="image-container quantum-evidence">
                                <img
                                    src={`${API_URL}${estado.evidencia_cuantica_url}`}
                                    alt="Circuito Cuántico"
                                    onClick={() => !isProcessing && onOpenModal(estado.evidencia_cuantica_url)}
                                />
                            </div>
                            <div className="evidence-toolbar">
                                <button className="tool-btn" onClick={() => onDownload(estado.evidencia_cuantica_url)} disabled={isProcessing}>
                                    <Download size={16} /> Descargar
                                </button>
                                <button className="tool-btn" onClick={() => onOpenModal(estado.evidencia_cuantica_url)} disabled={isProcessing}>
                                    <Maximize2 size={16} /> Ampliar
                                </button>
                            </div>
                            <p className="success-msg">✅ Ejecución exitosa en Backend HQC</p>
                        </div>
                    ) : (
                        <div className="placeholder-quantum">
                            <span>💤 Módulo Cuántico Inactivo</span>
                        </div>
                    )}
                </div>
            </LoadingBlock>
        </div>
    );
};

export default QuantumPanel;
