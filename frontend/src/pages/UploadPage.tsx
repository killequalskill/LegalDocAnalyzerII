import React, { useState } from 'react';
import { documentApi } from '@/services/api';
import './UploadPage.css';

interface UploadPageProps {
  onDocumentUploaded: (docId: string) => void;
}

export const UploadPage: React.FC<UploadPageProps> = ({ onDocumentUploaded }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      setFile(files[0]);
      setError(null);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const result = await documentApi.upload(file);
      onDocumentUploaded(result.document_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="upload-container">
        <h1>Upload Legal Document</h1>
        <p>Upload a PDF contract or agreement for analysis</p>

        <div
          className="upload-zone"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          {file ? (
            <div className="file-selected">
              <p>📄 {file.name}</p>
              <p className="file-size">({(file.size / 1024).toFixed(2)} KB)</p>
            </div>
          ) : (
            <>
              <p>Drag and drop your PDF here</p>
              <p className="divider">or</p>
              <label htmlFor="file-input" className="file-label">
                Click to browse
              </label>
              <input
                id="file-input"
                type="file"
                accept=".pdf"
                onChange={handleFileSelect}
                className="hidden-input"
              />
            </>
          )}
        </div>

        {error && <div className="error-message">{error}</div>}

        <button
          className="upload-button"
          onClick={handleUpload}
          disabled={!file || uploading}
        >
          {uploading ? 'Uploading...' : 'Upload Document'}
        </button>
      </div>
    </div>
  );
};
