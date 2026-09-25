import React from 'react';
import AnnotationNote from './AnnotationNote';

export default function ResumeDocument({
  documentData,
  annotations,
  activeAnchorId,
  hoveredAnchorId,
  onHoverAnchor,
  onClickAnchor,
  documentRef
}) {
  if (!documentData) return null;

  const { candidateName, contactInfo, sections } = documentData;

  // Map of anchorId -> array of annotations for inline display on mobile
  const inlineAnnotationsMap = {};
  annotations.forEach((ann) => {
    if (!inlineAnnotationsMap[ann.anchorId]) {
      inlineAnnotationsMap[ann.anchorId] = [];
    }
    inlineAnnotationsMap[ann.anchorId].push(ann);
  });

  return (
    <main className="resume-document-pane" ref={documentRef}>
      <article className="resume-sheet">
        {/* Document Header */}
        <header className="resume-header">
          <h2 className="candidate-name">{candidateName}</h2>
          {contactInfo && <p className="candidate-contact">{contactInfo}</p>}
        </header>

        {/* Sections */}
        <div className="resume-sections">
          {sections.map((section) => (
            <section key={section.id} id={section.id} className="resume-section">
              <h3 className="section-title">{section.title}</h3>
              <div className="section-divider" />

              <div className="section-items">
                {section.items.map((item) => {
                  const isReferenced = annotations.some((a) => a.anchorId === item.id);
                  const isHighlighted =
                    activeAnchorId === item.id || hoveredAnchorId === item.id;
                  const itemInlineNotes = inlineAnnotationsMap[item.id] || [];

                  // Find primary flag type if referenced
                  const primaryFlag = annotations.find((a) => a.anchorId === item.id)?.flagType;

                  return (
                    <div
                      key={item.id}
                      data-anchor-id={item.id}
                      className={`resume-item type-${item.itemType} ${
                        isReferenced ? `flagged-item flag-${primaryFlag}` : ''
                      } ${isHighlighted ? 'active-target' : ''}`}
                      onMouseEnter={() => isReferenced && onHoverAnchor(item.id)}
                      onMouseLeave={() => isReferenced && onHoverAnchor(null)}
                      onClick={() => isReferenced && onClickAnchor(item.id)}
                    >
                      {item.itemType === 'bullet' ? (
                        <div className="bullet-row">
                          <span className="bullet-disc">•</span>
                          <span className="item-text">{item.text}</span>
                        </div>
                      ) : item.itemType === 'subheading' ? (
                        <h4 className="item-subheading">{item.text}</h4>
                      ) : (
                        <p className="item-text">{item.text}</p>
                      )}

                      {/* Mobile-only inline annotations */}
                      {itemInlineNotes.length > 0 && (
                        <div className="mobile-inline-annotations">
                          {itemInlineNotes.map((n) => (
                            <AnnotationNote
                              key={n.id}
                              annotation={n}
                              isHighlighted={isHighlighted}
                              onHover={onHoverAnchor}
                              onClick={onClickAnchor}
                            />
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </section>
          ))}
        </div>
      </article>
    </main>
  );
}
