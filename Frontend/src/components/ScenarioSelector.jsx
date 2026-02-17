import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Cloud, AlertTriangle, Clock, CheckCircle, Play, Loader2, Lock } from 'lucide-react';

// Asegúrate de que coincida con tu backend (localhost o 127.0.0.1)
const API_URL = 'http://127.0.0.1:8000';

// Recibimos isSystemBusy como prop desde App.jsx para bloquear la UI
const ScenarioSelector = ({ onScenarioChange, isSystemBusy }) => {
    const [scenarios, setScenarios] = useState([]);
    const [activeId, setActiveId] = useState(null);
    const [error, setError] = useState(null);

    // 1. Cargar escenarios al montar el componente
    useEffect(() => {
        const loadScenarios = async () => {
            try {
                const res = await axios.get(`${API_URL}/api/escenarios`);
                setScenarios(res.data);
            } catch (err) {
                console.error("Error cargando escenarios:", err);
                setError("No se pudieron cargar los escenarios del backend.");
            }
        };
        loadScenarios();
    }, []);

    // 2. Manejar el clic en un escenario
    const handleSelect = async (id) => {
        // Bloqueo de seguridad frontend: si está ocupado, no hacemos nada
        if (isSystemBusy) return;

        try {
            const res = await axios.post(`${API_URL}/api/seleccionar_escenario`, { id: id });
            if (res.data.status === 'ok') {
                setActiveId(id);
                // Avisamos al componente padre (App) para que refresque el estado
                if (onScenarioChange) onScenarioChange();
            }
        } catch (err) {
            console.error("Error seleccionando escenario:", err);
            // Manejamos el error 423 (Locked) específicamente por si el bloqueo visual falla
            if (err.response && err.response.status === 423) {
                alert("⚠️ El sistema está ocupado procesando una solicitud. Por favor espera.");
            } else {
                alert("Error al cambiar de escenario. Revisa la consola.");
            }
        }
    };

    // Helper para iconos visuales
    const getIcon = (id) => {
        switch (id) {
            case 1: return <Activity size={20} className="icon-green" />; // Base
            case 2: return <AlertTriangle size={20} className="icon-orange" />; // Alerta
            case 3: return <Cloud size={20} className="icon-blue" />; // Qiskit
            case 4: return <Clock size={20} className="icon-purple" />; // Cirq
            case 5: case 99: return <AlertTriangle size={20} style={{ color: 'red' }} />; // Caos/Evento X
            default: return <Play size={20} className="icon-gray" />;
        }
    };

    // Helper para formatear el SLA (Manejo de fallback por si la clave cambia en backend)
    const getSlaLabel = (scenario) => scenario.sla_prioridad || scenario.sla || "N/A";

    if (error) return <div className="error-msg">{error}</div>;

    return (
        <div className={`scenario-panel ${isSystemBusy ? 'panel-blocked' : ''}`}>
            <div className="scenario-header">
                <div className="flex items-center gap-2" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <h2>🕹️ Panel de Control (Simulación Estocástica)</h2>

                    {/* Indicador de Estado del Sistema */}
                    {isSystemBusy ? (
                        <span className="status-badge processing">
                            <Loader2 size={14} className="spin-icon" />
                            PROCESANDO CICLO MAPE-K...
                        </span>
                    ) : (
                        <span className="status-badge ready pulse-green">
                            <span className="dot-indicator"></span>
                            SISTEMA ACTIVO
                        </span>
                    )}
                </div>
            </div>

            <div className="scenario-grid">
                {scenarios.map((scenario) => (
                    <div
                        key={scenario.id}
                        onClick={() => handleSelect(scenario.id)}
                        className={`scenario-card 
                            ${activeId === scenario.id ? 'active' : ''} 
                            ${isSystemBusy ? 'disabled-card' : ''}
                        `}
                    >
                        {/* Overlay de bloqueo (Candado) */}
                        {isSystemBusy && (
                            <div className="card-overlay">
                                <Lock size={32} className="lock-icon" />
                            </div>
                        )}

                        {activeId === scenario.id && !isSystemBusy && (
                            <div className="active-badge glow-effect">
                                <CheckCircle size={14} /> ACTIVO
                            </div>
                        )}

                        <div className="card-content">
                            <div className="card-header">
                                <div className={`icon-wrapper icon-wrapper-${scenario.id}`}>
                                    {getIcon(scenario.id)}
                                </div>
                                <h3>{scenario.nombre}</h3>
                            </div>

                            <p className="card-desc">{scenario.descripcion}</p>

                            <div className="card-footer">
                                <div className="metrics-row">
                                    <span className="metric-pill">
                                        <span className="metric-label">ICA</span>
                                        <span className="metric-val">{scenario.rango_ica ? `${scenario.rango_ica[0]}-${scenario.rango_ica[1]}` : scenario.ica}</span>
                                    </span>
                                    <span className="metric-pill">
                                        <span className="metric-label">CP</span>
                                        <span className="metric-val">{scenario.rango_cp ? `${scenario.rango_cp[0]}-${scenario.rango_cp[1]}` : scenario.cp}</span>
                                    </span>
                                </div>
                                <span className={`sla-badge sla-${getSlaLabel(scenario).toLowerCase()}`}>
                                    {getSlaLabel(scenario)}
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ScenarioSelector;