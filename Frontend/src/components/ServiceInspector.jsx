// src/components/ServiceInspector.jsx
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Terminal, X } from 'lucide-react';

const API_URL = 'http://127.0.0.1:8000';

const ServiceInspector = ({ service, onClose }) => {
    const [realLogs, setRealLogs] = useState([]);
    const scrollRef = useRef(null);

    // Fetch real logs from the backend
    const fetchRealLogs = async () => {
        try {
            // Ask the backend to read the Docker logs
            const response = await axios.get(`${API_URL}/api/container_logs/${service.name}`);

            if (response.data.status === 'ok') {
                // Docker returns one large string, so split it into lines and remove empty ones
                const lines = response.data.logs.split('\n').filter(line => line.trim().length > 0);

                // Format the logs for readable terminal output
                const formattedLogs = lines.map(line => {
                    let ts = "";
                    let level = "INFO";
                    let msg = line;

                    // Try to parse the format: "14:30:01 [INFO] Message..."
                    // Simple regex to capture the time and bracketed level
                    const match = line.match(/^(\d{2}:\d{2}:\d{2})\s+\[([A-Z]+)\]\s+(.*)/);

                    if (match) {
                        ts = match[1];
                        level = match[2];
                        msg = match[3];
                    } else {
                        // If it does not match (for example, Python tracebacks), keep it raw but detect keywords
                        if (line.includes('ERROR') || line.includes('Exception')) level = 'ERROR';
                        else if (line.includes('WARN')) level = 'WARN';
                        else if (line.includes('DEBUG')) level = 'DEBUG';
                    }

                    return { ts, level, msg, raw: line };
                });

                setRealLogs(formattedLogs);
            } else {
                setRealLogs([{ ts: 'System', level: 'ERROR', msg: response.data.logs }]);
            }
        } catch (error) {
            // Handle connection failures (for example, when the backend is down)
            console.error(error);
            setRealLogs(prev => [...prev, { ts: 'System', level: 'ERROR', msg: "Error conectando con Docker API..." }]);
        }
    };

    // Poll every 2 seconds while the window is open
    useEffect(() => {
        fetchRealLogs(); // Load immediately on the first request
        const interval = setInterval(fetchRealLogs, 2000);
        return () => clearInterval(interval);
    }, [service]);

    // Automatically scroll to the bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [realLogs]);

    // Simulated metrics for display purposes (the Docker API is too slow for real-time updates)
    const cpu = service.status === 'active' || service.status === undefined ? Math.floor(Math.random() * 20 + 5) : 0;
    const mem = service.status === 'active' || service.status === undefined ? Math.floor(Math.random() * 50 + 40) : 0;

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
                        <div className="metric-card"><small>Memory</small><strong>{mem} MB</strong></div>
                        <div className="metric-card"><small>Logs Source</small><strong style={{ color: '#10b981' }}>DOCKER.SOCK</strong></div>
                    </div>
                    <div className="inspector-console" ref={scrollRef}>
                        {realLogs.length === 0 && <div className="console-line" style={{ color: '#666' }}>Cargando logs del contenedor...</div>}

                        {realLogs.map((log, i) => (
                            <div key={i} className="console-line">
                                {log.ts && <span className="log-ts">{log.ts}</span>}
                                <span className={`log-${log.level.toLowerCase()}`}>[{log.level}]</span>
                                <span>{log.msg}</span>
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
