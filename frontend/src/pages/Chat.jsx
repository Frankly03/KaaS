import React, { useState } from 'react';
import { postQuery } from '../api';
import DocList from '../components/DocList'; // Import DocList

function Chat({ docs, loadingDocs, docError, onRefreshDocs }) { // Receive props from App.jsx
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState(''); // State for the filter dropdown

  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    const userMessage = { sender: 'user', text: query };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setQuery('');

    try {
      // Pass the selected document filename to the API call
      const filename = selectedDoc === 'all' ? null : selectedDoc;
      const response = await postQuery(query, filename);
      const { answer, sources } = response.data;
      const assistantMessage = { sender: 'assistant', text: answer, sources };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to get an answer.';
      const assistantMessage = { sender: 'assistant', text: `Error: ${errorMsg}`, sources: [] };
      setMessages(prev => [...prev, assistantMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      {/* The DocList is now part of the Chat view */}
      <DocList 
        docs={docs} 
        loading={loadingDocs} 
        error={docError} 
        onRefresh={onRefreshDocs} 
      />
      
      {/* NEW: Document Filter Dropdown */}
      <div className="doc-filter">
        <label htmlFor="doc-select">Filter by Document: </label>
        <select 
          id="doc-select" 
          value={selectedDoc} 
          onChange={(e) => setSelectedDoc(e.target.value)}
        >
          <option value="all">All Documents</option>
          {docs.map(doc => (
            <option key={doc.id} value={doc.filename}>{doc.filename}</option>
          ))}
        </select>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && <p>Select a document filter (optional) and ask a question.</p>}
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}-message`}>
            <p>{msg.text}</p>
            {msg.sources && msg.sources.length > 0 && (
              <div className="sources">
                <h4>Sources:</h4>
                {msg.sources.map((source, idx) => (
                  <div key={idx} className="source">
                    <strong>{source.filename} (chunk: {source.chunk_index})</strong>
                    <pre>{source.snippet}</pre>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
         {loading && <div className="message assistant-message"><p>Thinking...</p></div>}
      </div>
      <form onSubmit={handleQuerySubmit} className="chat-input">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !query.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

export default Chat;

