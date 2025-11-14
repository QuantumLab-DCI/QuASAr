import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// URL de tu API de Flask
const API_URL = 'http://127.0.0.1:8000';
// Intervalo de refresco (en milisegundos)
const REFRESH_INTERVAL = 3000; // 3 segundos

function App() {
  const [estado, setEstado] = useState(null);
  const [logs, setLogs] = useState("Cargando logs...");
  const [error, setError] = useState(null);

  // Función para cargar todos los datos del backend
  const fetchData = async () => {
    try {
      // Pedir el estado principal (imágenes y contexto)
      const resEstado = await axios.get(`${API_URL}/api/estado`);
      setEstado(resEstado.data);
      
      // Pedir los logs
      const resLogs = await axios.get(`${API_URL}/api/logs`);
      setLogs(resLogs.data.log_content); // Accedemos al contenido del JSON
      
      setError(null);
    } catch (err) {
      console.error("Error al cargar datos:", err);
      if (err.code === "ERR_NETWORK") {
        setError("No se pudo conectar al back-end. ¿Está encendido?");
      } else {
        setError("El back-end está arrancando. Esperando el primer ciclo...");
      }
    }
  };

  // Hook de Efecto: Carga los datos al inicio y luego
  // establece un intervalo para refrescar cada 3 segundos.
  useEffect(() => {
    fetchData(); // Carga inicial
    
    // Configura el intervalo
    const intervalId = setInterval(fetchData, REFRESH_INTERVAL); 

    // Limpia el intervalo cuando el componente se "desmonta"
    return () => clearInterval(intervalId);
  }, []); // El array vacío [] significa que esto se ejecuta solo una vez (al montar)

  // --- Renderizado ---

  if (error) {
    return <div className="App"><h1>Error: {error}</h1></div>;
  }

  if (!estado) {
    return <div className="App"><h1>Cargando estado del sistema...</h1></div>;
  }

  // Truco para evitar el caché de la imagen
  const imageUrl = `${API_URL}${estado.imagen_estado_url}?t=${new Date().getTime()}`;

  return (
    <div className="App">
      <header className="App-header">
        <h1>Dashboard de Adaptación Híbrida</h1>
      </header>
      
      <div className="container">
        
        {/* Panel Izquierdo: Estado Actual */}
        <div className="panel">
          <h2>Estado Actual del Sistema</h2>
          <div className="context-info">
            <p><strong>Calidad del Aire (ICA):</strong> {estado.contexto?.calidad_aire_ica}</p>
            <p><strong>Complejidad Problema (CP):</strong> {estado.contexto?.complejidad_problema_cp}</p>
          </div>
          <img 
            src={imageUrl} 
            alt="Estado actual del sistema" 
            className="status-image"
          />
        </div>
        
        {/* Panel Derecho: Modelo y Logs */}
        <div className="panel-right">
          <div className="panel">
            <h2>Log de Cambios</h2>
            <pre className="log-box">
              {logs}
            </pre>
          </div>
          
          <div className="panel">
            <h2>Modelo de Características</h2>
            <img 
              src={`${API_URL}${estado.imagen_modelo_url}`} 
              alt="Modelo de características" 
              className="status-image"
            />
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;