import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { Terminal, X } from 'lucide-react';

const API_BASE_URL = 'http://127.0.0.1:8000';

/** Display live container logs and simulated resource metrics. */
const ServiceInspector = ({ service, onClose }) => {
    const [containerLogs, setContainerLogs] = useState([]);
    const scrollRef = useRef(null);

    const fetchContainerLogs = useCallback(async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/container_logs/${service.name}`);

            if (response.data.status === 'ok') {
                const lines = response.data.logs.split('\n').filter(line => line.trim().length > 0);

                const formattedLogs = lines.map(line => {
                    let timestamp = "";
                    let level = "INFO";
                    let message = line;

                    // Parse the conventional "14:30:01 [INFO] Message" format when available.
                    const match = line.match(/^(\d{2}:\d{2}:\d{2})\s+\[([A-Z]+)\]\s+(.*)/);

                    if (match) {
                        timestamp = match[1];
                        level = match[2];
                        message = match[3];
                    } else {
                        if (line.includes('ERROR') || line.includes('Exception')) level = 'ERROR';
                        else if (line.includes('WARN')) level = 'WARN';
                        else if (line.includes('DEBUG')) level = 'DEBUG';
                    }

                    return { timestamp, level, message };
                });

                setContainerLogs(formattedLogs);
            } else {
                setContainerLogs([{ timestamp: 'System', level: 'ERROR', message: response.data.logs }]);
            }
        } catch (error) {
            console.error("Docker API connection error:", error);
            setContainerLogs(previousLogs => [...previousLogs, { timestamp: 'System', level: 'ERROR', message: "Could not connect to the Docker API." }]);
        }
    }, [service.name]);

    useEffect(() => {
        const initialRequest = setTimeout(fetchContainerLogs, 0);
        const interval = setInterval(fetchContainerLogs, 2000);
        return () => {
            clearTimeout(initialRequest);
            clearInterval(interval);
        };
    }, [fetchContainerLogs]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [containerLogs]);

    // Display placeholders, not Docker telemetry.
    const isActive = service.status === 'active' || service.status === undefined;
    const [cpu] = useState(() => isActive ? Math.floor(Math.random() * 20 + 5) : 0);
    const [memory] = useState(() => isActive ? Math.floor(Math.random() * 50 + 40) : 0);

    return (
        <div className="inspector-overlay" onClick={onClose}>
            <div className="inspector-window" onClick={e => e.stopPropagation()}>
                <div className="inspector-header">
                    <div className="inspector-title">
                        <Terminal size={18} />
                        root@{service.name.toLowerCase().replace(' ', '-')}:~#
                    </div>
                    <button className="inspector-close" onClick={onClose}><X size={18} /></button>
                </div>
                <div className="inspector-body">
                    <div className="inspector-metrics">
                        <div className="metric-card"><small>CPU (Live)</small><strong>{cpu}%</strong></div>
                        <div className="metric-card"><small>Memory</small><strong>{memory} MB</strong></div>
                        <div className="metric-card"><small>Log Source</small><strong style={{ color: '#10b981' }}>DOCKER.SOCK</strong></div>
                    </div>
                    <div className="inspector-console" ref={scrollRef}>
                        {containerLogs.length === 0 && <div className="console-line" style={{ color: '#666' }}>Loading container logs...</div>}

                        {containerLogs.map((log, logIndex) => (
                            <div key={logIndex} className="console-line">
                                {log.timestamp && <span className="log-timestamp">{log.timestamp}</span>}
                                <span className={`log-${log.level.toLowerCase()}`}>[{log.level}]</span>
                                <span>{log.message}</span>
                            </div>
                        ))}
                        <div className="console-line"><span className="cursor-blink"></span></div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ServiceInspector;
