import React, { useState, useRef } from 'react';
import ScoreHeader from './components/ScoreHeader';
import UploadDropzone from './components/UploadDropzone';
import ResumeDocument from './components/ResumeDocument';
import AnnotationMargin from './components/AnnotationMargin';
import AnalysisProgress from './components/AnalysisProgress';
import ErrorNotice from './components/ErrorNotice';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

export default function App() {
  const [viewState, setViewState] = useState('upload'); // 'upload' | 'loading' | 'results' | 'error'
  const [analysisData, setAnalysisData] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [activeAnchorId, setActiveAnchorId] = useState(null);
  const [hoveredAnchorId, setHoveredAnchorId] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);

  const documentRef = useRef(null);

  const handleAnalyze = async ({ file, text, jobDescription }) => {
    setViewState('loading');
    setErrorMessage('');

    try {
      const formData = new FormData();
      if (file) {
        formData.append('file', file);
      }
      if (text) {
        formData.append('text', text);
      }
      if (jobDescription) {
        formData.append('job_description', jobDescription);
      }

      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Couldn't read that file — try a text-based PDF or DOCX (scanned images aren't supported yet).");
      }

      const data = await response.json();
      setAnalysisData(data);
      setViewState('results');
    } catch (err) {
      console.error('Analysis error:', err);
      setErrorMessage(err.message);
      setViewState('error');
    }
  };

  const handleLoadSample = async () => {
    setViewState('loading');
    setErrorMessage('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/sample`);
      if (!response.ok) {
        throw new Error('Failed to load sample analysis.');
      }
      const data = await response.json();
      setAnalysisData(data);
      setViewState('results');
    } catch (err) {
      console.error('Sample load error:', err);
      setErrorMessage(err.message);
      setViewState('error');
    }
  };

  const handleReset = () => {
    setViewState('upload');
    setAnalysisData(null);
    setActiveAnchorId(null);
    setHoveredAnchorId(null);
    setSelectedCategory(null);
  };

  const handleAnchorClick = (anchorId) => {
    setActiveAnchorId(anchorId);
    if (documentRef.current) {
      const target = documentRef.current.querySelector(`[data-anchor-id="${anchorId}"]`);
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  };

  // Filter annotations based on category if selected
  const displayedAnnotations = analysisData?.annotations.filter((ann) => {
    if (!selectedCategory) return true;
    if (selectedCategory === 'ats') return ann.flagType === 'amber' || ann.label.toLowerCase().includes('ats');
    if (selectedCategory === 'skillGap') return ann.flagType === 'red';
    if (selectedCategory === 'jdMatch') return ann.label.toLowerCase().includes('jd') || ann.flagType === 'red';
    if (selectedCategory === 'general') return ann.flagType === 'green' || ann.flagType === 'amber';
    return true;
  }) || [];

  return (
    <div className="app-layout">
      {viewState === 'results' && analysisData && (
        <ScoreHeader
          scores={analysisData.scores}
          onReset={handleReset}
          activeCategory={selectedCategory}
          onSelectCategory={setSelectedCategory}
        />
      )}

      {viewState === 'upload' && (
        <UploadDropzone
          onAnalyze={handleAnalyze}
          onLoadSample={handleLoadSample}
          isLoading={false}
        />
      )}

      {viewState === 'loading' && <AnalysisProgress />}

      {viewState === 'error' && (
        <ErrorNotice message={errorMessage} onRetry={() => setViewState('upload')} />
      )}

      {viewState === 'results' && analysisData && (
        <div className="results-container">
          <div className="manuscript-stage">
            {/* Left: Resume Document */}
            <ResumeDocument
              documentData={analysisData.document}
              annotations={displayedAnnotations}
              activeAnchorId={activeAnchorId}
              hoveredAnchorId={hoveredAnchorId}
              onHoverAnchor={setHoveredAnchorId}
              onClickAnchor={handleAnchorClick}
              documentRef={documentRef}
            />

            {/* Right: Annotation Margin */}
            <AnnotationMargin
              annotations={displayedAnnotations}
              activeAnchorId={activeAnchorId}
              hoveredAnchorId={hoveredAnchorId}
              onHoverAnchor={setHoveredAnchorId}
              onClickAnchor={handleAnchorClick}
              documentRef={documentRef}
            />
          </div>
        </div>
      )}
    </div>
  );
}
