import React from 'react';
import { ArrowLeft, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

export default function ScoreHeader({ scores, onReset, activeCategory, onSelectCategory }) {
  if (!scores) return null;

  const categories = [
    { key: 'general', label: 'General', val: scores.general },
    { key: 'ats', label: 'ATS', val: scores.ats },
    { key: 'jdMatch', label: 'JD Match', val: scores.jdMatch },
    { key: 'skillGap', label: 'Skill Gap', val: scores.skillGap },
  ];

  return (
    <header className="score-header-sticky">
      <div className="score-header-inner">
        <div className="score-header-left">
          <button className="back-btn" onClick={onReset} title="Review another resume">
            <ArrowLeft size={16} />
            <span>New Review</span>
          </button>
          <div className="app-branding">
            <span className="app-kicker">EDITORIAL MANUSCRIPT REVIEW</span>
            <h1 className="app-title">AI Resume Analyzer</h1>
          </div>
        </div>

        <div className="score-header-metrics">
          <div className="overall-score-block">
            <span className="metric-label">OVERALL SCORE</span>
            <div className="overall-score-value">
              <span className="big-num">{scores.overall}</span>
              <span className="scale-denominator">/100</span>
            </div>
          </div>

          <div className="categories-list">
            {categories.map((cat) => {
              const isActive = activeCategory === cat.key;
              return (
                <button
                  key={cat.key}
                  className={`category-pill ${isActive ? 'active' : ''}`}
                  onClick={() => onSelectCategory && onSelectCategory(isActive ? null : cat.key)}
                >
                  <span className="cat-label">{cat.label}</span>
                  <span className="cat-value">{cat.val}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </header>
  );
}
