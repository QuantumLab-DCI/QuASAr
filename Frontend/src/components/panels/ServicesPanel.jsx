// src/components/panels/ServicesPanel.jsx
import React, { useState } from 'react';
import { LayoutGrid } from 'lucide-react';
import MicroFrontendCard from '../MicroFrontendCard';
import ServiceInspector from '../ServiceInspector';

const ServicesPanel = ({ estado }) => {
    const [inspectService, setInspectService] = useState(null);

    const isDeportesActive = estado?.configuracion?.deportes === true;
    const isHqcActive = estado?.configuracion?.hqc === true;

    const getDeportesReason = () => {
        if (estado?.contexto?.calidad_aire_ica > 100) return "Bloqueo por Crisis Ambiental (ICA > 100)";
        return "Desactivado por Perfil de Usuario (No requerido)";
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
                <h2 className="panel-title"><LayoutGrid className="icon" /> Micro-Frontends Distribuidos</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>

                    <MicroFrontendCard
                        title="Turismo (:8081)"
                        port={8081}
                        active={true}
                        color="#e67e22"
                        onInspect={() => setInspectService({ name: 'Turismo', status: 'active' })}
                    />

                    <MicroFrontendCard
                        title="Deportes (:8082)"
                        port={8082}
                        active={isDeportesActive}
                        reason={getDeportesReason()}
                        color="#2ecc71"
                        onInspect={() => setInspectService({ name: 'Deportes' })}
                    />

                    <MicroFrontendCard
                        title="Gestor Aire (:8083)"
                        port={8083}
                        active={true}
                        color="#3498db"
                        onInspect={() => setInspectService({ name: 'Gestor Calidad Aire' })}
                    />

                    <MicroFrontendCard
                        title="HQC Quantum (:8084)"
                        port={8084}
                        active={isHqcActive}
                        reason="Baja Complejidad (CP < 100)"
                        color="#9b59b6"
                        onInspect={() => setInspectService({ name: 'HQC Module' })}
                    />
                </div>
            </div>
        </>
    );
};

export default ServicesPanel;
