export type PartnerStatus = "pending" | "active" | "suspended" | "closed";

export type ServiceType = "b2b" | "b2c" | "marketplace";

export type PayoutStatus =
    | "requested"
    | "under_review"
    | "approved"
    | "paid"
    | "rejected";

export interface Partner {
    id: string;
    code: string;
    name: string;
    partnerType: "individual" | "company" | "agency";
    email: string;
    phone?: string;
    addressText?: string;
    bankAccountName?: string;
    bankAccountIban?: string;
    bankAccountSwift?: string;
    defaultB2BShare: number;
    defaultB2CShare: number;
    defaultMarketplaceShare: number;
    revenueTotal: number;
    revenuePending: number;
    revenuePaid: number;
    status: PartnerStatus;
    joinedAt: string;
    lastLoginAt?: string;
}

export interface PartnerListResponse {
    items: Partner[];
    total: number;
}

export interface PartnerClient {
    id: string;
    clientId: string;
    name?: string;
    email?: string;
    isActive: boolean;
    relationshipStartedAt: string;
    relationshipChannel: string;
    totalOrders: number;
    totalRevenue: number;
}

export interface PartnerClientListResponse {
    items: PartnerClient[];
    total: number;
}

export interface PartnerRevenueRow {
    id: string;
    orderId: string;
    clientId?: string;
    serviceType: ServiceType;
    currencyCode: string;
    grossAmount: number;
    netProfitAmount: number;
    partnerSharePercent: number;
    partnerAmount: number;
    gtsAmount: number;
    status: string;
    periodYear: number;
    periodMonth: number;
    createdAt: string;
}

export interface PartnerRevenueListResponse {
    items: PartnerRevenueRow[];
    total: number;
}

export interface PartnerRevenueSummaryItem {
    serviceType: ServiceType;
    periodYear: number;
    periodMonth: number;
    totalNetProfit: number;
    totalPartnerAmount: number;
    totalGtsAmount: number;
    ordersCount: number;
}

export interface PartnerRevenueSummaryResponse {
    partnerId: string;
    items: PartnerRevenueSummaryItem[];
    totalPartnerAmount: number;
    totalGtsAmount: number;
    totalOrders: number;
}

export interface PartnerPayout {
    id: string;
    currencyCode: string;
    totalAmount: number;
    feesAmount: number;
    netAmount: number;
    periodStartDate: string;
    periodEndDate: string;
    status: PayoutStatus;
    requestedAt: string;
    approvedAt?: string;
    paidAt?: string;
    paymentReference?: string;
}

export interface PartnerPayoutListResponse {
    items: PartnerPayout[];
    total: number;
}

export interface PartnerPayoutCreateRequest {
    periodStartDate: string;
    periodEndDate: string;
    currencyCode?: string;
}

export interface PartnerDashboardSummary {
    partnerId: string;
    totalClients: number;
    totalOrders: number;
    totalRevenue: number;
    totalPendingPayout: number;
    lastMonthRevenue: number;
    lastPayoutDate?: string;
}

export interface PartnerAgreementCurrentResponse {
    agreementVersion: string;
    agreementBody: string;
    agreementTextHash: string;
}

export interface PartnerAgreementSignRequest {
    agreementVersion: string;
    signatureName: string;
    checkboxRevenue: boolean;
    checkboxConfidentiality: boolean;
    checkboxMisuse: boolean;
}

export interface PartnerAgreementSignResponse {
    partnerId: string;
    agreementVersion: string;
    signedAt: string;
    ipAddress?: string;
    signatureName: string;
}
