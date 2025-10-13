import React, { useState } from 'react';
import { uploadFile } from '../api';

function Upload({ onUploadSuccess }) { // Receive the callback function as a prop
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setMessage('');
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage('Please select a file first.');
      return;
    }

    setUploading(true);
    setMessage(`Uploading ${selectedFile.name}...`);

    try {
      const response = await uploadFile(selectedFile);
      setMessage(`✅ Success: ${response.data.filename} is being processed. (ID: ${response.data.upload_id})`);
      
      // Call the success handler passed from the parent App component
      if (onUploadSuccess) {
        onUploadSuccess();
      }

      setSelectedFile(null);
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'An unexpected error occurred.';
      setMessage(`❌ Error: ${errorMsg}`);
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload a PDF or TXT Document</h2>
      <p>The content will be chunked, embedded, and stored for querying.</p>
      <input type="file" onChange={handleFileChange} accept=".pdf,.txt" disabled={uploading} />
      <button onClick={handleUpload} disabled={uploading || !selectedFile}>
        {uploading ? 'Uploading...' : 'Upload'}
      </button>
      {message && <p>{message}</p>}
    </div>
  );
}

export default Upload;
