import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, Cloud, AlertTriangle, Clock, CheckCircle, Play, Loader2, Lock } from 'lucide-react';

const API_BASE_URL = 'http://127.0.0.1:8000';

const ScenarioSelector = ({ onScenarioChange, isSystemBusy }) => {
    const [scenarios, setScenarios] = useState([]);
    const [activeScenarioId, setActiveScenarioId] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadScenarios = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/api/scenarios`);
                setScenarios(response.data);
            } catch (requestError) {
                console.error("Scenario loading error:", requestError);
                setError("The scenarios could not be loaded from the backend.");
            }
        };
        loadScenarios();
    }, []);

    const handleSelect = async (scenarioId) => {
        if (isSystemBusy) return;

        try {
            const response = await axios.post(`${API_BASE_URL}/api/select-scenario`, { scenario_id: scenarioId });
            if (response.data.status === 'ok') {
                setActiveScenarioId(scenarioId);
                if (onScenarioChange) onScenarioChange();
            }
        } catch (requestError) {
            console.error("Scenario selection error:", requestError);
            if (requestError.response && requestError.response.status === 423) {
                alert("The system is processing an adaptation request. Please wait for the current cycle to finish.");
            } else {
                alert("The scenario could not be changed. See the browser console for details.");
            }
        }
    };

    const getIcon = (scenarioId) => {
        switch (scenarioId) {
            case 1: return <Activity size={20} className="icon-green" />; // Base
            case 2: return <AlertTriangle size={20} className="icon-orange" />; // Alert
            case 3: return <Cloud size={20} className="icon-blue" />; // Environmental crisis
            case 4: return <Clock size={20} className="icon-purple" />; // Infrastructure degradation
            case 5: case 99: return <AlertTriangle size={20} style={{ color: 'red' }} />; // Exceptional event
            default: return <Play size={20} className="icon-gray" />;
        }
    };

    if (error) return <div className="error-msg">{error}</div>;

    return (
        <div className={`scenario-panel ${isSystemBusy ? 'panel-blocked' : ''}`}>
            <div className="scenario-header">
                <div className="flex items-center gap-2" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <h2>Stochastic Scenario Control</h2>

                    {isSystemBusy ? (
                        <span className="status-badge processing">
                            <Loader2 size={14} className="spin-icon" />
                            RUNNING MAPE-K FEEDBACK LOOP...
                        </span>
                    ) : (
                        <span className="status-badge ready pulse-green">
                            <span className="dot-indicator"></span>
                            SYSTEM READY
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
                            ${activeScenarioId === scenario.id ? 'active' : ''}
                            ${isSystemBusy ? 'disabled-card' : ''}
                        `}
                    >
                        {isSystemBusy && (
                            <div className="card-overlay">
                                <Lock size={32} className="lock-icon" />
                            </div>
                        )}

                        {activeScenarioId === scenario.id && !isSystemBusy && (
                            <div className="active-badge glow-effect">
                                <CheckCircle size={14} /> ACTIVE
                            </div>
                        )}

                        <div className="card-content">
                            <div className="card-header">
                                <div className={`icon-wrapper icon-wrapper-${scenario.id}`}>
                                    {getIcon(scenario.id)}
                                </div>
                                <h3>{scenario.name}</h3>
                            </div>

                            <p className="card-desc">{scenario.description}</p>

                            <div className="card-footer">
                                <div className="metrics-row">
                                    <span className="metric-pill">
                                        <span className="metric-label">AQI</span>
                                        <span className="metric-val">{scenario.air_quality_index_range.join('-')}</span>
                                    </span>
                                    <span className="metric-pill">
                                        <span className="metric-label">Complexity</span>
                                        <span className="metric-val">{scenario.problem_complexity_range.join('-')}</span>
                                    </span>
                                </div>
                                <span className={`sla-badge sla-${scenario.sla_priority.toLowerCase()}`}>
                                    SLA: {scenario.sla_priority}
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
