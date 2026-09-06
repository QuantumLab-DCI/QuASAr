import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';
const REFRESH_INTERVAL = 3000;

/** Poll backend status and expose dashboard state and actions. */
export const useSystemStatus = () => {
    const [systemState, setSystemState] = useState(null);
    const [logs, setLogs] = useState("System ready. Select a scenario to initiate adaptation.");
    const [lastUpdate, setLastUpdate] = useState(new Date());
    const [isSystemReady, setIsSystemReady] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);

    const fetchSystemStatus = useCallback(async () => {
        try {
            const timestamp = new Date().getTime();
            const stateResponse = await axios.get(`${API_BASE_URL}/api/state?t=${timestamp}`);
            const data = stateResponse.data;

            if (data.state_image_url) data.state_image_url += `?t=${timestamp}`;
            if (data.model_image_url) data.model_image_url += `?t=${timestamp}`;
            if (data.quantum_evidence_url) data.quantum_evidence_url += `?t=${timestamp}`;

            setIsProcessing(data.is_running);
            setSystemState(data);
            setIsSystemReady(true);

            const logsResponse = await axios.get(`${API_BASE_URL}/api/logs`);
            setLogs(logsResponse.data.log_content);
            setLastUpdate(new Date());

        } catch (requestError) {
            if (requestError.response && requestError.response.status === 503) setIsSystemReady(false);
            else console.error("Backend connection error:", requestError);
        }
    }, []);

    useEffect(() => {
        const initialRequest = setTimeout(fetchSystemStatus, 0);
        const intervalId = setInterval(fetchSystemStatus, REFRESH_INTERVAL);
        return () => {
            clearTimeout(initialRequest);
            clearInterval(intervalId);
        };
    }, [fetchSystemStatus]);

    const refreshNow = () => {
        setIsProcessing(true);
        setTimeout(fetchSystemStatus, 1000);
    };

    const downloadImage = async (imageUrl) => {
        if (!imageUrl) return;
        try {
            const fullUrl = imageUrl.startsWith('http')
                ? imageUrl
                : `${API_BASE_URL}${imageUrl.startsWith('/') ? '' : '/'}${imageUrl}`;

            const response = await axios.get(fullUrl, { maxRedirects: 0, responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `hqc_execution_evidence_${new Date().getTime()}.png`);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error("Image download error:", error);
            alert("The image could not be downloaded.");
        }
    };

    return {
        systemState,
        logs,
        lastUpdate,
        isSystemReady,
        isProcessing,
        refreshNow,
        downloadImage,
        apiBaseUrl: API_BASE_URL
    };
};
