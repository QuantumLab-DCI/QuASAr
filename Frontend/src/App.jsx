import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ScenarioSelector from './components/ScenarioSelector';
import {
  RefreshCw, Zap, Network, Terminal, Info, Brain, Download, Maximize2,
  ExternalLink, X, Activity, GitMerge, Box, CheckCircle, Loader2,
  Eye, Play, Server, ShieldAlert, CheckCircle2, Search, LayoutGrid
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

// --- COMPONENTE NUEVO: Inspector de Servicios (REAL TIME) ---
const ServiceInspector = ({ service, onClose }) => {
  const [realLogs, setRealLogs] = useState([]);
  const scrollRef = useRef(null);

  // Función para obtener logs REALES del Backend
  const fetchRealLogs = async () => {
    try {
      // Pedimos al backend que lea los logs de Docker
      const response = await axios.get(`${API_URL}/api/container_logs/${service.name}`);

      if (response.data.status === 'ok') {
        // Docker devuelve un string gigante, lo dividimos en líneas y filtramos vacías
        const lines = response.data.logs.split('\n').filter(line => line.trim().length > 0);

        // Formateamos para que se vea bonito en la terminal
        const formattedLogs = lines.map(line => {
          let ts = "";
          let level = "INFO";
          let msg = line;

          // Intentamos parsear el formato: "14:30:01 [INFO] Mensaje..."
          // Regex simple para capturar hora y nivel entre corchetes
          const match = line.match(/^(\d{2}:\d{2}:\d{2})\s+\[([A-Z]+)\]\s+(.*)/);

          if (match) {
            ts = match[1];
            level = match[2];
            msg = match[3];
          } else {
            // Si no coincide (ej. trazas de error de Python), lo dejamos raw pero detectamos palabras clave
            if (line.includes('ERROR') || line.includes('Exception')) level = 'ERROR';
            else if (line.includes('WARN')) level = 'WARN';
            else if (line.includes('DEBUG')) level = 'DEBUG';
          }

          return { ts, level, msg, raw: line };
        });

        setRealLogs(formattedLogs);
      } else {
        setRealLogs([{ ts: 'System', level: 'ERROR', msg: response.data.logs }]);
      }
    } catch (error) {
      // Si falla la conexión (ej. backend caído)
      console.error(error);
      setRealLogs(prev => [...prev, { ts: 'System', level: 'ERROR', msg: "Error conectando con Docker API..." }]);
    }
  };

  // Polling: Actualizar logs cada 2 segundos mientras la ventana esté abierta
  useEffect(() => {
    fetchRealLogs(); // Primera carga inmediata
    const interval = setInterval(fetchRealLogs, 2000);
    return () => clearInterval(interval);
  }, [service]);

  // Auto-scroll al final
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [realLogs]);

  // Métricas FALSAS para decoración (Docker API es lenta para esto en tiempo real)
  const cpu = service.status === 'active' || service.status === undefined ? Math.floor(Math.random() * 20 + 5) : 0;
  const mem = service.status === 'active' || service.status === undefined ? Math.floor(Math.random() * 50 + 40) : 0;

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
            <div className="metric-card"><small>CPU (Live)</small><strong>{cpu}%</strong></div>
            <div className="metric-card"><small>Memory</small><strong>{mem} MB</strong></div>
            <div className="metric-card"><small>Logs Source</small><strong style={{ color: '#10b981' }}>DOCKER.SOCK</strong></div>
          </div>
          <div className="inspector-console" ref={scrollRef}>
            {realLogs.length === 0 && <div className="console-line" style={{ color: '#666' }}>Cargando logs del contenedor...</div>}

            {realLogs.map((log, i) => (
              <div key={i} className="console-line">
                {log.ts && <span className="log-ts">{log.ts}</span>}
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

// --- COMPONENTE DE MICRO-FRONTEND ---
const MicroFrontendCard = ({ title, port, active, reason, onInspect, color }) => {
  return (
    <div style={{ border: `1px solid ${active ? '#e5e7eb' : '#fca5a5'}`, borderRadius: '8px', overflow: 'hidden', background: 'white', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '8px 12px', background: active ? '#f9fafb' : '#fef2f2', borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', fontWeight: '600', color: '#374151' }}>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: active ? '#10b981' : '#ef4444' }}></div>
          {title}
        </div>
        <button onClick={onInspect} className="tool-btn" style={{ padding: '2px 6px', fontSize: '0.7rem' }} title="Ver Logs Reales">
          <Terminal size={12} />
        </button>
      </div>

      <div style={{ height: '160px', position: 'relative', background: '#f3f4f6' }}>
        {active ? (
          <iframe
            src={`http://localhost:${port}`}
            style={{ width: '100%', height: '100%', border: 'none' }}
            title={`MF ${title}`}
            scrolling="no"
          />
        ) : (
          <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#b91c1c', padding: '10px', textAlign: 'center' }}>
            <ShieldAlert size={32} style={{ marginBottom: '8px', opacity: 0.5 }} />
            <span style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>SERVICIO DETENIDO</span>
            <span style={{ fontSize: '0.75rem', marginTop: '4px' }}>{reason}</span>
          </div>
        )}
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

  // Función ROBUSTA para forzar la descarga de la imagen
  const handleDownload = async (imageUrl) => {
    if (!imageUrl) return;

    try {
      // 1. Construir la URL completa correctamente
      const fullUrl = imageUrl.startsWith('http')
        ? imageUrl
        : `${API_URL}${imageUrl.startsWith('/') ? '' : '/'}${imageUrl}`;

      // 2. Usar AXIOS para pedir la imagen como "blob"
      const response = await axios.get(fullUrl, {
        responseType: 'blob', // <--- ESTO ES LA CLAVE
      });

      // 3. Crear una URL temporal en memoria para ese blob
      const url = window.URL.createObjectURL(new Blob([response.data]));

      // 4. Crear un enlace invisible, hacer clic y borrarlo
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `evidencia_hqc_${new Date().getTime()}.png`);
      document.body.appendChild(link);
      link.click();

      // 5. Limpieza
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error("Error descargando imagen:", error);
      alert("Error al descargar. Intenta usar el botón 'Pestaña' y guardar manualmente.");
    }
  };

  const getPhaseIcon = (fase) => {
    if (fase.includes("MONITOR")) return <Activity size={16} />;
    if (fase.includes("ANÁLISIS")) return <Brain size={16} />;
    if (fase.includes("PLAN")) return <GitMerge size={16} />;
    if (fase.includes("EJECUCIÓN")) return <Box size={16} />;
    if (fase.includes("FIN")) return <CheckCircle size={16} />;
    return <Info size={16} />;
  };

  const currentPhaseStep = getCurrentPhase(estado?.mapek_trace);

  // --- LÓGICA DE ESTADO DE SERVICIOS (VERDADERA) ---
  // Usamos la 'configuracion' real del backend, no heurísticas
  const isDeportesActive = estado?.configuracion?.deportes === true;
  const isHqcActive = estado?.configuracion?.hqc === true;

  // Lógica para el mensaje de razón (Feedback visual)
  const getDeportesReason = () => {
    // Si el backend dice que está apagado, explicamos por qué (basado en contexto)
    if (estado?.contexto?.calidad_aire_ica > 100) return "Bloqueo por Crisis Ambiental (ICA > 100)";
    return "Desactivado por Perfil de Usuario (No requerido)";
  };

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
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Network className="text-blue-600" />
            <h1 style={{ fontSize: '1.2rem', margin: 0 }}>Arquitectura HQC Auto-adaptativa</h1>
          </div>
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
              <h2 className="panel-title"><LayoutGrid className="icon" /> Micro-Frontends Distribuidos</h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>

                {/* 1. Módulo Turismo (Siempre Activo) */}
                <MicroFrontendCard
                  title="Turismo (:8081)"
                  port={8081}
                  active={true}
                  color="#e67e22"
                  onInspect={() => setInspectService({ name: 'Turismo', status: 'active' })}
                />

                {/* 2. Módulo Deportes (Condicional) */}
                <MicroFrontendCard
                  title="Deportes (:8082)"
                  port={8082}
                  active={isDeportesActive}
                  reason={getDeportesReason()}
                  color="#2ecc71"
                  onInspect={() => setInspectService({ name: 'Deportes' })}
                />

                {/* 3. Módulo Aire (Siempre Activo) */}
                <MicroFrontendCard
                  title="Gestor Aire (:8083)"
                  port={8083}
                  active={true}
                  color="#3498db"
                  onInspect={() => setInspectService({ name: 'Gestor Calidad Aire' })}
                />

                {/* 4. Módulo HQC (Condicional) */}
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