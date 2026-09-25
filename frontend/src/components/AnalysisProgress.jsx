import React, { useState, useEffect } from 'react';
import { Check, Circle, Loader2 } from 'lucide-react';

export default function AnalysisProgress() {
  const steps = [
    { id: 1, label: 'Parsing document structure & typography' },
    { id: 2, label: 'Evaluating general clarity, action verbs & syntax' },
    { id: 3, label: 'Running ATS parse & readability check' },
    { id: 4, label: 'Comparing qualifications & skill gaps against Job Description' },
  ];

  const [currentStep, setCurrentStep] = useState(1);

  useEffect(() => {
    const timer1 = setTimeout(() => setCurrentStep(2), 600);
    const timer2 = setTimeout(() => setCurrentStep(3), 1300);
    const timer3 = setTimeout(() => setCurrentStep(4), 2100);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, []);

  return (
    <div className="progress-screen">
      <div className="progress-card">
        <div className="progress-header">
          <span className="progress-kicker">ANALYSIS IN PROGRESS</span>
          <h2 className="progress-title">Reviewing Manuscript</h2>
          <p className="progress-sub">Checking layout, phrasing, quantified metrics, and ATS compatibility.</p>
        </div>

        <ul className="progress-steps-list">
          {steps.map((s) => {
            const isCompleted = currentStep > s.id;
            const isCurrent = currentStep === s.id;

            return (
              <li key={s.id} className={`step-item ${isCompleted ? 'done' : isCurrent ? 'current' : 'pending'}`}>
                <span className="step-icon-wrap">
                  {isCompleted ? (
                    <Check size={16} className="step-check" />
                  ) : isCurrent ? (
                    <Loader2 size={16} className="step-spin animate-spin" />
                  ) : (
                    <Circle size={14} className="step-circle" />
                  )}
                </span>
                <span className="step-label">{s.label}</span>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
