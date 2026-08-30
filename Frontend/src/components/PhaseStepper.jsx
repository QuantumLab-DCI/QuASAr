// src/components/PhaseStepper.jsx
import React from 'react';
import { Eye, Brain, GitMerge, Play } from 'lucide-react';

const getCurrentPhase = (trace) => {
    if (!trace || trace.length === 0) return 0;
    const lastPhase = trace[trace.length - 1].phase;
    if (lastPhase === "MONITOR") return 1;
    if (lastPhase === "ANALYZE") return 2;
    if (lastPhase === "PLAN") return 3;
    if (lastPhase === "EXECUTE") return 4;
    return 0;
};

const PhaseStepper = ({ trace }) => {
    const currentPhaseStep = getCurrentPhase(trace);

    return (
        <div className="phase-stepper">
            <div className={`phase-node ${currentPhaseStep >= 1 ? 'active' : ''}`}>
                <Eye size={18} /> <span className="phase-label">Monitor</span>
            </div>
            <div className={`phase-node ${currentPhaseStep >= 2 ? 'active' : ''}`}>
                <Brain size={18} /> <span className="phase-label">Analyze</span>
            </div>
            <div className={`phase-node ${currentPhaseStep >= 3 ? 'active' : ''}`}>
                <GitMerge size={18} /> <span className="phase-label">Plan</span>
            </div>
            <div className={`phase-node ${currentPhaseStep >= 4 ? 'active' : ''}`}>
                <Play size={18} /> <span className="phase-label">Execute</span>
            </div>
        </div>
    );
};

export default PhaseStepper;
