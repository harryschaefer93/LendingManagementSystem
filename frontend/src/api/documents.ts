import apiClient from './client';
import type { DocumentFull } from '../types';

export async function fetchDocuments(loanId: string): Promise<DocumentFull[]> {
  const { data } = await apiClient.get<DocumentFull[]>(`/api/loans/${loanId}/documents`);
  return data;
}

export async function uploadDocument(
  loanId: string,
  file: File,
  documentType: string,
): Promise<void> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('document_type', documentType);
  await apiClient.post(`/api/loans/${loanId}/documents`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
}

export async function getDownloadUrl(
  loanId: string,
  documentId: string,
): Promise<{ download_url: string; filename: string }> {
  const { data } = await apiClient.get<{ download_url: string; filename: string }>(
    `/api/loans/${loanId}/documents/${documentId}/download`,
  );
  return data;
}
