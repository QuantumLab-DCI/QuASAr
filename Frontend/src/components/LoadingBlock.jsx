// src/components/LoadingBlock.jsx
import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingBlock = ({ loading, children, message = "Processing..." }) => {
    return (
        <div className="loading-wrapper">
            {loading && (
                <div className="loading-overlay glass-effect">
                    <div className="spinner-container">
                        <Loader2 size={48} className="spinner-icon" />
                        <div className="spinner-pulse"></div>
                    </div>
                    <span className="loading-message">{message}</span>
                </div>
            )}
            <div className={`loading-content ${loading ? "blurred" : ""}`}>
                {children}
            </div>
        </div>
    );
};

export default LoadingBlock;
