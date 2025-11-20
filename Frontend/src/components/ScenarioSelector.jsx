import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Cloud, AlertTriangle, Clock, CheckCircle, Play } from 'lucide-react';

// Asegúrate de que coincida con tu backend (localhost o 127.0.0.1)
const API_URL = 'http://127.0.0.1:8000';

const ScenarioSelector = ({ onScenarioChange }) => {
    const [scenarios, setScenarios] = useState([]);
    const [activeId, setActiveId] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // 1. Cargar escenarios al montar el componente
    useEffect(() => {
        const loadScenarios = async () => {
            try {
                const res = await axios.get(`${API_URL}/api/escenarios`);
                setScenarios(res.data);
                // Opcional: Podrías consultar /api/estado para ver cuál está activo al inicio
            } catch (err) {
                console.error("Error cargando escenarios:", err);
                setError("No se pudieron cargar los escenarios del backend.");
            }
        };
        loadScenarios();
    }, []);

    // 2. Manejar el clic en un escenario
    const handleSelect = async (id) => {
        if (loading) return;
        setLoading(true);

        try {
            const res = await axios.post(`${API_URL}/api/seleccionar_escenario`, { id: id });
            if (res.data.status === 'ok') {
                setActiveId(id);
                // Avisamos al componente padre (App) para que refresque el estado
                if (onScenarioChange) onScenarioChange();
            }
        } catch (err) {
            console.error("Error seleccionando escenario:", err);
            alert("Error al cambiar de escenario. Revisa la consola.");
        } finally {
            setLoading(false);
        }
    };

    // Helper para iconos visuales
    const getIcon = (id) => {
        switch (id) {
            case 1: return <Activity size={20} className="icon-green" />; // Base
            case 2: return <AlertTriangle size={20} className="icon-orange" />; // Alerta
            case 3: return <Cloud size={20} className="icon-blue" />; // Qiskit
            case 4: return <Clock size={20} className="icon-purple" />; // Cirq
            default: return <Play size={20} className="icon-gray" />;
        }
    };

    if (error) return <div className="error-msg">{error}</div>;

    return (
        <div className="scenario-panel">
            <div className="scenario-header">
                <h2>🕹️ Panel de Control (Tesis HQC)</h2>
                {loading && <span className="loading-badge">⏳ Reconfigurando... (10s)</span>}
            </div>

            <div className="scenario-grid">
                {scenarios.map((scenario) => (
                    <div
                        key={scenario.id}
                        onClick={() => handleSelect(scenario.id)}
                        className={`scenario-card ${activeId === scenario.id ? 'active' : ''} ${loading ? 'disabled' : ''}`}
                    >
                        {activeId === scenario.id && (
                            <div className="active-badge"><CheckCircle size={12} /> ACTIVO</div>
                        )}

                        <div className="card-header">
                            <div className="icon-wrapper">{getIcon(scenario.id)}</div>
                            <h3>{scenario.nombre}</h3>
                        </div>

                        <p className="card-desc">{scenario.descripcion}</p>

                        <div className="card-metrics">
                            <span className="metric-tag">ICA: {scenario.ica}</span>
                            <span className="metric-tag">CP: {scenario.cp}</span>
                            <span className={`metric-tag sla-${scenario.sla.toLowerCase()}`}>
                                {scenario.sla}
                            </span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ScenarioSelector;