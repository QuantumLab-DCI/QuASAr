// src/components/panels/ServicesPanel.jsx
import React, { useState } from 'react';
import { LayoutGrid } from 'lucide-react';
import MicroFrontendCard from '../MicroFrontendCard';
import ServiceInspector from '../ServiceInspector';

const ServicesPanel = ({ systemState }) => {
    const [inspectService, setInspectService] = useState(null);

    const isSportsActive = systemState?.configuration?.sports === true;
    const isHybridQuantumActive = systemState?.configuration?.hybrid_quantum_computing === true;

    const getSportsReason = () => {
        if (systemState?.context?.air_quality_index > 100) return "Disabled because hazardous air quality exceeds AQI 100";
        return "Disabled because the monitored user profile does not require sports services";
    };

    return (
        <>
            {inspectService && (
                <ServiceInspector
                    service={inspectService}
                    onClose={() => setInspectService(null)}
                />
            )}

            <div className="panel services-panel">
                <h2 className="panel-title"><LayoutGrid className="icon" /> Distributed Micro-Frontends</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>

                    <MicroFrontendCard
                        title="Tourism (:8081)"
                        port={8081}
                        active={true}
                        onInspect={() => setInspectService({ name: 'tourism', status: 'active' })}
                    />

                    <MicroFrontendCard
                        title="Sports (:8082)"
                        port={8082}
                        active={isSportsActive}
                        reason={getSportsReason()}
                        onInspect={() => setInspectService({ name: 'sports' })}
                    />

                    <MicroFrontendCard
                        title="Air Quality Manager (:8083)"
                        port={8083}
                        active={true}
                        onInspect={() => setInspectService({ name: 'air_quality_manager' })}
                    />

                    <MicroFrontendCard
                        title="Hybrid Quantum-Classical Computing (:8084)"
                        port={8084}
                        active={isHybridQuantumActive}
                        reason="Disabled because the problem complexity does not warrant hybrid quantum-classical execution"
                        onInspect={() => setInspectService({ name: 'hybrid_quantum_computing' })}
                    />
                </div>
            </div>
        </>
    );
};

export default ServicesPanel;
