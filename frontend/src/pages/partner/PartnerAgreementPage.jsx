// frontend/src/pages/partner/PartnerAgreementPage.jsx

import React, { useEffect, useState } from "react";
import {
  getPartnerAgreementCurrent,
  signPartnerAgreement,
} from "../../services/partnerApi";
import { useRefreshSubscription } from "../../contexts/UiActionsContext.jsx";

const PartnerAgreementPage = () => {
  const [agreement, setAgreement] = useState(null);
  const [loading, setLoading] = useState(true);
  const [signing, setSigning] = useState(false);
  const [error, setError] = useState(null);

  const [checkboxRevenue, setCheckboxRevenue] = useState(false);
  const [checkboxConfidentiality, setCheckboxConfidentiality] = useState(false);
  const [checkboxMisuse, setCheckboxMisuse] = useState(false);
  const [fullName, setFullName] = useState("");
  const [hasScrolledToEnd, setHasScrolledToEnd] = useState(false);

  const errorLower = (error || "").toString().toLowerCase();
  const tokenIssue =
    errorLower.includes("token") ||
    errorLower.includes("expired") ||
    errorLower.includes("invalid");

  const loadAgreement = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getPartnerAgreementCurrent();
      setAgreement(res);
    } catch (err) {
      const msg =
        err?.response?.data?.detail || err?.message || "Failed to load agreement.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAgreement();
  }, []);

  useRefreshSubscription(() => {
    loadAgreement();
  });

  const handleScroll = (e) => {
    const target = e.target;
    if (target.scrollTop + target.clientHeight >= target.scrollHeight - 10) {
      setHasScrolledToEnd(true);
    }
  };

  const handleSign = async (e) => {
    e.preventDefault();
    if (!agreement) return;

    if (
      !checkboxRevenue ||
      !checkboxConfidentiality ||
      !checkboxMisuse ||
      !fullName.trim()
    ) {
      alert("Please complete all checkboxes and signature name.");
      return;
    }

    try {
      setSigning(true);
      await signPartnerAgreement({
        agreementVersion: agreement.version,
        signatureName: fullName.trim(),
        checkboxRevenue,
        checkboxConfidentiality,
        checkboxMisuse,
      });
      alert("Agreement signed successfully. Your account should now be active.");
    } catch (err) {
      console.error("Failed to sign agreement", err);
      alert(
        err?.response?.data?.detail || err?.message || "Failed to sign agreement."
      );
    } finally {
      setSigning(false);
    }
  };

  const submitDisabled =
    !agreement ||
    !checkboxRevenue ||
    !checkboxConfidentiality ||
    !checkboxMisuse ||
    !fullName.trim() ||
    !hasScrolledToEnd ||
    signing;

  return (
    <div className="glass-page max-w-3xl mx-auto space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-white">
          GTS Electronic Partner Agreement
        </h1>
        <p className="text-sm text-white">
          Please read the agreement carefully, confirm the checkboxes and sign
          electronically to activate your partner account.
        </p>
      </div>

      {error && (
        <div className="glass-panel rounded-md px-4 py-3 text-sm text-white border border-red-200/60 space-y-2">
          <div className="font-medium">
            {tokenIssue
              ? "This agreement link is no longer valid."
              : "We could not load the agreement right now."}
          </div>
          <div className="text-xs text-white/80">{error}</div>
          {tokenIssue && (
            <div className="flex flex-wrap gap-2 pt-1">
              <a
                href="mailto:investments@gabanilogistics.com?subject=Partner%20Agreement%20Link%20Request"
                className="px-3 py-1.5 rounded-md bg-sky-500/80 text-white text-xs hover:bg-sky-500/90"
              >
                Request a new link
              </a>
              <a
                href="mailto:admin@gabanilogistics.com?subject=Partner%20Agreement%20Access"
                className="px-3 py-1.5 rounded-md border border-white/20 text-white text-xs hover:bg-white/10"
              >
                Contact admin
              </a>
            </div>
          )}
        </div>
      )}

      {loading ? (
        <div className="text-sm text-white">Loading agreement...</div>
      ) : !agreement ? (
        <div className="text-sm text-white">
          Agreement content is not available yet. Please try again later.
        </div>
      ) : (
        <>
          <div className="glass-panel rounded-lg border">
            <div className="px-4 py-2 border-b border-white/10 flex items-center justify-between">
              <span className="text-sm font-medium text-white">
                Agreement - Version {agreement.version}
              </span>
              <span className="text-xs text-white">
                Hash: {agreement.hash?.slice(0, 12)}...
              </span>
            </div>
            <div
              className="max-h-80 overflow-y-auto p-4 text-sm text-white whitespace-pre-wrap"
              onScroll={handleScroll}
            >
              {agreement.body}
            </div>
            {!hasScrolledToEnd && (
              <div className="px-4 py-2 text-[11px] text-white border-t border-white/10">
                Scroll to the bottom of the agreement to enable signing.
              </div>
            )}
          </div>

          <form
            onSubmit={handleSign}
            className="glass-panel border rounded-lg p-4 space-y-3 text-sm"
          >
            <div className="space-y-2">
              <label className="flex items-start gap-2 text-sm text-white">
                <input
                  type="checkbox"
                  checked={checkboxRevenue}
                  onChange={(e) => setCheckboxRevenue(e.target.checked)}
                  className="mt-1 accent-sky-400"
                />
                <span>I agree to the revenue model.</span>
              </label>
              <label className="flex items-start gap-2 text-sm text-white">
                <input
                  type="checkbox"
                  checked={checkboxConfidentiality}
                  onChange={(e) => setCheckboxConfidentiality(e.target.checked)}
                  className="mt-1 accent-sky-400"
                />
                <span>I agree to the confidentiality rules.</span>
              </label>
              <label className="flex items-start gap-2 text-sm text-white">
                <input
                  type="checkbox"
                  checked={checkboxMisuse}
                  onChange={(e) => setCheckboxMisuse(e.target.checked)}
                  className="mt-1 accent-sky-400"
                />
                <span>I confirm that I will not misuse the platform.</span>
              </label>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
              <div>
                <label className="block text-xs font-medium text-white mb-1">
                  Full name (for signature)
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full border border-white/20 rounded-md bg-white/10 px-2 py-1 text-sm text-white placeholder:text-white/60"
                  placeholder="Your full name"
                />
              </div>
              <div className="text-xs text-white flex flex-col justify-end">
                <p>
                  IP and timestamp will be recorded by the system when you submit
                  your signature.
                </p>
              </div>
            </div>

            <div className="pt-3">
              <button
                type="submit"
                disabled={submitDisabled}
                className="px-4 py-2 rounded-md bg-sky-500/80 text-white text-sm disabled:opacity-60"
              >
                {signing ? "Submitting..." : "Accept & Activate Account"}
              </button>
            </div>
          </form>
        </>
      )}
    </div>
  );
};

export default PartnerAgreementPage;
