import React, { useState } from 'react';
import { UploadPage } from '@/pages/UploadPage';
import { DashboardPage } from '@/pages/DashboardPage';
import './App.css';

function App() {
  const [documentId, setDocumentId] = useState<string | null>(null);

  return (
    <div className="app">
      {!documentId ? (
        <UploadPage onDocumentUploaded={setDocumentId} />
      ) : (
        <DashboardPage documentId={documentId} onBack={() => setDocumentId(null)} />
      )}
    </div>
  );
}

export default App;
