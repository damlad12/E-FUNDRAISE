// App.js

import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import UploadForm from './components/UploadForm';
import ProgressBar from './components/ProgressBar';
import ResultsList from './components/ResultsList';
import './App.css';

function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [progressMessages, setProgressMessages] = useState([]);
  const steps = [
    'Extracting text from your file...',
    'Summarizing text...',
    'Generating embeddings...',
    'Calculating similarity scores...',
    'Identifying top matches...',
    'Processing complete.'
  ];
  const [results, setResults] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    const socket = io('http://localhost:5000');

    socket.on('progress', (data) => {
      setProgressMessages((prevMessages) => [...prevMessages, data.message]);

      // Update currentStep based on predefined steps
      const index = steps.findIndex((step) => data.message.includes(step));
      if (index !== -1) {
        setCurrentStep(index);
      }
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const handleUpload = async (filesFolder1, filesFolder2, textInput) => {
    setIsAnalyzing(true);
    setCurrentStep(0);
    setResults([]);
    setProgressMessages([]);

    // Clear previous uploads
    await clearUploads();

    if (textInput) {
      await uploadTextInput(textInput);
    } else {
      // Upload files to the backend
      await uploadFiles('folder1', filesFolder1);
    }

    await uploadFiles('folder2', filesFolder2);

    // Trigger similarity computation
    await computeSimilarity();

    setIsAnalyzing(false);
  };

  const clearUploads = async () => {
    try {
      await fetch('http://localhost:5000/clear_uploads', {
        method: 'POST',
      });
    } catch (error) {
      console.error('Error clearing uploads:', error);
    }
  };

  const uploadFiles = async (folder, files) => {
    if (files.length === 0) {
      alert(`No files selected for ${folder}`);
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

      if (!response.ok) {
        const errorData = await response.json();
        alert('Failed to upload files: ' + (errorData.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error uploading files:', error);
      alert('An error occurred while uploading the files');
    }
  };

  const uploadTextInput = async (textInput) => {
    try {
      const formData = new FormData();
      formData.append('textInput', textInput);

      const response = await fetch('http://localhost:5000/upload/text_input', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        alert('Failed to upload text input: ' + (errorData.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error uploading text input:', error);
      alert('An error occurred while uploading the text input');
    }
  };

  const computeSimilarity = async () => {
    try {
      const response = await fetch('http://localhost:5000/compute_similarity', {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();

        // Set the results received from the backend
        setResults(data.results || []);
      } else {
        const errorData = await response.json();
        alert('Failed to compute similarity: ' + (errorData.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error computing similarity:', error);
      alert('An error occurred while computing similarity');
    }
  };

  return (
    <div className="App">
      <UploadForm onUpload={handleUpload} />
      {isAnalyzing && (
        <ProgressBar steps={steps} currentStep={currentStep} />
      )}
      {results.length > 0 && <ResultsList results={results} />}
    </div>
  );
}

export default App;
