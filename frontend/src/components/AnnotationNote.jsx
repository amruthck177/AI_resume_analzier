import React from 'react';

export default function AnnotationNote({ annotation, isHighlighted, onHover, onClick }) {
  const { id, anchorId, flagType, symbol, label, fixText } = annotation;

  return (
    <article
      id={id}
      data-anchor-target={anchorId}
      className={`annotation-note flag-${flagType} ${isHighlighted ? 'highlighted' : ''}`}
      onMouseEnter={() => onHover && onHover(anchorId)}
      onMouseLeave={() => onHover && onHover(null)}
      onClick={() => onClick && onClick(anchorId)}
      tabIndex={0}
      role="button"
      aria-label={`${label}: ${fixText}`}
    >
      <div className="note-header">
        <span className="note-symbol" aria-hidden="true">{symbol}</span>
        <span className="note-label">{label}</span>
      </div>
      <p className="note-fix">{fixText}</p>
    </article>
  );
}
