import React, { useState, useEffect } from 'react';
import Upload from './pages/Upload';
import Chat from './pages/Chat';
import { listDocuments, resetAllData } from './api'; // Import resetAllData

function App() {
  const [activeTab, setActiveTab] = useState('chat');
  
  const [docs, setDocs] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [docError, setDocError] = useState('');

  const fetchDocs = async () => {
      setLoadingDocs(true);
      setDocError('');
      try {
          const response = await listDocuments();
          setDocs(response.data);
      } catch (error) {
          console.error("Failed to fetch documents:", error);
          setDocError("Could not load document list.");
      } finally {
          setLoadingDocs(false);
      }
  };

  useEffect(() => {
      fetchDocs();
  }, []);

  const handleUploadSuccess = () => {
    fetchDocs();
    setActiveTab('chat');
  };

  // New handler for the reset button
  const handleReset = async () => {
    // A simple confirmation before deleting everything
    if (window.confirm("Are you sure you want to delete all uploaded data? This cannot be undone.")) {
      try {
        await resetAllData();
        alert("All data has been successfully reset.");
        fetchDocs(); // Refresh the now-empty list
      } catch (error) {
        alert("Failed to reset data. See console for details.");
        console.error("Reset failed:", error);
      }
    }
  };

  return (
    <div className="container">
      <header>
        <h1>KnowledgeOps as a Service 🧠</h1>
        <nav>
          <button onClick={() => setActiveTab('upload')} className={activeTab === 'upload' ? 'active' : ''}>
            Upload Document
          </button>
          <button onClick={() => setActiveTab('chat')} className={activeTab === 'chat' ? 'active' : ''}>
            Chat
          </button>
        </nav>
        {/* New Reset Button */}
        <div className="reset-container">
            <button onClick={handleReset} className="reset-button">
                Reset All Data
            </button>
        </div>
      </header>
      <main>
        {activeTab === 'upload' && <Upload onUploadSuccess={handleUploadSuccess} />}
        {activeTab === 'chat' && (
          <Chat 
            docs={docs} 
            loadingDocs={loadingDocs} 
            docError={docError} 
            onRefreshDocs={fetchDocs} 
          />
        )}
      </main>
    </div>
  );
}

export default App;

