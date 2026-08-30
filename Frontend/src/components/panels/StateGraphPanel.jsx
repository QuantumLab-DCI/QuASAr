// src/components/panels/StateGraphPanel.jsx
import React from 'react';
import { Network, Info } from 'lucide-react';
import LoadingBlock from '../LoadingBlock';

const StateGraphPanel = ({ systemState, isProcessing, isSystemReady, onOpenModal, apiBaseUrl }) => {
    return (
        <div className="panel graph-panel">
            <h2 className="panel-title"><Network className="icon" /> Current Configuration (DSPL)</h2>
            <LoadingBlock loading={isProcessing} message="Reconfiguring the system architecture...">
                <div className="image-container state-graph">
                    {isSystemReady && systemState?.state_image_url ? (
                        <img
                            src={`${apiBaseUrl}${systemState.state_image_url}`}
                            alt="Current self-adaptive system configuration graph"
                            className="clickable-image"
                            onClick={() => !isProcessing && onOpenModal(systemState.state_image_url)}
                        />
                    ) : (
                        <div className="placeholder-state">
                            <Info size={40} className="text-gray-300 mb-2" />
                            <p className="text-gray-400">No active configuration is available.</p>
                        </div>
                    )}
                </div>
            </LoadingBlock>
        </div>
    );
};

export default StateGraphPanel;
