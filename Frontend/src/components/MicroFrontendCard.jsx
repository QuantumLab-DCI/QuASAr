import React from 'react';
import { Terminal, ShieldAlert } from 'lucide-react';

const MicroFrontendCard = ({ title, port, active, reason, onInspect }) => {
    return (
        <div style={{ border: `1px solid ${active ? '#e5e7eb' : '#cbd5e1'}`, borderRadius: '8px', overflow: 'hidden', background: 'white', display: 'flex', flexDirection: 'column' }}>
            <div style={{ padding: '8px 12px', background: active ? '#f9fafb' : '#f8fafc', borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', fontWeight: '600', color: '#374151' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: active ? '#10b981' : '#64748b' }}></div>
                    {title}
                </div>
                <button onClick={onInspect} className="tool-btn" style={{ padding: '2px 6px', fontSize: '0.7rem' }} title="Inspect live container logs">
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
                    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#475569', padding: '10px', textAlign: 'center' }}>
                        <ShieldAlert size={32} style={{ marginBottom: '8px', color: '#64748b' }} />
                        <span style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>DISABLED BY POLICY</span>
                        <span style={{ fontSize: '0.75rem', marginTop: '4px' }}>{reason}</span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MicroFrontendCard;
