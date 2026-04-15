import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchLoans, fetchLoan, createLoan, updateLoan, submitLoan, startReview, decideLoan } from '../api/loans';
import type { LoanCreate, LoanUpdate, DecisionCreate } from '../types';

export function useLoans(params?: { status?: string; skip?: number; limit?: number }) {
  return useQuery({
    queryKey: ['loans', params],
    queryFn: () => fetchLoans(params),
  });
}

export function useLoan(id: string) {
  return useQuery({
    queryKey: ['loan', id],
    queryFn: () => fetchLoan(id),
    enabled: !!id,
  });
}

export function useCreateLoan() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: LoanCreate) => createLoan(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['loans'] }),
  });
}

export function useUpdateLoan(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: LoanUpdate) => updateLoan(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['loans'] });
      qc.invalidateQueries({ queryKey: ['loan', id] });
    },
  });
}

export function useSubmitLoan() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => submitLoan(id),
    onSuccess: (_data, id) => {
      qc.invalidateQueries({ queryKey: ['loans'] });
      qc.invalidateQueries({ queryKey: ['loan', id] });
    },
  });
}

export function useStartReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => startReview(id),
    onSuccess: (_data, id) => {
      qc.invalidateQueries({ queryKey: ['loans'] });
      qc.invalidateQueries({ queryKey: ['loan', id] });
    },
  });
}

export function useDecideLoan(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: DecisionCreate) => decideLoan(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['loans'] });
      qc.invalidateQueries({ queryKey: ['loan', id] });
    },
  });
}
