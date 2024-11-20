import React, { useEffect, useState } from 'react';
import '../styles/ProgressBar.css';

function ProgressBar({ steps, currentStep }) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Reset progress when currentStep changes
    setProgress(0);

    // Animate progress filling
    let progressInterval = setInterval(() => {
      setProgress((oldProgress) => {
        const newProgress = oldProgress + 10;
        if (newProgress >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return newProgress;
      });
    }, 100); // Adjust the speed as needed

    return () => {
      clearInterval(progressInterval);
    };
  }, [currentStep]);

  return (
    <div className="progress-bar-container">
      <div className="progress-bar-step">
        <div className="progress-bar-fill" style={{ width: `${progress}%` }}></div>
        <div className="progress-bar-label">{steps[currentStep]}</div>
      </div>
    </div>
  );
}

export default ProgressBar;
