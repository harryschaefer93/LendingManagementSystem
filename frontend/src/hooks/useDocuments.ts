import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchDocuments, uploadDocument } from '../api/documents';

export function useDocuments(loanId: string) {
  return useQuery({
    queryKey: ['documents', loanId],
    queryFn: () => fetchDocuments(loanId),
    enabled: !!loanId,
  });
}

export function useUploadDocument(loanId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ file, documentType }: { file: File; documentType: string }) =>
      uploadDocument(loanId, file, documentType),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['documents', loanId] });
      qc.invalidateQueries({ queryKey: ['loan', loanId] });
    },
  });
}
