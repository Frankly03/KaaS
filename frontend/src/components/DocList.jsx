    // import React, { useState, useEffect } from 'react';
    // import { listDocuments } from '../api';

    // function DocList() {
    //     const [docs, setDocs] = useState([]);
    //     const [loading, setLoading] = useState(true);
    //     const [error, setError] = useState('');

    //     const fetchDocs = async () => {
    //         setLoading(true);
    //         setError('');
    //         try {
    //             const response = await listDocuments();
    //             setDocs(response.data);
    //         } catch (error) {
    //             console.error("Failed to fetch documents:", error);
    //             setError("Could not load document list.");
    //         } finally {
    //             setLoading(false);
    //         }
    //     };

    //     useEffect(() => {
    //         fetchDocs();
    //     }, []);

    //     // This component doesn't automatically refresh when you upload.
    //     // A full-featured app would use state management or a refresh button.
    //     // For now, you can refresh the page to see new uploads.

    //     return (
    //         <div className="doc-list">
    //             <h4>Uploaded Documents <button onClick={fetchDocs} title="Refresh list">🔄</button></h4>
    //             {loading && <p>Loading documents...</p>}
    //             {error && <p style={{color: 'red'}}>{error}</p>}
    //             {!loading && !error && docs.length === 0 && (
    //                 <p>No documents found. Upload one to begin.</p>
    //             )}
    //             <ul>
    //                 {docs.map(doc => (
    //                     <li key={doc.id}>{doc.filename}</li>
    //                 ))}
    //             </ul>
    //         </div>
    //     );
    // }

    // export default DocList;



import React from 'react';

function DocList({ docs, loading, error, onRefresh }) {
    // This component now receives everything it needs as props.
    // It is a "presentational" component.

    return (
        <div className="doc-list">
            <h4>Uploaded Documents <button onClick={onRefresh} title="Refresh list">🔄</button></h4>
            {loading && <p>Loading documents...</p>}
            {error && <p style={{color: 'red'}}>{error}</p>}
            {!loading && !error && docs.length === 0 && (
                <p>No documents found. Upload one to begin.</p>
            )}
            <ul>
                {docs.map(doc => (
                    <li key={doc.id}>{doc.filename}</li>
                ))}
            </ul>
        </div>
    );
}

export default DocList;

