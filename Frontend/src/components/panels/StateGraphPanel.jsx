// src/components/panels/StateGraphPanel.jsx
import React from 'react';
import { Network, Info } from 'lucide-react';
import LoadingBlock from '../LoadingBlock';

const StateGraphPanel = ({ estado, isProcessing, isSystemReady, onOpenModal, API_URL }) => {
    return (
        <div className="panel graph-panel">
            <h2 className="panel-title"><Network className="icon" /> Estado Actual (LPSD)</h2>
            <LoadingBlock loading={isProcessing} message="Reconfigurando Arquitectura...">
                <div className="image-container state-graph">
                    {isSystemReady && estado?.imagen_estado_url ? (
                        <img
                            src={`${API_URL}${estado.imagen_estado_url}`}
                            alt="Grafo de Estado"
                            className="clickable-image"
                            onClick={() => !isProcessing && onOpenModal(estado.imagen_estado_url)}
                        />
                    ) : (
                        <div className="placeholder-state">
                            <Info size={40} className="text-gray-300 mb-2" />
                            <p className="text-gray-400">Sin arquitectura activa.</p>
                        </div>
                    )}
                </div>
            </LoadingBlock>
        </div>
    );
};

export default StateGraphPanel;
