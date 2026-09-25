import React, { useEffect, useState, useRef } from 'react';
import AnnotationNote from './AnnotationNote';

export default function AnnotationMargin({
  annotations,
  activeAnchorId,
  hoveredAnchorId,
  onHoverAnchor,
  onClickAnchor,
  documentRef
}) {
  const [positions, setPositions] = useState({});
  const marginContainerRef = useRef(null);

  // Calculate vertical alignment with respect to anchored DOM elements
  const updatePositions = () => {
    if (!documentRef?.current || !marginContainerRef?.current) return;

    const docContainer = documentRef.current;
    const docRect = docContainer.getBoundingClientRect();
    const marginRect = marginContainerRef.current.getBoundingClientRect();
    const newPositions = {};

    let lastTop = 0;
    const minSpacing = 16; // minimum pixels between notes

    annotations.forEach((ann) => {
      const targetEl = docContainer.querySelector(`[data-anchor-id="${ann.anchorId}"]`);
      if (targetEl) {
        const targetRect = targetEl.getBoundingClientRect();
        // Calculate offset from top of document container
        let idealTop = targetRect.top - docRect.top;

        // Prevent overlap by pushing down if necessary
        if (idealTop < lastTop + minSpacing) {
          idealTop = lastTop + minSpacing;
        }

        newPositions[ann.id] = Math.max(0, idealTop);
        lastTop = idealTop + 70; // approximate note height
      }
    });

    setPositions(newPositions);
  };

  useEffect(() => {
    updatePositions();
    const timer = setTimeout(updatePositions, 100);
    window.addEventListener('resize', updatePositions);
    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', updatePositions);
    };
  }, [annotations]);

  return (
    <aside className="annotation-margin" ref={marginContainerRef}>
      <div className="margin-legend">
        <span className="legend-title">MARGIN PROOF MARKS ({annotations.length})</span>
      </div>

      <div className="notes-stack">
        {annotations.map((ann) => {
          const isHighlighted =
            activeAnchorId === ann.anchorId || hoveredAnchorId === ann.anchorId;
          const topOffset = positions[ann.id];

          return (
            <div
              key={ann.id}
              className={`note-position-wrapper ${isHighlighted ? 'active-guide' : ''}`}
              style={{
                transform: topOffset !== undefined ? `translateY(${topOffset}px)` : 'none',
              }}
            >
              {isHighlighted && <div className="connecting-rule" />}
              <AnnotationNote
                annotation={ann}
                isHighlighted={isHighlighted}
                onHover={onHoverAnchor}
                onClick={onClickAnchor}
              />
            </div>
          );
        })}
      </div>
    </aside>
  );
}
