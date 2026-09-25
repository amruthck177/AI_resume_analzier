import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export default function ErrorNotice({ message, onRetry }) {
  return (
    <div className="error-screen">
      <div className="error-card">
        <div className="error-icon-box">
          <AlertCircle size={28} className="error-icon" />
        </div>
        <h2 className="error-title">Analysis Interrupted</h2>
        <p className="error-message">
          {message || "Couldn't read that file — try a text-based PDF or DOCX (scanned images aren't supported yet)."}
        </p>
        <button type="button" className="error-action-btn" onClick={onRetry}>
          <RefreshCw size={14} />
          <span>Choose Another File</span>
        </button>
      </div>
    </div>
  );
}
