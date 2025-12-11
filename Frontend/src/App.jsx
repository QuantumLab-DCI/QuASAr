import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ScenarioSelector from './components/ScenarioSelector';
// Se agrega Loader2 a las importaciones
import { RefreshCw, Zap, Network, Terminal, Info, Brain, Download, Maximize2, ExternalLink, X, Activity, GitMerge, Box, CheckCircle, Loader2 } from 'lucide-react';
import './App.css';

const API_URL = 'http://127.0.0.1:8000';
const REFRESH_INTERVAL = 3000;

// 1. REEMPLAZA TU COMPONENTE LoadingBlock POR ESTA VERSIÓN MEJORADA
const LoadingBlock = ({ loading, children, message = "Procesando..." }) => {
  return (
    <div className="loading-wrapper" style={{
      /* Usamos flex: 1 para que ocupe el espacio restante, no 'height: 100%' que causa desbordamiento */
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      position: 'relative',
      minHeight: 0, /* Crítico para que el scroll funcione dentro de flexbox */
      overflow: 'hidden' /* Asegura que nada se salga del contenedor */
    }}>
      {loading && (
        <div className="loading-overlay" style={{
          position: 'absolute', top: 0, left: 0, width: '100%', height: '100%',
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          zIndex: 10, backdropFilter: 'blur(2px)', backgroundColor: 'rgba(255,255,255,0.1)',
          color: '#61dafb', fontWeight: 'bold', textShadow: '0 2px 4px rgba(0,0,0,0.8)'
        }}>
          <Loader2 size={40} className="spinner-icon" style={{ animation: 'spin 1s linear infinite', marginBottom: '10px' }} />
          <span>{message}</span>
        </div>
      )}
      {/* El contenedor interno también debe crecer para llenar el espacio */}
      <div className={loading ? "loading-blur" : ""} style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        minHeight: 0, /* Permite que el hijo (mapek-timeline) maneje su propio scroll */
        overflow: 'hidden', /* Delega el scroll al hijo */
        ...(loading ? { filter: 'blur(4px)', opacity: 0.7, pointerEvents: 'none' } : {})
      }}>
        {children}
      </div>
    </div>
  );
};

// Estilo inline para la animación del spinner (si no está en el CSS)
const styleSheet = document.createElement("style");
styleSheet.innerText = `
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
`;
document.head.appendChild(styleSheet);


function App() {
  const [estado, setEstado] = useState(null);
  const [logs, setLogs] = useState("Sistema listo. Seleccione un escenario para iniciar.");
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [isSystemReady, setIsSystemReady] = useState(false);

  // Estado para el Modal de visualización (Lightbox)
  const [modalImage, setModalImage] = useState(null);

  // Estado para saber si el sistema está ocupado (Bloqueo de UI)
  const [isProcessing, setIsProcessing] = useState(false);

  const fetchData = async () => {
    try {
      const timestamp = new Date().getTime();

      // 1. Obtener Estado General desde el Backend
      const resEstado = await axios.get(`${API_URL}/api/estado?t=${timestamp}`);
      let data = resEstado.data;

      // Truco cache-busting para forzar recarga de imágenes si cambian
      if (data.imagen_estado_url) data.imagen_estado_url += `?t=${timestamp}`;
      if (data.evidencia_cuantica_url) data.evidencia_cuantica_url += `?t=${timestamp}`;

      // Actualizar semáforo de ocupación desde el backend
      // Si el backend dice que terminó (false), se quita el blur. Si sigue (true), se mantiene.
      setIsProcessing(data.en_ejecucion);

      setEstado(data);
      setIsSystemReady(true);

      // 2. Obtener Logs del sistema
      const resLogs = await axios.get(`${API_URL}/api/logs`);
      setLogs(resLogs.data.log_content);

      setLastUpdate(new Date());

    } catch (err) {
      // Si el backend devuelve 503, es que aún está iniciando
      if (err.response && err.response.status === 503) {
        setIsSystemReady(false);
      } else {
        console.error("Error de conexión:", err);
      }
    }
  };

  // Polling automático cada 3 segundos
  useEffect(() => {
    fetchData();
    const intervalId = setInterval(fetchData, REFRESH_INTERVAL);
    return () => clearInterval(intervalId);
  }, []);

  const handleScenarioChange = () => {
    // CAMBIO IMPORTANTE:
    // Ya no limpiamos el estado (setEstado) para evitar que los componentes desaparezcan.
    // Solo activamos el modo "Procesando" para activar el Blur y el Spinner sobre lo viejo.
    setIsProcessing(true);

    // Damos un respiro antes de volver a consultar
    setTimeout(fetchData, 1000);
  };

  // Función para forzar la descarga de la imagen de evidencia
  const handleDownload = async (imageUrl) => {
    try {
      const response = await fetch(`${API_URL}${imageUrl}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `evidencia_cuantica_${new Date().getTime()}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error descargando imagen:", error);
    }
  };

  // Helper para icono según fase MAPE-K
  const getPhaseIcon = (fase) => {
    if (fase.includes("MONITOR")) return <Activity size={16} />;
    if (fase.includes("ANÁLISIS")) return <Brain size={16} />;
    if (fase.includes("PLAN")) return <GitMerge size={16} />;
    if (fase.includes("EJECUCIÓN")) return <Box size={16} />;
    if (fase.includes("FIN")) return <CheckCircle size={16} />;
    return <Info size={16} />;
  };

  return (
    <div className="App">

      {/* --- COMPONENTE MODAL (Lightbox) --- */}
      {modalImage && (
        <div className="modal-overlay" onClick={() => setModalImage(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setModalImage(null)}>
              <X size={24} />
            </button>
            <img src={`${API_URL}${modalImage}`} alt="Evidencia Ampliada" />
            <div className="modal-footer">
              <span className="modal-caption">Vista detallada del artefacto generado</span>
            </div>
          </div>
        </div>
      )}

      <header className="App-header">
        <div className="header-content">
          <h1>⚛️ Arquitectura Híbrida Auto-adaptativa (HQC)</h1>
          <div className="header-meta">
            <span>Última act: {lastUpdate.toLocaleTimeString()}</span>
            <button onClick={fetchData} className="refresh-btn" title="Actualizar ahora">
              <RefreshCw size={18} />
            </button>
          </div>
        </div>
      </header>

      <div className="main-container">

        {/* SECCIÓN 1: CONTROL (Selector de Escenarios) */}
        <section className="control-section">
          {/* Pasamos el estado de bloqueo al hijo para deshabilitar clics */}
          <ScenarioSelector
            onScenarioChange={handleScenarioChange}
            isSystemBusy={isProcessing}
          />
        </section>

        {/* SECCIÓN 2: VISUALIZACIÓN (Dashboard) */}
        <div className="dashboard-grid">

          {/* COLUMNA IZQUIERDA */}
          <div className="left-col">

            {/* Panel 1: Grafo de Estado (Arquitectura Viva) */}
            <div className="panel graph-panel">
              <h2 className="panel-title"><Network className="icon" /> Estado Actual (LPSD)</h2>

              {/* ENVUELA EL CONTENIDO CON LOADINGBLOCK */}
              <LoadingBlock loading={isProcessing} message="Adaptando Arquitectura...">
                <div className="image-container state-graph">
                  {isSystemReady && estado?.imagen_estado_url ? (
                    <img
                      src={`${API_URL}${estado.imagen_estado_url}`}
                      alt="Grafo de Estado"
                      className="clickable-image"
                      onClick={() => !isProcessing && setModalImage(estado.imagen_estado_url)} // Bloquea click si carga
                      title="Clic para ampliar arquitectura"
                    />
                  ) : (
                    <div className="placeholder-state">
                      <Info size={40} className="text-gray-300 mb-2" />
                      <p className="text-gray-400">Selecciona un escenario para generar la arquitectura dinámica.</p>
                    </div>
                  )}
                </div>
              </LoadingBlock>
            </div>

            {/* Panel 2: Evidencia Cuántica (Circuitos) */}
            <div className="panel quantum-panel">
              <h2 className="panel-title">
                <Zap className="icon text-yellow" /> Evidencia de Ejecución Cuántica
              </h2>

              {/* ENVUELA EL CONTENIDO CON LOADINGBLOCK */}
              <LoadingBlock loading={isProcessing} message="Generando Circuito...">
                <div className="quantum-content">
                  {isSystemReady && estado?.evidencia_cuantica_url ? (
                    <div className="evidence-wrapper">
                      {/* Imagen del Circuito */}
                      <div className="image-container quantum-evidence">
                        <img
                          src={`${API_URL}${estado.evidencia_cuantica_url}`}
                          alt="Circuito Cuántico"
                          onError={(e) => { e.target.style.display = 'none'; e.target.parentNode.innerText = '⚠️ Error cargando imagen' }}
                          onClick={() => !isProcessing && setModalImage(estado.evidencia_cuantica_url)}
                        />
                      </div>

                      {/* Barra de Herramientas de Evidencia */}
                      <div className="evidence-toolbar">
                        <button
                          className="tool-btn"
                          onClick={() => handleDownload(estado.evidencia_cuantica_url)}
                          disabled={isProcessing}
                          title="Descargar Imagen PNG"
                        >
                          <Download size={16} /> Descargar
                        </button>
                        <button
                          className="tool-btn"
                          onClick={() => setModalImage(estado.evidencia_cuantica_url)}
                          disabled={isProcessing}
                          title="Ver en grande (Lightbox)"
                        >
                          <Maximize2 size={16} /> Ampliar
                        </button>
                        <button
                          className="tool-btn"
                          onClick={() => window.open(`${API_URL}${estado.evidencia_cuantica_url}`, '_blank')}
                          disabled={isProcessing}
                          title="Abrir imagen en nueva pestaña"
                        >
                          <ExternalLink size={16} /> Pestaña
                        </button>
                      </div>

                      <p className="success-msg">✅ Ejecución exitosa en Backend HQC</p>
                    </div>
                  ) : (
                    <div className="placeholder-quantum">
                      {isSystemReady ? (
                        <span>💤 Módulo Cuántico Inactivo (Baja complejidad o decisión del Agente)</span>
                      ) : (
                        <span>Esperando ejecución...</span>
                      )}
                    </div>
                  )}
                </div>
              </LoadingBlock>
            </div>
          </div>

          {/* COLUMNA DERECHA */}
          <div className="right-col">

            {/* Panel 3: Trace MAPE-K en Vivo */}
            <div className="panel mapek-panel">
              <h2 className="panel-title">🔄 Ciclo de Adaptación (Paso a Paso)</h2>

              {/* ENVUELA EL CONTENIDO CON LOADINGBLOCK */}
              <LoadingBlock loading={isProcessing} message="Ejecutando MAPE-K...">
                <div className="mapek-timeline">
                  {estado?.mapek_trace && estado.mapek_trace.length > 0 ? (
                    estado.mapek_trace.map((paso, index) => (
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
                        {paso.detalles && (
                          <div className="step-details">
                            <pre>{JSON.stringify(paso.detalles, null, 2)}</pre>
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="p-4 text-center text-gray-400 text-sm">
                      Esperando inicio del ciclo...
                    </div>
                  )}
                </div>
              </LoadingBlock>
            </div>

            {/* Panel 4: Contexto y Razonamiento */}
            <div className="panel context-panel">
              <h2 className="panel-title">Análisis Inteligente</h2>

              {/* ENVUELA EL CONTENIDO CON LOADINGBLOCK */}
              <LoadingBlock loading={isProcessing} message="Consultando LLM...">
                {isSystemReady && estado?.contexto ? (
                  <div>
                    <div className="metrics-list mb-4">
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

                    {estado.contexto.razonamiento && (
                      <div className="reasoning-box">
                        <h4 className="reasoning-title">
                          <Brain size={16} style={{ marginRight: '6px' }} />
                          Decisión del Agente (LLM)
                        </h4>
                        <p className="reasoning-text">
                          "{estado.contexto.razonamiento}"
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="p-4 text-center text-gray-400 text-sm">Sin datos de contexto.</div>
                )}
              </LoadingBlock>
            </div>

            {/* Panel 5: Logs */}
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