import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ScenarioSelector from './components/ScenarioSelector';
import {
  RefreshCw, Zap, Network, Terminal, Info, Brain, Download, Maximize2,
  ExternalLink, X, Activity, GitMerge, Box, CheckCircle, Loader2,
  Eye, Play, Server, ShieldAlert, CheckCircle2, Search // <--- Agregamos Search
} from 'lucide-react';
import './App.css';

const API_URL = 'http://127.0.0.1:8000';
const REFRESH_INTERVAL = 3000;

// --- FUNCIONES AUXILIARES ---

const getCurrentPhase = (trace) => {
  if (!trace || trace.length === 0) return 0;
  const lastPhase = trace[trace.length - 1].fase;
  if (lastPhase.includes("MONITOR")) return 1;
  if (lastPhase.includes("ANÁLISIS")) return 2;
  if (lastPhase.includes("PLAN")) return 3;
  if (lastPhase.includes("EJECUCIÓN") || lastPhase.includes("FIN")) return 4;
  return 0;
};

// Generador de Logs para la "Caja Blanca" (Simulación de Terminal)
const generateServiceLogs = (serviceName, estadoContexto) => {
  const logs = [];
  const ts = () => new Date().toLocaleTimeString('es-CL', { hour12: false }) + "." + Math.floor(Math.random() * 999);

  // Logs de arranque comunes
  logs.push({ ts: ts(), level: 'INFO', msg: `[System] Starting ${serviceName} v2.4.0...` });
  logs.push({ ts: ts(), level: 'INFO', msg: `[Network] Bound to port ${serviceName === 'HQC' ? 9090 : 8080}` });

  // Lógica específica para Deportes (Crisis Ambiental)
  if (serviceName === 'Deportes') {
    if (estadoContexto?.calidad_aire_ica > 100) {
      logs.push({ ts: ts(), level: 'INFO', msg: `[Sensor] Reading ICA_SENSOR_01...` });
      logs.push({ ts: ts(), level: 'WARN', msg: `[Sensor] Value: ${estadoContexto.calidad_aire_ica} (Threshold: 100)` });
      logs.push({ ts: ts(), level: 'ERROR', msg: `[Policy] VIOLATION DETECTED: AIR_QUALITY_CRITICAL` });
      logs.push({ ts: ts(), level: 'INFO', msg: `[MAPE-K] Received SIGTERM signal.` });
      logs.push({ ts: ts(), level: 'WARN', msg: `[System] Service stopped. Graceful shutdown initiated.` });
    } else {
      logs.push({ ts: ts(), level: 'INFO', msg: `[Sensor] Reading ICA_SENSOR_01... Value: ${estadoContexto?.calidad_aire_ica || 40}` });
      logs.push({ ts: ts(), level: 'INFO', msg: `[Health] Status OK. Serving requests.` });
    }
  }

  // Lógica específica para HQC (Alta Demanda)
  if (serviceName === 'HQC Module') {
    if (estadoContexto?.complejidad_problema_cp > 80) {
      logs.push({ ts: ts(), level: 'INFO', msg: `[JobManager] Received high-complexity task (CP=${estadoContexto.complejidad_problema_cp})` });
      logs.push({ ts: ts(), level: 'DEBUG', msg: `[Factory] Instantiating QuantumBackend...` });
      logs.push({ ts: ts(), level: 'INFO', msg: `[Qiskit] Transpiling circuit (optimization_level=3)...` });
      logs.push({ ts: ts(), level: 'INFO', msg: `[Result] Job completed. Evidence generated.` });
    } else {
      logs.push({ ts: ts(), level: 'INFO', msg: `[JobManager] Polling for tasks...` });
      logs.push({ ts: ts(), level: 'DEBUG', msg: `[JobManager] Queue empty. Entering sleep mode.` });
    }
  }

  if (serviceName === 'Turismo') {
    logs.push({ ts: ts(), level: 'INFO', msg: `[API] GET /routes/optimize 200 OK` });
    logs.push({ ts: ts(), level: 'INFO', msg: `[DB] Querying POI database...` });
  }

  return logs;
};

// --- COMPONENTES UI ---

const LoadingBlock = ({ loading, children, message = "Procesando..." }) => {
  return (
    <div className="loading-wrapper" style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative', minHeight: 0, overflow: 'hidden' }}>
      {loading && (
        <div className="loading-overlay" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', zIndex: 10, backdropFilter: 'blur(2px)', backgroundColor: 'rgba(255,255,255,0.1)', color: '#61dafb', fontWeight: 'bold', textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>
          <Loader2 size={40} className="spinner-icon" style={{ animation: 'spin 1s linear infinite', marginBottom: '10px' }} />
          <span>{message}</span>
        </div>
      )}
      <div className={loading ? "loading-blur" : ""} style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, overflow: 'hidden', ...(loading ? { filter: 'blur(4px)', opacity: 0.7, pointerEvents: 'none' } : {}) }}>
        {children}
      </div>
    </div>
  );
};

// --- COMPONENTE NUEVO: Inspector de Servicios (Terminal Flotante) ---
const ServiceInspector = ({ service, onClose, contexto }) => {
  const logs = generateServiceLogs(service.name, contexto);
  const scrollRef = useRef(null);

  // Auto-scroll al final de los logs
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  // Datos "fake" pero técnicos para la demo
  const cpu = service.status === 'active' ? Math.floor(Math.random() * 30 + 10) : 0;
  const mem = service.status === 'active' ? Math.floor(Math.random() * 100 + 50) : 0;
  const threads = service.status === 'active' ? Math.floor(Math.random() * 5 + 2) : 0;

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
            <div className="metric-card"><small>CPU Usage</small><strong>{cpu}%</strong></div>
            <div className="metric-card"><small>Memory</small><strong>{mem} MB</strong></div>
            <div className="metric-card"><small>Threads</small><strong>{threads}</strong></div>
          </div>
          <div className="inspector-console" ref={scrollRef}>
            {logs.map((log, i) => (
              <div key={i} className="console-line">
                <span className="log-ts">{log.ts}</span>
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

// --- APP PRINCIPAL ---

function App() {
  const [estado, setEstado] = useState(null);
  const [logs, setLogs] = useState("Sistema listo. Seleccione un escenario para iniciar.");
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [isSystemReady, setIsSystemReady] = useState(false);
  const [modalImage, setModalImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  // Estado para controlar qué servicio se está inspeccionando (Null = cerrado)
  const [inspectService, setInspectService] = useState(null);

  const fetchData = async () => {
    try {
      const timestamp = new Date().getTime();
      const resEstado = await axios.get(`${API_URL}/api/estado?t=${timestamp}`);
      let data = resEstado.data;

      if (data.imagen_estado_url) data.imagen_estado_url += `?t=${timestamp}`;
      if (data.evidencia_cuantica_url) data.evidencia_cuantica_url += `?t=${timestamp}`;

      setIsProcessing(data.en_ejecucion);
      setEstado(data);
      setIsSystemReady(true);

      const resLogs = await axios.get(`${API_URL}/api/logs`);
      setLogs(resLogs.data.log_content);
      setLastUpdate(new Date());

    } catch (err) {
      if (err.response && err.response.status === 503) setIsSystemReady(false);
      else console.error("Error de conexión:", err);
    }
  };

  useEffect(() => {
    fetchData();
    const intervalId = setInterval(fetchData, REFRESH_INTERVAL);
    return () => clearInterval(intervalId);
  }, []);

  const handleScenarioChange = () => {
    setIsProcessing(true);
    setTimeout(fetchData, 1000);
  };

  const handleDownload = async (imageUrl) => { /* Lógica de descarga */ };

  const getPhaseIcon = (fase) => {
    if (fase.includes("MONITOR")) return <Activity size={16} />;
    if (fase.includes("ANÁLISIS")) return <Brain size={16} />;
    if (fase.includes("PLAN")) return <GitMerge size={16} />;
    if (fase.includes("EJECUCIÓN")) return <Box size={16} />;
    if (fase.includes("FIN")) return <CheckCircle size={16} />;
    return <Info size={16} />;
  };

  const currentPhaseStep = getCurrentPhase(estado?.mapek_trace);

  return (
    <div className="App">

      {/* 1. RENDERIZADO DEL MODAL INSPECTOR (Si hay un servicio seleccionado) */}
      {inspectService && (
        <ServiceInspector
          service={inspectService}
          contexto={estado?.contexto}
          onClose={() => setInspectService(null)}
        />
      )}

      {/* 2. RENDERIZADO DEL MODAL DE IMAGEN (Lightbox) */}
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
          <h1>⚛️ Arquitectura Híbrida Auto-adaptativa (HQC)</h1>
          <div className="header-meta">
            <span>Última act: {lastUpdate.toLocaleTimeString()}</span>
            <button onClick={fetchData} className="refresh-btn">
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

          {estado?.contexto?.razonamiento ? (
            <div className="brain-box">
              <div className="brain-title">
                <Brain size={16} /> RAZONAMIENTO DEL ARQUITECTO AUTÓNOMO
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
            <div className="panel graph-panel">
              <h2 className="panel-title"><Network className="icon" /> Estado Actual (LPSD)</h2>
              <LoadingBlock loading={isProcessing} message="Reconfigurando Arquitectura...">
                <div className="image-container state-graph">
                  {isSystemReady && estado?.imagen_estado_url ? (
                    <img
                      src={`${API_URL}${estado.imagen_estado_url}`}
                      alt="Grafo de Estado"
                      className="clickable-image"
                      onClick={() => !isProcessing && setModalImage(estado.imagen_estado_url)}
                    />
                  ) : (
                    <div className="placeholder-state">
                      <Info size={40} className="text-gray-300 mb-2" />
                      <p className="text-gray-400">Sin arquitectura activa.</p>
                    </div>
                  )}
                </div>
              </LoadingBlock>
            </div>

            {/* --- PANEL SERVICIOS CON BOTONES INTERACTIVOS --- */}
            <div className="panel services-panel">
              <h2 className="panel-title"><Server className="icon" /> Estado de Microservicios</h2>
              <div className="services-table-container">
                <table className="services-table" style={{ width: '100%', fontSize: '0.85rem', textAlign: 'left', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #e5e7eb', color: '#6b7280' }}>
                      <th style={{ padding: '8px' }}>Servicio</th>
                      <th style={{ padding: '8px' }}>Estado</th>
                      <th style={{ padding: '8px', textAlign: 'right' }}>Acción</th> {/* Cambiado título a Acción */}
                    </tr>
                  </thead>
                  <tbody>
                    {/* Servicio Turismo */}
                    <tr style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '8px', fontWeight: '500' }}>Turismo</td>
                      <td style={{ padding: '8px' }}>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#10b981', background: '#ecfdf5', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem' }}>
                          <CheckCircle2 size={12} /> Activo
                        </span>
                      </td>
                      <td style={{ padding: '8px', textAlign: 'right' }}>
                        <button className="btn-inspect" onClick={() => setInspectService({ name: 'Turismo', status: 'active' })}>
                          <Search size={14} /> Monitor
                        </button>
                      </td>
                    </tr>

                    {/* Servicio Deportes */}
                    <tr style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '8px', fontWeight: '500' }}>Deportes</td>
                      <td style={{ padding: '8px' }}>
                        {estado?.contexto?.calidad_aire_ica > 100 ? (
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#ef4444', background: '#fef2f2', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem' }}>
                            <ShieldAlert size={12} /> Detenido
                          </span>
                        ) : (
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#10b981', background: '#ecfdf5', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem' }}>
                            <CheckCircle2 size={12} /> Activo
                          </span>
                        )}
                      </td>
                      <td style={{ padding: '8px', textAlign: 'right' }}>
                        {/* Este botón abre el inspector y muestra la "causa raíz" */}
                        <button className="btn-inspect" onClick={() => setInspectService({ name: 'Deportes', status: estado?.contexto?.calidad_aire_ica > 100 ? 'stopped' : 'active' })}>
                          <Search size={14} /> Monitor
                        </button>
                      </td>
                    </tr>

                    {/* Servicio HQC */}
                    <tr style={{ borderBottom: '1px solid #f3f4f6' }}>
                      <td style={{ padding: '8px', fontWeight: '500' }}>HQC Module</td>
                      <td style={{ padding: '8px' }}>
                        {estado?.evidencia_cuantica_url ? (
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#8b5cf6', background: '#f5f3ff', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem' }}>
                            <Zap size={12} /> Procesando
                          </span>
                        ) : (
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#9ca3af', background: '#f3f4f6', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem' }}>
                            Standby
                          </span>
                        )}
                      </td>
                      <td style={{ padding: '8px', textAlign: 'right' }}>
                        <button className="btn-inspect" onClick={() => setInspectService({ name: 'HQC Module', status: 'active' })}>
                          <Search size={14} /> Monitor
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div className="panel quantum-panel">
              <h2 className="panel-title">
                <Zap className="icon text-yellow" /> Evidencia de Ejecución Cuántica
              </h2>
              <LoadingBlock loading={isProcessing} message="Compilando Circuito...">
                <div className="quantum-content">
                  {isSystemReady && estado?.evidencia_cuantica_url ? (
                    <div className="evidence-wrapper">
                      <div className="image-container quantum-evidence">
                        <img
                          src={`${API_URL}${estado.evidencia_cuantica_url}`}
                          alt="Circuito Cuántico"
                          onClick={() => !isProcessing && setModalImage(estado.evidencia_cuantica_url)}
                        />
                      </div>
                      <div className="evidence-toolbar">
                        <button className="tool-btn" onClick={() => handleDownload(estado.evidencia_cuantica_url)} disabled={isProcessing}>
                          <Download size={16} /> Descargar
                        </button>
                        <button className="tool-btn" onClick={() => setModalImage(estado.evidencia_cuantica_url)} disabled={isProcessing}>
                          <Maximize2 size={16} /> Ampliar
                        </button>
                      </div>
                      <p className="success-msg">✅ Ejecución exitosa en Backend HQC</p>
                    </div>
                  ) : (
                    <div className="placeholder-quantum">
                      <span>💤 Módulo Cuántico Inactivo</span>
                    </div>
                  )}
                </div>
              </LoadingBlock>
            </div>
          </div>

          <div className="right-col">
            <div className="panel mapek-panel">
              <h2 className="panel-title">🔄 Historial de Adaptación</h2>
              <LoadingBlock loading={isProcessing} message="Registrando eventos...">
                <div className="mapek-timeline">
                  {estado?.mapek_trace?.map((paso, index) => (
                    <div key={index} className="mapek-step">
                      <div className="step-header">
                        <div className="step-meta">
                          {getPhaseIcon(paso.fase)}
                          <span className="step-time">{paso.timestamp}</span>
                        </div>
                        <span className={`step-badge phase-${paso.fase.split(' ')[0].toLowerCase()}`}>
                          {paso.fase}
                        </span>
                      </div>
                      <p className="step-msg">{paso.mensaje}</p>
                    </div>
                  ))}
                </div>
              </LoadingBlock>
            </div>

            <div className="panel context-panel">
              <h2 className="panel-title">Sensores del Entorno</h2>
              <LoadingBlock loading={isProcessing} message="Leyendo sensores...">
                {isSystemReady && estado?.contexto ? (
                  <div>
                    <div className="metrics-list">
                      <div className="metric-item">
                        <span className="metric-label">Calidad Aire (ICA)</span>
                        <span className="metric-value color-ica">{estado.contexto.calidad_aire_ica}</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Complejidad (CP)</span>
                        <span className="metric-value color-cp">{estado.contexto.complejidad_problema_cp}</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">SLA Prioridad</span>
                        <span className="metric-value color-sla">{estado.contexto.prioridad_sla}</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 text-center text-gray-400 text-sm">Sin datos.</div>
                )}
              </LoadingBlock>
            </div>

            <div className="panel log-panel">
              <h2 className="panel-title"><Terminal className="icon" /> Logs del Sistema</h2>
              <pre className="log-box">{logs}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;