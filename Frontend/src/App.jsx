import React, { useState } from 'react';
import ScenarioSelector from './components/ScenarioSelector';
import PhaseStepper from './components/PhaseStepper';
import ServicesPanel from './components/panels/ServicesPanel';
import QuantumPanel from './components/panels/QuantumPanel';
import MapekHistoryPanel from './components/panels/MapekHistoryPanel';
import MetricsPanel from './components/panels/MetricsPanel';
import LogsPanel from './components/panels/LogsPanel';
import StateGraphPanel from './components/panels/StateGraphPanel';
import { useSystemStatus } from './hooks/useSystemStatus';
import { Network, RefreshCw, Brain, X } from 'lucide-react';
import './App.css';

function App() {
  const {
    estado,
    logs,
    lastUpdate,
    isSystemReady,
    isProcessing,
    refreshNow,
    downloadImage,
    API_URL
  } = useSystemStatus();

  const [modalImage, setModalImage] = useState(null);

  // Handle scenario changes
  const handleScenarioChange = () => {
    refreshNow();
  };

  return (
    <div className="App">

      {/* IMAGE MODAL RENDERING (Lightbox) */}
      {modalImage && (
        <div className="modal-overlay" onClick={() => setModalImage(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setModalImage(null)}>
              <X size={24} />
            </button>
            <img src={`${API_URL}${modalImage}`} alt="Evidencia Ampliada" />
          </div>
        </div>
      )}

      <header className="App-header">
        <div className="header-content">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Network className="text-blue-600" />
            <h1 style={{ fontSize: '1.2rem', margin: 0 }}>Arquitectura HQC Auto-adaptativa</h1>
          </div>
          <div className="header-meta">
            <span>Última act: {lastUpdate.toLocaleTimeString()}</span>
            <button onClick={refreshNow} className="refresh-btn">
              <RefreshCw size={18} />
            </button>
          </div>
        </div>
      </header>

      <div className="main-container">

        <section className="control-section">
          <ScenarioSelector
            onScenarioChange={handleScenarioChange}
            isSystemBusy={isProcessing}
          />
        </section>

        <section className="mapek-visualizer">
          <PhaseStepper trace={estado?.mapek_trace} />

          {estado?.contexto?.razonamiento ? (
            <div className="brain-box">
              <div className="brain-title">
                <Brain size={16} /> DECISIÓN DEL AGENTE
              </div>
              <div className="brain-content">"{estado.contexto.razonamiento}"</div>
            </div>
          ) : (
            <div className="text-center text-gray-400 text-sm mt-2">
              Esperando evento del entorno para iniciar ciclo de adaptación...
            </div>
          )}
        </section>

        <div className="dashboard-grid">

          <div className="left-col">
            <StateGraphPanel
              estado={estado}
              isProcessing={isProcessing}
              isSystemReady={isSystemReady}
              onOpenModal={setModalImage}
              API_URL={API_URL}
            />

            <ServicesPanel estado={estado} />

            <QuantumPanel
              estado={estado}
              isProcessing={isProcessing}
              isSystemReady={isSystemReady}
              onOpenModal={setModalImage}
              onDownload={downloadImage}
              API_URL={API_URL}
            />
          </div>

          <div className="right-col">
            <MapekHistoryPanel
              mapekTrace={estado?.mapek_trace}
              isProcessing={isProcessing}
            />

            <MetricsPanel
              contexto={estado?.contexto}
              isProcessing={isProcessing}
              isSystemReady={isSystemReady}
            />

            <LogsPanel logs={logs} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
