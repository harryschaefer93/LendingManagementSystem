import { useState, useRef, useCallback } from 'react';
import { useUploadDocument } from '../../hooks/useDocuments';

interface Props {
  loanId: string;
}

export default function DocumentUpload({ loanId }: Props) {
  const uploadMutation = useUploadDocument(loanId);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [documentType, setDocumentType] = useState('id');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState('');

  const handleFile = useCallback((file: File) => {
    const allowed = ['application/pdf', 'image/jpeg', 'image/png'];
    if (!allowed.includes(file.type)) {
      setError('Only PDF, JPEG, and PNG files are allowed.');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be under 10 MB.');
      return;
    }
    setError('');
    setSelectedFile(file);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const handleUpload = async () => {
    if (!selectedFile) return;
    setError('');
    try {
      await uploadMutation.mutateAsync({ file: selectedFile, documentType });
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Upload failed';
      setError(message);
    }
  };

  return (
    <div className="card">
      <div className="card-header">Upload Document</div>
      <div className="card-body">
        {error && <div className="error-box" style={{ marginBottom: 12 }}>{error}</div>}

        <div className="form-group">
          <label>Document Type</label>
          <select className="form-control" value={documentType} onChange={(e) => setDocumentType(e.target.value)}>
            <option value="id">ID Document</option>
            <option value="income_proof">Income Proof</option>
            <option value="property">Property Document</option>
          </select>
        </div>

        <div
          className={`upload-zone${dragOver ? ' dragover' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFile(file);
            }}
          />
          {selectedFile ? (
            <div>
              <strong>{selectedFile.name}</strong>
              <br />
              <span style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
                {(selectedFile.size / 1024).toFixed(1)} KB - {selectedFile.type}
              </span>
            </div>
          ) : (
            <div>
              <p style={{ fontSize: '1rem', marginBottom: 4 }}>
                Drag & drop a file here, or click to browse
              </p>
              <p style={{ fontSize: '0.8rem' }}>PDF, JPEG, or PNG - max 10 MB</p>
            </div>
          )}
        </div>

        {selectedFile && (
          <div style={{ marginTop: 12 }}>
            <button
              className="btn btn-primary"
              disabled={uploadMutation.isPending}
              onClick={handleUpload}
            >
              {uploadMutation.isPending ? 'Uploading…' : 'Upload Document'}
            </button>
            <button
              className="btn btn-secondary"
              style={{ marginLeft: 8 }}
              onClick={() => { setSelectedFile(null); if (fileInputRef.current) fileInputRef.current.value = ''; }}
            >
              Clear
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
