import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ScenarioSelector from './components/ScenarioSelector'; // Asegúrate de que ScenarioSelector.jsx esté en src/components/
import { RefreshCw, Zap, Network, Terminal } from 'lucide-react'; // Iconos
import './App.css';

const API_URL = 'http://127.0.0.1:8000';
const REFRESH_INTERVAL = 5000; // 5 segundos para ver cambios rápidos

function App() {
  const [estado, setEstado] = useState(null);
  const [logs, setLogs] = useState("Cargando logs...");
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Función para cargar datos
  const fetchData = async () => {
    try {
      const timestamp = new Date().getTime();
      // Solicitud con timestamp para evitar caché de navegador en imágenes
      const resEstado = await axios.get(`${API_URL}/api/estado?t=${timestamp}`);

      // Truco: Añadir timestamp a las URLs de las imágenes
      let data = resEstado.data;
      if (data.imagen_estado_url) data.imagen_estado_url += `?t=${timestamp}`;
      if (data.evidencia_cuantica_url) data.evidencia_cuantica_url += `?t=${timestamp}`;

      setEstado(data);

      const resLogs = await axios.get(`${API_URL}/api/logs`);
      setLogs(resLogs.data.log_content);

      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      console.error("Error:", err);
      setError("Error de conexión con Backend HQC.");
    }
  };

  // Ciclo de vida
  useEffect(() => {
    fetchData();
    const intervalId = setInterval(fetchData, REFRESH_INTERVAL);
    return () => clearInterval(intervalId);
  }, []);

  // Manejador cuando se cambia un escenario manualmente
  const handleScenarioChange = () => {
    // Forzar un refresco rápido y luego dejar que el intervalo siga
    setTimeout(fetchData, 1000);
  };

  if (error) return <div className="App error-screen"><h1>⚠️ {error}</h1></div>;
  if (!estado) return <div className="App loading-screen"><h1>Cargando sistema HQC...</h1></div>;

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

        {/* 1. PANEL DE CONTROL (ESCENARIOS) */}
        <section className="control-section">
          <ScenarioSelector onScenarioChange={handleScenarioChange} />
        </section>

        <div className="dashboard-grid">

          {/* 2. COLUMNA IZQUIERDA: VISUALIZACIÓN PRINCIPAL */}
          <div className="left-col">

            {/* Grafo de Estado */}
            <div className="panel graph-panel">
              <h2 className="panel-title"><Network className="icon" /> Estado Actual (LPSD)</h2>
              <div className="image-container state-graph">
                <img src={`${API_URL}${estado.imagen_estado_url}`} alt="Grafo de Estado" />
              </div>
            </div>

            {/* Evidencia Cuántica (NUEVO) */}
            <div className="panel quantum-panel">
              <h2 className="panel-title">
                <Zap className="icon text-yellow" /> Evidencia de Ejecución Cuántica
              </h2>
              <div className="quantum-content">
                {estado.evidencia_cuantica_url ? (
                  <>
                    <div className="image-container quantum-evidence">
                      <img
                        src={`${API_URL}${estado.evidencia_cuantica_url}`}
                        alt="Circuito Cuántico"
                        onClick={() => window.open(`${API_URL}${estado.evidencia_cuantica_url}`, '_blank')}
                      />
                    </div>
                    <p className="success-msg">✅ Ejecución exitosa en Backend HQC</p>
                  </>
                ) : (
                  <div className="placeholder-quantum">
                    <span>💤 Módulo Cuántico Inactivo (Baja complejidad)</span>
                  </div>
                )}
              </div>
            </div>

          </div>

          {/* 3. COLUMNA DERECHA: CONTEXTO Y LOGS */}
          <div className="right-col">

            {/* Tarjeta de Contexto */}
            <div className="panel context-panel">
              <h2 className="panel-title">Contexto Detectado</h2>
              <div className="metrics-list">
                <div className="metric-item">
                  <span className="metric-label">Calidad Aire (ICA)</span>
                  <span className="metric-value color-ica">{estado.contexto?.calidad_aire_ica}</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Complejidad (CP)</span>
                  <span className="metric-value color-cp">{estado.contexto?.complejidad_problema_cp}</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">SLA Prioridad</span>
                  <span className="metric-value color-sla">{estado.contexto?.prioridad_sla}</span>
                </div>
              </div>
            </div>

            {/* Modelo Estático (Referencia) */}
            <div className="panel">
              <h2 className="panel-title">Modelo de Características</h2>
              <div className="image-container">
                <img src={`${API_URL}${estado.imagen_modelo_url}`} alt="Modelo Estático" />
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