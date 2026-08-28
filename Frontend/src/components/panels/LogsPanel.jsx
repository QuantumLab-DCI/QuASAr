// src/components/panels/LogsPanel.jsx
import React from 'react';
import { Terminal } from 'lucide-react';

const LogsPanel = ({ logs }) => {
    return (
        <div className="panel log-panel">
            <h2 className="panel-title"><Terminal className="icon" /> Logs del Sistema</h2>
            <pre className="log-box">{logs}</pre>
        </div>
    );
};

export default LogsPanel;
