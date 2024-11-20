// ResultsList.js

import React, { useState } from 'react';
import '../styles/ResultsList.css';

function ResultsList({ results }) {
  const [selectedGrants, setSelectedGrants] = useState([]);
  const [selectAll, setSelectAll] = useState(false);

  const handleSelectGrant = (grantId) => {
    setSelectedGrants((prevSelected) =>
      prevSelected.includes(grantId)
        ? prevSelected.filter((id) => id !== grantId)
        : [...prevSelected, grantId]
    );
  };

  const handleSelectAll = () => {
    setSelectAll(!selectAll);
    if (!selectAll) {
      setSelectedGrants(results.map((grant) => grant.id));
    } else {
      setSelectedGrants([]);
    }
  };

  const handleApply = () => {
    // Handle the apply action
    alert('Applied to selected grants!');
  };

  const getScoreClass = (score) => {
    if (score >= 0.8) return 'high-score';
    if (score >= 0.5) return 'medium-score';
    return 'low-score';
  };

  const formatScore = (score) => {
    return (score * 10).toFixed(1) + '/10';
  };

  // Sort results if not already sorted
  const sortedResults = results.sort((a, b) => b.score - a.score);

  return (
    <div className="results-list">
      <h2>Matched Grants</h2>
      <div className="actions">
        <input type="checkbox" checked={selectAll} onChange={handleSelectAll} />
        <label>Select All</label>
        <button onClick={handleApply} className="apply-button">Apply to Selected</button>
      </div>
      <ul>
        {sortedResults.map((grant, index) => (
          <li key={grant.id} className={`grant-item ${getScoreClass(grant.score)}`}>
            <input
              type="checkbox"
              checked={selectedGrants.includes(grant.id)}
              onChange={() => handleSelectGrant(grant.id)}
            />
            <div className="grant-details">
              <h3>
                {grant.title}
                {index === 0 && <span className="badge best-match">Best Match</span>}
                {index === 1 && <span className="badge highly-recommended">Highly Recommended</span>}
              </h3>
              <p>{grant.abstract}</p>
              <p><strong>Funding Amount:</strong> {grant.fundingAmount}</p>
              <p><strong>Deadline:</strong> {grant.deadline}</p>
              <span className="grant-score">Score: {formatScore(grant.score)}</span>
              <p className="grant-reason">Perfect match for AI research</p> {/* Replace with actual reason */}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ResultsList;
