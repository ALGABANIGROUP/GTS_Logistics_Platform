import axiosClient from "./http";
import type {
  Partner,
  PartnerClient,
  PartnerPayout,
  PartnerRevenueRow,
  PartnerStatus,
} from "../types/partner";

type AnyRecord = Record<string, any>;

export interface PartnerListFilters {
  status?: PartnerStatus;
  search?: string;
  page?: number;
  pageSize?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface PartnerDashboardSummary {
  partnerId: string;
  totalClients: number;
  totalOrders: number;
  totalRevenue: number;
  totalPendingPayout: number;
  lastMonthRevenue: number;
  lastPayoutDate?: string | null;
}

export interface PartnerAgreementCurrent {
  version: string;
  body: string;
  hash: string;
}

export interface PartnerAgreementSignPayload {
  agreementVersion: string;
  signatureName: string;
  checkboxRevenue: boolean;
  checkboxConfidentiality: boolean;
  checkboxMisuse: boolean;
}

const toPartner = (row: AnyRecord): Partner => ({
  id: row.id,
  code: row.code,
  name: row.name,
  partnerType: row.partner_type,
  email: row.email,
  phone: row.phone || undefined,
  addressText: row.address_text || undefined,
  defaultB2BShare: Number(row.default_b2b_share ?? 0),
  defaultB2CShare: Number(row.default_b2c_share ?? 0),
  defaultMarketplaceShare: Number(row.default_marketplace_share ?? 0),
  revenueTotal: Number(row.revenue_total ?? 0),
  revenuePending: Number(row.revenue_pending ?? 0),
  revenuePaid: Number(row.revenue_paid ?? 0),
  status: row.status,
  joinedAt: row.joined_at,
  lastLoginAt: row.last_login_at || undefined,
  bankAccountName: row.bank_account_name || undefined,
  bankAccountIban: row.bank_account_iban || undefined,
  bankAccountSwift: row.bank_account_swift || undefined,
} as Partner & AnyRecord);

const toPartnerClient = (row: AnyRecord): PartnerClient => ({
  id: row.id,
  clientId: row.client_id,
  name: row.name || undefined,
  email: row.email || undefined,
  isActive: Boolean(row.is_active),
  relationshipStartedAt: row.relationship_started_at,
  relationshipChannel: row.relationship_channel,
  totalOrders: Number(row.total_orders ?? 0),
  totalRevenue: Number(row.total_revenue ?? 0),
});

const toPartnerRevenueRow = (row: AnyRecord): PartnerRevenueRow => ({
  id: row.id,
  orderId: row.order_id,
  clientId: row.client_id || undefined,
  serviceType: row.service_type,
  currencyCode: row.currency_code,
  grossAmount: Number(row.gross_amount ?? 0),
  netProfitAmount: Number(row.net_profit_amount ?? 0),
  partnerSharePercent: Number(row.partner_share_percent ?? 0),
  partnerAmount: Number(row.partner_amount ?? 0),
  gtsAmount: Number(row.gts_amount ?? 0),
  status: row.status,
  periodYear: Number(row.period_year ?? 0),
  periodMonth: Number(row.period_month ?? 0),
  createdAt: row.created_at,
});

const toPartnerPayout = (row: AnyRecord): PartnerPayout => ({
  id: row.id,
  currencyCode: row.currency_code,
  totalAmount: Number(row.total_amount ?? 0),
  feesAmount: Number(row.fees_amount ?? 0),
  netAmount: Number(row.net_amount ?? 0),
  periodStartDate: row.period_start_date,
  periodEndDate: row.period_end_date,
  status: row.status,
  requestedAt: row.requested_at,
  approvedAt: row.approved_at || undefined,
  paidAt: row.paid_at || undefined,
  paymentReference: row.payment_reference || undefined,
});

const toPaginated = <T>(
  payload: AnyRecord,
  mapper: (row: AnyRecord) => T,
  requestedPage: number,
  requestedPageSize: number
): PaginatedResponse<T> => {
  const items = Array.isArray(payload?.items) ? payload.items.map(mapper) : [];
  return {
    items,
    total: Number(payload?.total ?? items.length),
    page: requestedPage,
    pageSize: requestedPageSize,
  };
};

export async function listPartners(
  filters: PartnerListFilters = {}
): Promise<PaginatedResponse<Partner>> {
  const page = filters.page ?? 1;
  const pageSize = filters.pageSize ?? 20;
  const params: Record<string, any> = { page, page_size: pageSize };
  if (filters.status) params.status = filters.status;
  if (filters.search) params.search = filters.search;
  const res = await axiosClient.get("/api/v1/partners", { params });
  return toPaginated(res.data, toPartner, page, pageSize);
}

export async function getPartnerById(id: string): Promise<Partner> {
  const res = await axiosClient.get(`/api/v1/partners/${id}`);
  return toPartner(res.data);
}

export async function updatePartnerStatus(
  id: string,
  status: PartnerStatus
): Promise<Partner> {
  const res = await axiosClient.patch(`/api/v1/partners/${id}/status`, { status });
  return toPartner(res.data);
}

export async function getPartnerRevenueSummaryAdmin(partnerId: string): Promise<{
  totalRevenue: number;
  pendingRevenue: number;
  paidRevenue: number;
  byServiceType: Record<string, number>;
}> {
  const res = await axiosClient.get(`/api/v1/partners/${partnerId}/revenue/summary`);
  const items = Array.isArray(res.data?.items) ? res.data.items : [];
  const byServiceType = items.reduce((acc: Record<string, number>, item: AnyRecord) => {
    acc[item.service_type] = Number(item.total_partner_amount ?? 0);
    return acc;
  }, {});
  return {
    totalRevenue: Number(res.data?.total_partner_amount ?? 0),
    pendingRevenue: 0,
    paidRevenue: 0,
    byServiceType,
  };
}

export async function getPartnerPayoutsAdmin(partnerId: string): Promise<PartnerPayout[]> {
  const res = await axiosClient.get(`/api/v1/partners/${partnerId}/payouts`);
  return Array.isArray(res.data?.items) ? res.data.items.map(toPartnerPayout) : [];
}

export async function getPartnerProfile(): Promise<Partner> {
  const res = await axiosClient.get("/api/v1/partner/me");
  return toPartner(res.data);
}

export async function getPartnerDashboard(): Promise<PartnerDashboardSummary> {
  const res = await axiosClient.get("/api/v1/partner/me/dashboard");
  return {
    partnerId: res.data.partner_id,
    totalClients: Number(res.data.total_clients ?? 0),
    totalOrders: Number(res.data.total_orders ?? 0),
    totalRevenue: Number(res.data.total_revenue ?? 0),
    totalPendingPayout: Number(res.data.total_pending_payout ?? 0),
    lastMonthRevenue: Number(res.data.last_month_revenue ?? 0),
    lastPayoutDate: res.data.last_payout_date || null,
  };
}

export async function getPartnerClients(
  page = 1,
  pageSize = 20
): Promise<PaginatedResponse<PartnerClient>> {
  const res = await axiosClient.get("/api/v1/partner/me/clients", {
    params: { page, page_size: pageSize },
  });
  return toPaginated(res.data, toPartnerClient, page, pageSize);
}

export async function getPartnerOrders(
  params: { page?: number; pageSize?: number; status?: string } = {}
): Promise<PaginatedResponse<PartnerRevenueRow>> {
  const page = params.page ?? 1;
  const pageSize = params.pageSize ?? 20;
  const query: Record<string, any> = { page, page_size: pageSize };
  if (params.status) query.status = params.status;
  const res = await axiosClient.get("/api/v1/partner/me/orders", { params: query });
  return toPaginated(res.data, toPartnerRevenueRow, page, pageSize);
}

export async function getPartnerRevenue(
  page = 1,
  pageSize = 50
): Promise<PaginatedResponse<PartnerRevenueRow>> {
  const res = await axiosClient.get("/api/v1/partner/me/revenue", {
    params: { page, page_size: pageSize },
  });
  return toPaginated(res.data, toPartnerRevenueRow, page, pageSize);
}

export async function getPartnerPayouts(): Promise<PartnerPayout[]> {
  const res = await axiosClient.get("/api/v1/partner/me/payouts");
  return Array.isArray(res.data?.items) ? res.data.items.map(toPartnerPayout) : [];
}

export async function createPartnerPayoutRequest(payload: {
  periodStartDate: string;
  periodEndDate: string;
}): Promise<PartnerPayout> {
  const res = await axiosClient.post("/api/v1/partner/me/payouts", {
    period_start_date: payload.periodStartDate,
    period_end_date: payload.periodEndDate,
  });
  return toPartnerPayout(res.data);
}

export async function getPartnerAgreementCurrent(): Promise<PartnerAgreementCurrent> {
  const res = await axiosClient.get("/api/v1/partner/agreement/current");
  return {
    version: res.data.agreement_version,
    body: res.data.agreement_body,
    hash: res.data.agreement_text_hash,
  };
}

export async function signPartnerAgreement(
  payload: PartnerAgreementSignPayload
): Promise<{ ok: boolean; activated: boolean }> {
  const res = await axiosClient.post("/api/v1/partner/agreement/sign", {
    agreement_version: payload.agreementVersion,
    signature_name: payload.signatureName,
    checkbox_revenue: payload.checkboxRevenue,
    checkbox_confidentiality: payload.checkboxConfidentiality,
    checkbox_misuse: payload.checkboxMisuse,
  });
  return {
    ok: true,
    activated: Boolean(res.data?.partner_id),
  };
}
