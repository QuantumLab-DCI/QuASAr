// src/hooks/useSystemStatus.js
import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';
const REFRESH_INTERVAL = 3000;

export const useSystemStatus = () => {
    const [estado, setEstado] = useState(null);
    const [logs, setLogs] = useState("Sistema listo. Seleccione un escenario para iniciar.");
    const [lastUpdate, setLastUpdate] = useState(new Date());
    const [isSystemReady, setIsSystemReady] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);

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

    const refreshNow = () => {
        setIsProcessing(true);
        setTimeout(fetchData, 1000);
    };

    // Función de descarga (utilidad)
    const downloadImage = async (imageUrl) => {
        if (!imageUrl) return;
        try {
            const fullUrl = imageUrl.startsWith('http')
                ? imageUrl
                : `${API_URL}${imageUrl.startsWith('/') ? '' : '/'}${imageUrl}`;

            const response = await axios.get(fullUrl, { maxRedirects: 0, responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `evidencia_hqc_${new Date().getTime()}.png`);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error("Error descargando imagen:", error);
            alert("Error al descargar la imagen.");
        }
    };

    return {
        estado,
        logs,
        lastUpdate,
        isSystemReady,
        isProcessing,
        refreshNow,
        downloadImage,
        API_URL
    };
};
