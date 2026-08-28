// src/components/PhaseStepper.jsx
import React from 'react';
import { Eye, Brain, GitMerge, Play } from 'lucide-react';

const getCurrentPhase = (trace) => {
    if (!trace || trace.length === 0) return 0;
    const lastPhase = trace[trace.length - 1].fase;
    if (lastPhase.includes("MONITOR")) return 1;
    if (lastPhase.includes("ANÁLISIS")) return 2;
    if (lastPhase.includes("PLAN")) return 3;
    if (lastPhase.includes("EJECUCIÓN") || lastPhase.includes("FIN")) return 4;
    return 0;
};

const PhaseStepper = ({ trace }) => {
    const currentPhaseStep = getCurrentPhase(trace);

    return (
        <div className="phase-stepper">
            <div className={`phase-node ${currentPhaseStep >= 1 ? 'active' : ''}`}>
                <Eye size={18} /> <span className="phase-label">MONITOREO</span>
            </div>
            <div className={`phase-node ${currentPhaseStep >= 2 ? 'active' : ''}`}>
                <Brain size={18} /> <span className="phase-label">ANÁLISIS (IA)</span>
            </div>
            <div className={`phase-node ${currentPhaseStep >= 3 ? 'active' : ''}`}>
                <GitMerge size={18} /> <span className="phase-label">PLANIFICACIÓN</span>
            </div>
            <div className={`phase-node ${currentPhaseStep >= 4 ? 'active' : ''}`}>
                <Play size={18} /> <span className="phase-label">EJECUCIÓN</span>
            </div>
        </div>
    );
};

export default PhaseStepper;
