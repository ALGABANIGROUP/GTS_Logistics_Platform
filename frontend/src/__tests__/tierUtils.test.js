import { describe, expect, it } from 'vitest';
import { UNIFIED_TIERS, formatTierLabel, normalizeTier } from '../utils/tierUtils';

describe('tierUtils', () => {
    it('normalizes legacy aliases to unified tiers', () => {
        expect(normalizeTier('demo')).toBe('free');
        expect(normalizeTier('basic')).toBe('starter');
        expect(normalizeTier('pro')).toBe('professional');
        expect(normalizeTier('tms_pro')).toBe('growth');
        expect(normalizeTier('unified')).toBe('professional');
    });

    it('normalizes case and whitespace', () => {
        expect(normalizeTier('  BASIC  ')).toBe('starter');
        expect(normalizeTier(' PROFESSIONAL ')).toBe('professional');
    });

    it('uses fallback for unknown tier values', () => {
        expect(normalizeTier('custom-tier')).toBe('free');
        expect(normalizeTier('custom-tier', 'starter')).toBe('starter');
    });

    it('formats unified tier labels', () => {
        expect(formatTierLabel('free')).toBe('Free');
        expect(formatTierLabel('starter')).toBe('Starter');
        expect(formatTierLabel('growth')).toBe('Growth');
        expect(formatTierLabel('professional')).toBe('Professional');
        expect(formatTierLabel('enterprise')).toBe('Enterprise');
    });

    it('formats legacy aliases using unified labels', () => {
        expect(formatTierLabel('demo')).toBe('Free');
        expect(formatTierLabel('basic')).toBe('Starter');
        expect(formatTierLabel('pro')).toBe('Professional');
        expect(formatTierLabel('tms_pro')).toBe('Growth');
        expect(formatTierLabel('unified')).toBe('Professional');
    });

    it('formats unknown values and empty values safely', () => {
        expect(formatTierLabel('vip-plan')).toBe('Vip-plan');
        expect(formatTierLabel('')).toBe('Free');
        expect(formatTierLabel(null)).toBe('Free');
    });

    it('exposes unified tiers list in expected order', () => {
        expect(UNIFIED_TIERS).toEqual(['free', 'starter', 'growth', 'professional', 'enterprise']);
    });
});