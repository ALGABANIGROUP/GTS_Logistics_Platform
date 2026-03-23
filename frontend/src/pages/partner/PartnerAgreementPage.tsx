import React, { useEffect, useRef, useState } from "react";
import { getPartnerAgreementCurrent, signPartnerAgreement } from "../../services/partnerApi";
import {
    PartnerAgreementCurrentResponse,
    PartnerAgreementSignRequest,
} from "../../types/partner";

const PartnerAgreementPage: React.FC = () => {
    const [agreement, setAgreement] = useState<PartnerAgreementCurrentResponse | null>(
        null
    );
    const [loading, setLoading] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const [checkboxRevenue, setCheckboxRevenue] = useState(false);
    const [checkboxConfidentiality, setCheckboxConfidentiality] = useState(false);
    const [checkboxMisuse, setCheckboxMisuse] = useState(false);
    const [fullName, setFullName] = useState("");
    const [signature, setSignature] = useState("");

    const [hasScrolledToBottom, setHasScrolledToBottom] = useState(false);
    const agreementRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        const fetchAgreement = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await getPartnerAgreementCurrent();
                setAgreement(data);
            } catch (err: any) {
                setError(
                    err?.response?.data?.detail ||
                    err?.message ||
                    "Failed to load partner agreement."
                );
            } finally {
                setLoading(false);
            }
        };

        fetchAgreement();
    }, []);

    const handleScroll = () => {
        const element = agreementRef.current;
        if (!element) return;
        const { scrollTop, scrollHeight, clientHeight } = element;
        if (scrollTop + clientHeight >= scrollHeight - 10) {
            setHasScrolledToBottom(true);
        }
    };

    const canSubmit =
        !!agreement &&
        checkboxRevenue &&
        checkboxConfidentiality &&
        checkboxMisuse &&
        fullName.trim().length > 0 &&
        signature.trim().length > 0 &&
        hasScrolledToBottom;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!agreement) return;

        if (!canSubmit) {
            setError("Please complete all required fields and read the full agreement.");
            return;
        }

        const payload: PartnerAgreementSignRequest = {
            agreementVersion: agreement.agreementVersion,
            signatureName: signature.trim(),
            checkboxRevenue,
            checkboxConfidentiality,
            checkboxMisuse,
        };

        try {
            setSubmitting(true);
            setError(null);
            setSuccess(null);
            await signPartnerAgreement(payload);
            setSuccess("Agreement signed successfully. Your partner account is now active.");
        } catch (err: any) {
            setError(
                err?.response?.data?.detail ||
                err?.message ||
                "Failed to sign the partner agreement."
            );
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="glass-page min-h-screen flex items-center justify-center py-8 px-4">
            <div className="glass-panel w-full max-w-3xl rounded-xl p-6 space-y-6">
                <h1 className="text-2xl font-semibold text-white">
                    GTS Electronic Partner Agreement
                </h1>

                {loading && <p className="text-sm text-white">Loading agreement...</p>}

                {error && (
                    <div className="rounded-md border border-red-200 bg-red-50/20 px-3 py-2 text-sm text-white">
                        {error}
                    </div>
                )}

                {success && (
                    <div className="rounded-md border border-emerald-200 bg-emerald-50/20 px-3 py-2 text-sm text-white">
                        {success}
                    </div>
                )}

                {agreement && (
                    <>
                        <div className="text-xs text-white">
                            Version: {agreement.agreementVersion}
                        </div>

                        <div
                            ref={agreementRef}
                            onScroll={handleScroll}
                            className="glass-panel border rounded-md p-3 h-72 overflow-y-auto text-sm whitespace-pre-wrap text-white"
                        >
                            {agreement.agreementBody}
                        </div>

                        {!hasScrolledToBottom && (
                            <p className="text-xs text-white">
                                Please scroll to the bottom of the agreement before signing.
                            </p>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="space-y-2">
                                <label className="block text-sm font-medium text-white">
                                    Full Name
                                </label>
                                <input
                                    type="text"
                                    className="w-full rounded-md border border-white/20 bg-white/10 px-3 py-2 text-sm text-white placeholder:text-white/60 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                                    value={fullName}
                                    onChange={(e) => {
                                        setFullName(e.target.value);
                                        if (!signature) {
                                            setSignature(e.target.value);
                                        }
                                    }}
                                    placeholder="Enter your full legal name"
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="block text-sm font-medium text-white">
                                    Signature
                                </label>
                                <input
                                    type="text"
                                    className="w-full rounded-md border border-white/20 bg-white/10 px-3 py-2 text-sm text-white placeholder:text-white/60 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                                    value={signature}
                                    onChange={(e) => setSignature(e.target.value)}
                                    placeholder="Type your name as signature"
                                />
                            </div>

                            <div className="space-y-2 text-sm text-white">
                                <label className="flex items-start gap-2">
                                    <input
                                        type="checkbox"
                                        className="mt-1 accent-sky-400"
                                        checked={checkboxRevenue}
                                        onChange={(e) => setCheckboxRevenue(e.target.checked)}
                                    />
                                    <span>
                                        I agree to the revenue model as described in this agreement.
                                    </span>
                                </label>

                                <label className="flex items-start gap-2">
                                    <input
                                        type="checkbox"
                                        className="mt-1 accent-sky-400"
                                        checked={checkboxConfidentiality}
                                        onChange={(e) => setCheckboxConfidentiality(e.target.checked)}
                                    />
                                    <span>
                                        I agree to the confidentiality rules and data protection obligations.
                                    </span>
                                </label>

                                <label className="flex items-start gap-2">
                                    <input
                                        type="checkbox"
                                        className="mt-1 accent-sky-400"
                                        checked={checkboxMisuse}
                                        onChange={(e) => setCheckboxMisuse(e.target.checked)}
                                    />
                                    <span>
                                        I confirm that I will not misuse the platform or attempt to bypass its
                                        controls.
                                    </span>
                                </label>
                            </div>

                            <button
                                type="submit"
                                disabled={!canSubmit || submitting}
                                className={`inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium text-white ${canSubmit && !submitting
                                    ? "bg-sky-600 hover:bg-sky-700"
                                    : "bg-slate-400 cursor-not-allowed"
                                    }`}
                            >
                                {submitting ? "Signing..." : "Accept & Activate Account"}
                            </button>
                        </form>
                    </>
                )}
            </div>
        </div>
    );
};

export default PartnerAgreementPage;
