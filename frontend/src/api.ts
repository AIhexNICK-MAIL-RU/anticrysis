const BASE = '/api';

export type PeriodTableData = {
  period: { id: number; label: string; period_start?: string; period_end?: string };
  balance: Record<string, number>;
  bdr: Record<string, number>;
  bdds: Record<string, number>;
  coefficients: Record<string, number>;
  crisis: { crisis_type_code: string; crisis_type_name: string; confidence: number; reasoning: string };
  fin_model?: Record<string, number>;
};

function getToken(): string | null {
  return localStorage.getItem('token');
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(options.headers as object),
  };
  if (token) (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  if (res.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    const msg = err?.detail;
    const str =
      typeof msg === 'string'
        ? msg
        : Array.isArray(msg)
          ? msg.map((e: { msg?: string }) => e?.msg || JSON.stringify(e)).join(', ')
          : msg != null
            ? JSON.stringify(msg)
            : res.statusText || 'Ошибка запроса';
    throw new Error(str);
  }
  const result = res.headers.get('content-type')?.includes('json') ? await res.json() : await res.text();
  return result as T;
}

export const auth = {
  login: (email: string, password: string) =>
    api<{ access_token: string }>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  register: (email: string, password: string, full_name: string) =>
    api<{ id: number; email: string; full_name: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name }),
    }),
  me: () => api<{ id: number; email: string; full_name: string }>('/auth/me'),
};

export const orgs = {
  list: () => api<{ id: number; name: string }[]>('/orgs'),
  create: (name: string) => api<{ id: number; name: string }>('/orgs', { method: 'POST', body: JSON.stringify({ name }) }),
  get: (id: number) => api<{ id: number; name: string }>(`/orgs/${id}`),
};

export const anticrisis = {
  periods: (orgId: number) =>
    api<{ id: number; organization_id: number; period_type: string; period_start: string; period_end: string; label: string }[]>(
      `/orgs/${orgId}/anticrisis/periods`
    ),
  createPeriod: (orgId: number, data: { period_type: string; period_start: string; period_end: string; label?: string }) =>
    api<{ id: number; label: string }>(`/orgs/${orgId}/anticrisis/periods`, { method: 'POST', body: JSON.stringify(data) }),
  updateBalance: (orgId: number, periodId: number, data: Record<string, number>) =>
    api(`/orgs/${orgId}/anticrisis/periods/${periodId}/balance`, { method: 'PUT', body: JSON.stringify(data) }),
  updateBDR: (orgId: number, periodId: number, data: Record<string, number>) =>
    api(`/orgs/${orgId}/anticrisis/periods/${periodId}/bdr`, { method: 'PUT', body: JSON.stringify(data) }),
  updateBDDS: (orgId: number, periodId: number, data: Record<string, number>) =>
    api(`/orgs/${orgId}/anticrisis/periods/${periodId}/bdds`, { method: 'PUT', body: JSON.stringify(data) }),
  coefficients: (orgId: number, periodId: number) =>
    api<Record<string, number>>(`/orgs/${orgId}/anticrisis/periods/${periodId}/coefficients`),
  periodTable: (orgId: number, periodId: number) =>
    api<PeriodTableData>(`/orgs/${orgId}/anticrisis/periods/${periodId}/table`),
  crisis: (orgId: number, periodId: number) =>
    api<{ crisis_type_code: string; crisis_type_name: string; confidence: number; reasoning: string }>(
      `/orgs/${orgId}/anticrisis/periods/${periodId}/crisis`
    ),
  crisisTypes: () =>
    api<{ code: string; name: string }[]>('/crisis-types').catch(() => []),
  plans: (orgId: number) =>
    api<{ id: number; organization_id: number; crisis_type_code: string; title: string; created_at: string; items: { id: number; title: string; stage: string; status: string; completed: boolean }[] }[]>(
      `/orgs/${orgId}/anticrisis/plans`
    ),
  createPlan: (orgId: number, data: { crisis_type_code: string; title: string; items: { title: string; stage: string }[] }) =>
    api<{ id: number; title: string }>(`/orgs/${orgId}/anticrisis/plans`, { method: 'POST', body: JSON.stringify(data) }),
  getPlan: (orgId: number, planId: number) =>
    api<{ id: number; title: string; items: { id: number; title: string; status: string; completed: boolean }[] }>(
      `/orgs/${orgId}/anticrisis/plans/${planId}`
    ),
  updatePlanItem: (orgId: number, planId: number, itemId: number, data: { completed?: boolean; status?: string }) =>
    api(`/orgs/${orgId}/anticrisis/plans/${planId}/items/${itemId}`, { method: 'PATCH', body: JSON.stringify(data) }),
};

export const calc = {
  model: () =>
    api<{ sheets: { name: string; visibility: string; file: string }[]; active_sheet: string; has_model: boolean }>('/calc/model'),
  run: (inputs: Record<string, number>) =>
    api<{ cells: Record<string, number | string | null>; metadata: { sheets: unknown[]; has_model: boolean } }>(
      '/calc/run',
      { method: 'POST', body: JSON.stringify({ inputs }) }
    ),
};
