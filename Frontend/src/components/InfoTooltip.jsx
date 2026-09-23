import React, { useCallback, useEffect, useId, useRef, useState } from 'react';
import { CircleHelp } from 'lucide-react';
import { createPortal } from 'react-dom';

const InfoTooltip = ({ label, children }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [position, setPosition] = useState({ left: 0, top: 0, width: 280 });
    const triggerRef = useRef(null);
    const tooltipRef = useRef(null);
    const tooltipId = useId();

    const updatePosition = useCallback(() => {
        if (!triggerRef.current) return;

        const rect = triggerRef.current.getBoundingClientRect();
        const tooltipHeight = tooltipRef.current?.offsetHeight ?? 160;
        const width = Math.min(280, window.innerWidth - 32);
        const left = Math.min(
            Math.max(16, rect.left + (rect.width / 2) - (width / 2)),
            window.innerWidth - width - 16
        );
        const availableAbove = rect.top;
        const availableBelow = window.innerHeight - rect.bottom;
        const opensAbove = availableBelow < tooltipHeight + 8 && availableAbove > availableBelow;
        const requestedTop = opensAbove
            ? rect.top - tooltipHeight - 8
            : rect.bottom + 8;
        const top = Math.min(
            Math.max(8, requestedTop),
            Math.max(8, window.innerHeight - tooltipHeight - 8)
        );

        setPosition({ left, top, width });
    }, []);

    const captureTooltip = useCallback((node) => {
        tooltipRef.current = node;
        if (node) updatePosition();
    }, [updatePosition]);

    const showTooltip = () => {
        updatePosition();
        setIsOpen(true);
    };

    const hideTooltip = () => setIsOpen(false);

    useEffect(() => {
        if (!isOpen) return undefined;

        const closeOnEscape = (event) => {
            if (event.key === 'Escape') {
                hideTooltip();
            }
        };
        const closeOnScroll = () => hideTooltip();
        const closeOnOutsidePointer = (event) => {
            if (!triggerRef.current?.contains(event.target)) hideTooltip();
        };

        window.addEventListener('resize', updatePosition);
        window.addEventListener('scroll', closeOnScroll, true);
        document.addEventListener('keydown', closeOnEscape);
        document.addEventListener('pointerdown', closeOnOutsidePointer);

        return () => {
            window.removeEventListener('resize', updatePosition);
            window.removeEventListener('scroll', closeOnScroll, true);
            document.removeEventListener('keydown', closeOnEscape);
            document.removeEventListener('pointerdown', closeOnOutsidePointer);
        };
    }, [isOpen, updatePosition]);

    return (
        <span className="info-tooltip-wrapper">
            <button
                ref={triggerRef}
                type="button"
                className="info-tooltip-trigger"
                aria-label={`Learn more about ${label}`}
                aria-describedby={isOpen ? tooltipId : undefined}
                onMouseEnter={showTooltip}
                onMouseLeave={() => {
                    if (document.activeElement !== triggerRef.current) hideTooltip();
                }}
                onFocus={showTooltip}
                onBlur={hideTooltip}
                onClick={(event) => {
                    event.stopPropagation();
                    showTooltip();
                }}
            >
                <CircleHelp size={14} aria-hidden="true" />
            </button>
            {isOpen && createPortal(
                <span
                    ref={captureTooltip}
                    id={tooltipId}
                    role="tooltip"
                    className="info-tooltip-content"
                    style={position}
                >
                    <strong>{label}</strong>
                    <span>{children}</span>
                </span>,
                document.body
            )}
        </span>
    );
};

export default InfoTooltip;
