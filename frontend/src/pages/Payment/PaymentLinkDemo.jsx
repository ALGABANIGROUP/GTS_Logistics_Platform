import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaArrowRight, FaLink } from "react-icons/fa";

export default function PaymentLinkDemo() {
  const navigate = useNavigate();
  const [paymentId, setPaymentId] = useState("1");

  const handleOpen = () => {
    const normalized = String(paymentId || "").trim();
    if (!normalized) {
      return;
    }
    navigate(`/pay/${encodeURIComponent(normalized)}`);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4 py-10 dark:bg-slate-950">
      <div className="w-full max-w-xl rounded-3xl border border-slate-200 bg-white p-8 shadow-xl dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-600 text-white">
            <FaLink />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Payment Link Preview</h1>
            <p className="text-sm text-slate-600 dark:text-slate-300">
              Open the secure payment link page using an existing payment id.
            </p>
          </div>
        </div>

        <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-600 dark:bg-slate-950/50 dark:text-slate-300">
          <div>Correct format:</div>
          <div className="mt-1 font-medium text-slate-900 dark:text-white">/pay/:paymentId</div>
          <div className="mt-3">Examples:</div>
          <div className="mt-1 font-medium text-slate-900 dark:text-white">1</div>
          <div className="font-medium text-slate-900 dark:text-white">PAY_TEST_001</div>
        </div>

        <div className="mt-6">
          <label htmlFor="payment-id" className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-200">
            Payment ID
          </label>
          <input
            id="payment-id"
            type="text"
            value={paymentId}
            onChange={(event) => setPaymentId(event.target.value)}
            placeholder="Enter a payment id"
            className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:focus:ring-blue-900"
          />
        </div>

        <button
          onClick={handleOpen}
          className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-medium text-white transition hover:bg-blue-700"
        >
          Open Payment Page
          <FaArrowRight />
        </button>

        <p className="mt-4 text-center text-xs text-slate-500 dark:text-slate-400">
          Use a real payment id from the backend for a successful end-to-end test.
        </p>
      </div>
    </div>
  );
}
