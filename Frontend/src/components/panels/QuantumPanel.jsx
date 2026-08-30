// src/components/panels/QuantumPanel.jsx
import React from 'react';
import { Zap, Download, Maximize2 } from 'lucide-react';
import LoadingBlock from '../LoadingBlock';

const QuantumPanel = ({ systemState, isProcessing, isSystemReady, onOpenModal, onDownload, apiBaseUrl }) => {
    return (
        <div className="panel quantum-panel">
            <h2 className="panel-title">
                <Zap className="icon text-yellow" /> Quantum Execution Evidence
            </h2>
            <LoadingBlock loading={isProcessing} message="Executing the hybrid quantum-classical workload...">
                <div className="quantum-content">
                    {isSystemReady && systemState?.quantum_evidence_url ? (
                        <div className="evidence-wrapper">
                            <div className="image-container quantum-evidence">
                                <img
                                    src={`${apiBaseUrl}${systemState.quantum_evidence_url}`}
                                    alt="Quantum execution evidence"
                                    onClick={() => !isProcessing && onOpenModal(systemState.quantum_evidence_url)}
                                />
                            </div>
                            <div className="evidence-toolbar">
                                <button className="tool-btn" onClick={() => onDownload(systemState.quantum_evidence_url)} disabled={isProcessing}>
                                    <Download size={16} /> Download
                                </button>
                                <button className="tool-btn" onClick={() => onOpenModal(systemState.quantum_evidence_url)} disabled={isProcessing}>
                                    <Maximize2 size={16} /> Expand
                                </button>
                            </div>
                            <p className="success-msg">Hybrid quantum-classical execution completed successfully.</p>
                        </div>
                    ) : (
                        <div className="placeholder-quantum">
                            <span>Quantum execution evidence is not available.</span>
                        </div>
                    )}
                </div>
            </LoadingBlock>
        </div>
    );
};

export default QuantumPanel;
