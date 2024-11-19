import React, { useState } from 'react';

function FileUpload() {
  const [selectedFilesFolder1, setSelectedFilesFolder1] = useState([]);
  const [selectedFilesFolder2, setSelectedFilesFolder2] = useState([]);
  const [uploadStatus, setUploadStatus] = useState('');
  const [similarityResult, setSimilarityResult] = useState('');
  const [isUploadSuccessful, setIsUploadSuccessful] = useState(false);
  const [isSimilaritySuccessful, setIsSimilaritySuccessful] = useState(false);

  const handleFileChangeFolder1 = (e) => {
    setSelectedFilesFolder1(e.target.files);
  };

  const handleFileChangeFolder2 = (e) => {
    setSelectedFilesFolder2(e.target.files);
  };

  const handleFileUpload = async (folder, files) => {
    setUploadStatus('');
    setIsUploadSuccessful(false);
  
    if (files.length === 0) {
      setUploadStatus('No files selected');
      return;
    }
  
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
  
    try {
      const response = await fetch(`http://localhost:5000/upload/${folder}`, {
        method: 'POST',
        body: formData,
      });
  
      if (response.ok) {
        const data = await response.json();
        setUploadStatus('Files uploaded successfully: ' + data.file_paths.join(', '));
        setIsUploadSuccessful(true);
      } else {
        const errorData = await response.json();
        setUploadStatus('Failed to upload files: ' + (errorData.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error uploading files:', error);
      setUploadStatus('An error occurred while uploading the files');
    }
  };
  
  const computeSimilarity = async () => {
    setSimilarityResult('');
    setIsSimilaritySuccessful(false);
  
    try {
      const response = await fetch('http://localhost:5000/compute_similarity', {
        method: 'POST',
      });
  
      if (response.ok) {
        const data = await response.json();
        setSimilarityResult('Similarity Score: ' + data.similarity_score);
        setIsSimilaritySuccessful(true);
      } else {
        const errorData = await response.json();
        setSimilarityResult('Failed to compute similarity: ' + (errorData.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error computing similarity:', error);
      setSimilarityResult('An error occurred while computing similarity');
    }
  };

  const clearUploads = async () => {
    setUploadStatus('');
    setIsUploadSuccessful(false);

    try {
      const response = await fetch('http://localhost:5000/clear_uploads', {
        method: 'POST',
      });

      if (response.ok) {
        setUploadStatus('Upload folders cleared successfully');
        setIsUploadSuccessful(true);
      } else {
        const errorData = await response.json();
        setUploadStatus('Failed to clear uploads: ' + (errorData.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error clearing uploads:', error);
      setUploadStatus('An error occurred while clearing the upload folders');
    }
  };
  
  return (
    <div style={{ padding: '20px' }}>
      <div style={{ marginBottom: '20px' }}>
        <h3>Research Profile</h3>
        <input type="file" multiple onChange={handleFileChangeFolder1} />
        <button onClick={() => handleFileUpload('folder1', selectedFilesFolder1)}>Upload to Folder 1</button>
      </div>
      <div style={{ marginBottom: '20px' }}>
        <h3>Grant Profile</h3>
        <input type="file" multiple onChange={handleFileChangeFolder2} />
        <button onClick={() => handleFileUpload('folder2', selectedFilesFolder2)}>Upload to Folder 2</button>
      </div>
      <div style={{ marginBottom: '20px' }}>
        <button onClick={computeSimilarity}>Compute Similarity</button>
      </div>
      <div style={{ marginBottom: '20px' }}>
        <button onClick={clearUploads}>Clear Uploads</button>
      </div>
      {uploadStatus && (
        <p style={{ color: isUploadSuccessful ? 'green' : 'red' }}>{uploadStatus}</p>
      )}
      {similarityResult && (
        <p style={{ color: isSimilaritySuccessful ? 'green' : 'red' }}>{similarityResult}</p>
      )}
    </div>
  );
}

export default FileUpload;
