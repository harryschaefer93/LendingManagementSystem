import { useDocuments } from '../../hooks/useDocuments';
import { getDownloadUrl } from '../../api/documents';
import LoadingSpinner from '../common/LoadingSpinner';
import { format } from 'date-fns';

interface Props {
  loanId: string;
}

const docTypeLabels: Record<string, string> = {
  id: 'ID Document',
  income_proof: 'Income Proof',
  property: 'Property Document',
};

export default function DocumentList({ loanId }: Props) {
  const { data: documents, isLoading, error } = useDocuments(loanId);

  const handleDownload = async (documentId: string) => {
    try {
      const { download_url } = await getDownloadUrl(loanId, documentId);
      window.open(download_url, '_blank');
    } catch {
      alert('Failed to generate download link. Azure Blob Storage may not be configured.');
    }
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <div className="error-box">Failed to load documents.</div>;

  if (!documents || documents.length === 0) {
    return (
      <div className="card">
        <div className="card-body" style={{ textAlign: 'center', color: 'var(--color-text-secondary)', padding: 32 }}>
          No documents uploaded yet.
        </div>
      </div>
    );
  }

  const formatSize = (bytes: number | null) => {
    if (!bytes) return '-';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="card">
      <table className="data-table">
        <thead>
          <tr>
            <th>Filename</th>
            <th>Type</th>
            <th>Size</th>
            <th>Uploaded By</th>
            <th>Date</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.id} style={{ cursor: 'default' }}>
              <td style={{ fontWeight: 500 }}>{doc.filename}</td>
              <td>{docTypeLabels[doc.document_type] ?? doc.document_type}</td>
              <td>{formatSize(doc.file_size)}</td>
              <td>{doc.uploaded_by_name ?? '-'}</td>
              <td>{format(new Date(doc.uploaded_at), 'MMM d, yyyy h:mm a')}</td>
              <td>
                <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '0.8rem' }} onClick={() => handleDownload(doc.id)}>
                  Download
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
