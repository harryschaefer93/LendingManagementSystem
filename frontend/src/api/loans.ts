import apiClient from './client';
import type {
  Loan,
  LoanCreate,
  LoanDetail,
  LoanListResponse,
  LoanUpdate,
  DecisionCreate,
  AuditEntryFull,
} from '../types';

export async function fetchLoans(params?: {
  status?: string;
  loan_officer_id?: string;
  skip?: number;
  limit?: number;
}): Promise<LoanListResponse> {
  const { data } = await apiClient.get<LoanListResponse>('/api/loans', { params });
  return data;
}

export async function fetchLoan(id: string): Promise<LoanDetail> {
  const { data } = await apiClient.get<LoanDetail>(`/api/loans/${id}`);
  return data;
}

export async function createLoan(body: LoanCreate): Promise<Loan> {
  const { data } = await apiClient.post<Loan>('/api/loans', body);
  return data;
}

export async function updateLoan(id: string, body: LoanUpdate): Promise<Loan> {
  const { data } = await apiClient.patch<Loan>(`/api/loans/${id}`, body);
  return data;
}

export async function submitLoan(id: string): Promise<Loan> {
  const { data } = await apiClient.post<Loan>(`/api/loans/${id}/submit`);
  return data;
}

export async function startReview(id: string): Promise<Loan> {
  const { data } = await apiClient.post<Loan>(`/api/loans/${id}/review`);
  return data;
}

export async function decideLoan(id: string, body: DecisionCreate): Promise<Loan> {
  const { data } = await apiClient.post<Loan>(`/api/loans/${id}/decide`, body);
  return data;
}

export async function fetchAuditTrail(loanId: string): Promise<AuditEntryFull[]> {
  const { data } = await apiClient.get<AuditEntryFull[]>(`/api/loans/${loanId}/audit`);
  return data;
}
