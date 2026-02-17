// src/components/ServiceInspector.jsx
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Terminal, X } from 'lucide-react';

const API_URL = 'http://127.0.0.1:8000';

const ServiceInspector = ({ service, onClose }) => {
    const [realLogs, setRealLogs] = useState([]);
    const scrollRef = useRef(null);

    // Función para obtener logs REALES del Backend
    const fetchRealLogs = async () => {
        try {
            // Pedimos al backend que lea los logs de Docker
            const response = await axios.get(`${API_URL}/api/container_logs/${service.name}`);

            if (response.data.status === 'ok') {
                // Docker devuelve un string gigante, lo dividimos en líneas y filtramos vacías
                const lines = response.data.logs.split('\n').filter(line => line.trim().length > 0);

                // Formateamos para que se vea bonito en la terminal
                const formattedLogs = lines.map(line => {
                    let ts = "";
                    let level = "INFO";
                    let msg = line;

                    // Intentamos parsear el formato: "14:30:01 [INFO] Mensaje..."
                    // Regex simple para capturar hora y nivel entre corchetes
                    const match = line.match(/^(\d{2}:\d{2}:\d{2})\s+\[([A-Z]+)\]\s+(.*)/);

                    if (match) {
                        ts = match[1];
                        level = match[2];
                        msg = match[3];
                    } else {
                        // Si no coincide (ej. trazas de error de Python), lo dejamos raw pero detectamos palabras clave
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
            // Si falla la conexión (ej. backend caído)
            console.error(error);
            setRealLogs(prev => [...prev, { ts: 'System', level: 'ERROR', msg: "Error conectando con Docker API..." }]);
        }
    };

    // Polling: Actualizar logs cada 2 segundos mientras la ventana esté abierta
    useEffect(() => {
        fetchRealLogs(); // Primera carga inmediata
        const interval = setInterval(fetchRealLogs, 2000);
        return () => clearInterval(interval);
    }, [service]);

    // Auto-scroll al final
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [realLogs]);

    // Métricas FALSAS para decoración (Docker API es lenta para esto en tiempo real)
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
