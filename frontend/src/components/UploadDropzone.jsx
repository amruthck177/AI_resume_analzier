import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, ArrowRight, Sparkles, Check, X } from 'lucide-react';
import JDInput from './JDInput';

export default function UploadDropzone({ onAnalyze, onLoadSample, isLoading }) {
  const [file, setFile] = useState(null);
  const [rawText, setRawText] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [activeTab, setActiveTab] = useState('file'); // 'file' | 'text'
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!file && !rawText.trim()) return;
    onAnalyze({ file, text: rawText, jobDescription });
  };

  const canSubmit = (file || rawText.trim().length > 20) && !isLoading;

  return (
    <div className="upload-container">
      <div className="upload-card">
        {/* Header */}
        <div className="upload-header">
          <span className="upload-kicker">EDITORIAL MANUSCRIPT REVIEW</span>
          <h1 className="upload-title">AI Resume Analyzer</h1>
          <p className="upload-subtitle">
            Hand your resume to a meticulous proofreader. Feedback lives in the margin, anchored to the exact line it critiques.
          </p>
        </div>

        {/* Input Mode Tabs */}
        <div className="mode-tabs">
          <button
            type="button"
            className={`tab-btn ${activeTab === 'file' ? 'active' : ''}`}
            onClick={() => setActiveTab('file')}
          >
            <UploadCloud size={14} />
            <span>Upload File (PDF / DOCX)</span>
          </button>
          <button
            type="button"
            className={`tab-btn ${activeTab === 'text' ? 'active' : ''}`}
            onClick={() => setActiveTab('text')}
          >
            <FileText size={14} />
            <span>Paste Resume Text</span>
          </button>
        </div>

        {/* Dropzone area */}
        <form onSubmit={handleSubmit} className="upload-form">
          {activeTab === 'file' ? (
            <div
              className={`dropzone-box ${dragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                className="hidden-file-input"
                onChange={handleFileChange}
              />
              {file ? (
                <div className="file-selected-view">
                  <div className="file-info-badge">
                    <FileText size={20} className="file-icon" />
                    <div className="file-details">
                      <span className="file-name">{file.name}</span>
                      <span className="file-size">{(file.size / 1024).toFixed(1)} KB</span>
                    </div>
                  </div>
                  <button
                    type="button"
                    className="remove-file-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      setFile(null);
                    }}
                    title="Remove file"
                  >
                    <X size={16} />
                  </button>
                </div>
              ) : (
                <div className="dropzone-empty-content">
                  <UploadCloud size={32} className="dropzone-icon" />
                  <p className="drop-main-text">Drop your resume here</p>
                  <p className="drop-sub-text">PDF or DOCX · or click to browse</p>
                </div>
              )}
            </div>
          ) : (
            <div className="paste-text-box">
              <textarea
                className="resume-textarea"
                rows={8}
                placeholder="Paste the plain text of your resume here..."
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
              />
            </div>
          )}

          {/* Job Description */}
          <JDInput value={jobDescription} onChange={setJobDescription} />

          {/* Action Row */}
          <div className="upload-actions">
            <button
              type="button"
              className="sample-btn"
              onClick={onLoadSample}
              disabled={isLoading}
            >
              <Sparkles size={14} />
              <span>Load Sample Resume</span>
            </button>

            <button
              type="submit"
              className="analyze-submit-btn"
              disabled={!canSubmit}
            >
              <span>{isLoading ? 'Analyzing…' : 'Analyze resume →'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
