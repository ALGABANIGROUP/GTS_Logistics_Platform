export const LEGACY_TO_UNIFIED_TIER = {
    demo: 'free',
    basic: 'starter',
    pro: 'professional',
    tms_pro: 'growth',
    unified: 'professional',
    enterprise: 'enterprise',
    free: 'free',
    starter: 'starter',
    growth: 'growth',
    professional: 'professional',
};

export const UNIFIED_TIERS = ['free', 'starter', 'growth', 'professional', 'enterprise'];

export const normalizeTier = (tier, fallback = 'free') => {
    const key = String(tier || '').trim().toLowerCase();
    return LEGACY_TO_UNIFIED_TIER[key] || fallback;
};

export const formatTierLabel = (tier) => {
    const normalized = normalizeTier(tier, String(tier || '').trim().toLowerCase());
    if (normalized === 'free') return 'Free';
    if (normalized === 'starter') return 'Starter';
    if (normalized === 'growth') return 'Growth';
    if (normalized === 'professional') return 'Professional';
    if (normalized === 'enterprise') return 'Enterprise';
    if (!normalized) return 'Free';
    return normalized.charAt(0).toUpperCase() + normalized.slice(1);
};