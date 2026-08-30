import React, { useState } from 'react';
import ScenarioSelector from './components/ScenarioSelector';
import PhaseStepper from './components/PhaseStepper';
import ServicesPanel from './components/panels/ServicesPanel';
import QuantumPanel from './components/panels/QuantumPanel';
import AdaptationTracePanel from './components/panels/AdaptationTracePanel';
import MonitoredContextPanel from './components/panels/MonitoredContextPanel';
import LogsPanel from './components/panels/LogsPanel';
import StateGraphPanel from './components/panels/StateGraphPanel';
import { useSystemStatus } from './hooks/useSystemStatus';
import { Network, RefreshCw, Brain, X } from 'lucide-react';
import './App.css';

function App() {
  const {
    systemState,
    logs,
    lastUpdate,
    isSystemReady,
    isProcessing,
    refreshNow,
    downloadImage,
    apiBaseUrl
  } = useSystemStatus();

  const [modalImageUrl, setModalImageUrl] = useState(null);

  const handleScenarioChange = () => {
    refreshNow();
  };

  return (
    <div className="App">

      {/* Image lightbox */}
      {modalImageUrl && (
        <div className="modal-overlay" onClick={() => setModalImageUrl(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setModalImageUrl(null)}>
              <X size={24} />
            </button>
            <img src={`${apiBaseUrl}${modalImageUrl}`} alt="Expanded system evidence" />
          </div>
        </div>
      )}

      <header className="App-header">
        <div className="header-content">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Network className="text-blue-600" />
            <h1 style={{ fontSize: '1.2rem', margin: 0 }}>FMweb-K-Quantum Self-Adaptive HQC Architecture</h1>
          </div>
          <div className="header-meta">
            <span>Last updated: {lastUpdate.toLocaleTimeString()}</span>
            <button onClick={refreshNow} className="refresh-btn" title="Refresh system status">
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
          <PhaseStepper trace={systemState?.mapek_trace} />

          {systemState?.context?.reasoning ? (
            <div className="brain-box">
              <div className="brain-title">
                <Brain size={16} /> ADAPTATION DECISION
              </div>
              <div className="brain-content">"{systemState.context.reasoning}"</div>
            </div>
          ) : (
            <div className="text-center text-gray-400 text-sm mt-2">
              Awaiting a monitored-context event to initiate the MAPE-K feedback loop...
            </div>
          )}
        </section>

        <div className="dashboard-grid">

          <div className="left-col">
            <StateGraphPanel
              systemState={systemState}
              isProcessing={isProcessing}
              isSystemReady={isSystemReady}
              onOpenModal={setModalImageUrl}
              apiBaseUrl={apiBaseUrl}
            />

            <ServicesPanel systemState={systemState} />

            <QuantumPanel
              systemState={systemState}
              isProcessing={isProcessing}
              isSystemReady={isSystemReady}
              onOpenModal={setModalImageUrl}
              onDownload={downloadImage}
              apiBaseUrl={apiBaseUrl}
            />
          </div>

          <div className="right-col">
            <AdaptationTracePanel
              mapekTrace={systemState?.mapek_trace}
              isProcessing={isProcessing}
            />

            <MonitoredContextPanel
              context={systemState?.context}
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
