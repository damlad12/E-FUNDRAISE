// UploadForm.js

import React, { useState } from 'react';
import '../styles/UploadForm.css';

function UploadForm({ onUpload }) {
  const [selectedFilesFolder1, setSelectedFilesFolder1] = useState([]);
  const [selectedFilesFolder2, setSelectedFilesFolder2] = useState([]);
  const [textInput, setTextInput] = useState('');

  const handleFileChangeFolder1 = (e) => {
    setSelectedFilesFolder1(e.target.files);
  };

  const handleFileChangeFolder2 = (e) => {
    setSelectedFilesFolder2(e.target.files);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onUpload(selectedFilesFolder1, selectedFilesFolder2, textInput);
  };

  return (
    <div className="upload-form">
      <h2>Upload Your Files</h2>
      <form onSubmit={handleSubmit}>
        <div className="file-upload">
          <label>Research Paper:</label>
          <input type="file" multiple onChange={handleFileChangeFolder1} />
        </div>
        <div className="text-input">
          <label>Or Paste Your Research Paper Text:</label>
          <textarea value={textInput} onChange={(e) => setTextInput(e.target.value)} rows="10" />
        </div>
        <div className="file-upload">
          <label>Grant Files:</label>
          <input type="file" multiple onChange={handleFileChangeFolder2} />
        </div>
        <button type="submit" className="upload-button">Analyze</button>
      </form>
    </div>
  );
}

export default UploadForm;
