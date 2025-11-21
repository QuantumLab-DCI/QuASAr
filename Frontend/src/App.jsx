import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ScenarioSelector from './components/ScenarioSelector';
import { RefreshCw, Zap, Network, Terminal, Info } from 'lucide-react';
import './App.css';

const API_URL = 'http://127.0.0.1:8000';
const REFRESH_INTERVAL = 3000;

function App() {
  const [estado, setEstado] = useState(null);
  const [logs, setLogs] = useState("Sistema listo. Seleccione un escenario para iniciar.");
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [isSystemReady, setIsSystemReady] = useState(false);

  // Función para cargar datos
  const fetchData = async () => {
    try {
      const timestamp = new Date().getTime();

      // 1. Obtener Estado
      const resEstado = await axios.get(`${API_URL}/api/estado?t=${timestamp}`);
      let data = resEstado.data;

      // Truco cache-busting para imágenes
      if (data.imagen_estado_url) data.imagen_estado_url += `?t=${timestamp}`;
      if (data.evidencia_cuantica_url) data.evidencia_cuantica_url += `?t=${timestamp}`;

      setEstado(data);
      setIsSystemReady(true);

      // 2. Obtener Logs
      const resLogs = await axios.get(`${API_URL}/api/logs`);
      setLogs(resLogs.data.log_content);

      setLastUpdate(new Date());

    } catch (err) {
      if (err.response && err.response.status === 503) {
        // 503 es normal al inicio (sistema en espera)
        setIsSystemReady(false);
      } else {
        console.error("Error de conexión:", err);
      }
    }
  };

  // Polling
  useEffect(() => {
    fetchData();
    const intervalId = setInterval(fetchData, REFRESH_INTERVAL);
    return () => clearInterval(intervalId);
  }, []);

  // Handler cambio de escenario
  const handleScenarioChange = () => {
    setTimeout(fetchData, 1000);
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1>⚛️ Arquitectura Híbrida Auto-adaptativa</h1>
          <div className="header-meta">
            <span>Última act: {lastUpdate.toLocaleTimeString()}</span>
            <button onClick={fetchData} className="refresh-btn" title="Actualizar ahora">
              <RefreshCw size={18} />
            </button>
          </div>
        </div>
      </header>

      <div className="main-container">

        {/* SECCIÓN 1: CONTROL */}
        <section className="control-section">
          <ScenarioSelector onScenarioChange={handleScenarioChange} />
        </section>

        {/* SECCIÓN 2: VISUALIZACIÓN */}
        <div className="dashboard-grid">

          {/* COLUMNA IZQUIERDA */}
          <div className="left-col">

            {/* Grafo de Estado */}
            <div className="panel graph-panel">
              <h2 className="panel-title"><Network className="icon" /> Estado Actual (LPSD)</h2>
              <div className="image-container state-graph">
                {isSystemReady && estado?.imagen_estado_url ? (
                  <img src={`${API_URL}${estado.imagen_estado_url}`} alt="Grafo de Estado" />
                ) : (
                  <div className="placeholder-state">
                    <Info size={40} className="text-gray-300 mb-2" />
                    <p className="text-gray-400">Selecciona un escenario para generar la arquitectura.</p>
                  </div>
                )}
              </div>
            </div>

            {/* Evidencia Cuántica */}
            <div className="panel quantum-panel">
              <h2 className="panel-title">
                <Zap className="icon text-yellow" /> Evidencia de Ejecución Cuántica
              </h2>
              <div className="quantum-content">
                {isSystemReady && estado?.evidencia_cuantica_url ? (
                  <>
                    <div className="image-container quantum-evidence">
                      <img
                        src={`${API_URL}${estado.evidencia_cuantica_url}`}
                        alt="Circuito Cuántico"
                        // Manejo de error de carga de imagen
                        onError={(e) => { e.target.style.display = 'none'; e.target.parentNode.innerText = '⚠️ Error cargando imagen' }}
                        onClick={() => window.open(`${API_URL}${estado.evidencia_cuantica_url}`, '_blank')}
                      />
                    </div>
                    <p className="success-msg">✅ Ejecución exitosa en Backend HQC</p>
                  </>
                ) : (
                  <div className="placeholder-quantum">
                    {isSystemReady ? (
                      <span>💤 Módulo Cuántico Inactivo (Baja complejidad)</span>
                    ) : (
                      <span>Esperando ejecución...</span>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* COLUMNA DERECHA */}
          <div className="right-col">

            {/* Contexto */}
            <div className="panel context-panel">
              <h2 className="panel-title">Contexto Detectado</h2>
              {isSystemReady && estado?.contexto ? (
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
              ) : (
                <div className="p-4 text-center text-gray-400 text-sm">Sin datos.</div>
              )}
            </div>

            {/* Modelo Estático */}
            <div className="panel">
              <h2 className="panel-title">Modelo de Características</h2>
              <div className="image-container">
                <img
                  src={`${API_URL}/api/static/modelo_caracteristicas.png`}
                  onError={(e) => e.target.style.display = 'none'}
                  alt="Modelo Estático"
                />
              </div>
            </div>

            {/* Logs */}
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