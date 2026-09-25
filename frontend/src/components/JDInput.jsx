import React, { useState } from 'react';
import { ChevronDown, ChevronUp, FileCode } from 'lucide-react';

export default function JDInput({ value, onChange }) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="jd-input-card">
      <div className="jd-header" onClick={() => setIsOpen(!isOpen)}>
        <div className="jd-title-wrap">
          <FileCode size={16} />
          <span className="jd-label">Target Job Description</span>
          <span className="jd-badge">Optional</span>
        </div>
        <button type="button" className="toggle-btn" aria-label="Toggle JD input">
          {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {isOpen && (
        <div className="jd-body">
          <textarea
            className="jd-textarea"
            rows={4}
            placeholder="Paste target job requirements here to unlock precision JD-match score and skill-gap flags..."
            value={value}
            onChange={(e) => onChange(e.target.value)}
          />
          <p className="jd-hint">
            Paste one to get JD-match + skill-gap marks alongside general ATS proofreading.
          </p>
        </div>
      )}
    </div>
  );
}
