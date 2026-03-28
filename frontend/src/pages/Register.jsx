import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import axiosClient from "../api/axiosClient";
import truckBg from "../assets/bg_login.png";
import GlassCard from "../components/ui/GlassCard.jsx";
import CountrySelect from "../components/ui/CountrySelect.jsx";
import { COUNTRIES } from "../constants/countries";
import FormError from "../components/ui/FormError.jsx";
import { isStrongPassword, isValidEmail, isValidPhone, normalizePhone } from "../utils/validators";
import { registrationStatus } from "../config/registration";
import { getPlans, getPolicyContext } from "../services/billingApi";
import { formatTierLabel, normalizeTier } from "../utils/tierUtils";

const DEFAULT_PLAN_OPTIONS = [
  { value: "free", label: "Free - 0 / month" },
  { value: "starter", label: "Starter - 9 / month" },
  { value: "growth", label: "Growth - 19 / month" },
  { value: "professional", label: "Professional - 39 / month" },
  { value: "enterprise", label: "Enterprise - 79 / month" },
];

/**
 * Registration requirements:
 * - Choose ONE system: tms OR loadboard
 * - Choose role: shipper / carrier / broker
 * - Choose subscription plan
 * - After submit -> go to /login
 * - Save chosen system+role+plan so Login can redirect directly
 */
export default function Register() {
  const navigate = useNavigate();
  const { disabled: registrationClosed, notice, reopenLabel, contactEmail } =
    registrationStatus;
  const companyRef = useRef(null);
  const defaultCountry = COUNTRIES.find((c) => c.iso2 === "US") || COUNTRIES[0];

  const [form, setForm] = useState({
    companyName: "",
    fullName: "",
    username: "",
    email: "",
    phone: "",
    password: "",
    system: "",
    role: "",
    subscription: "free",
    country: defaultCountry,
    comment: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [formError, setFormError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [planOptions, setPlanOptions] = useState(DEFAULT_PLAN_OPTIONS);
  const hasValidationErrors = useMemo(
    () => Object.values(errors).some(Boolean),
    [errors]
  );

  const requiredMissing = useMemo(() => {
    return (
      !form.companyName.trim() ||
      !form.fullName.trim() ||
      !form.username.trim() ||
      !form.email.trim() ||
      !form.password.trim() ||
      !form.phone.trim() ||
      !form.country?.iso2
    );
  }, [form]);

  const validateField = (field, value, nextForm = form) => {
    switch (field) {
      case "companyName":
      case "fullName":
        return value.trim() ? "" : "This field is required.";
      case "username":
        return value.trim().length >= 3
          ? ""
          : "Username must be at least 3 characters.";
      case "email":
        return isValidEmail(value) ? "" : "Enter a valid email address.";
      case "password":
        return isStrongPassword(value)
          ? ""
          : "Password must be 8+ chars with a number and uppercase letter.";
      case "phone":
        return isValidPhone(value) ? "" : "Enter a valid phone number.";
      case "country":
        return nextForm.country?.iso2 ? "" : "Select a country.";
      case "system":
        return nextForm.system ? "" : "Select a system.";
      case "role":
        return nextForm.role ? "" : "Select a role.";
      default:
        return "";
    }
  };

  const validateAll = (nextForm = form) => {
    const nextErrors = {};
    [
      "companyName",
      "fullName",
      "username",
      "email",
      "password",
      "phone",
      "country",
      "system",
      "role",
    ].forEach((field) => {
      const value = nextForm[field] ?? "";
      const message = validateField(field, value, nextForm);
      if (message) nextErrors[field] = message;
    });
    return nextErrors;
  };

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => {
      const next = { ...prev, [name]: value };
      if (touched[name]) {
        setErrors((curr) => ({ ...curr, [name]: validateField(name, value, next) }));
      }
      return next;
    });
  };

  const onBlur = (e) => {
    const { name, value } = e.target;
    setTouched((prev) => ({ ...prev, [name]: true }));
    setErrors((curr) => ({ ...curr, [name]: validateField(name, value, form) }));
  };

  useEffect(() => {
    companyRef.current?.focus();
  }, []);

  useEffect(() => {
    let active = true;

    const loadPlans = async () => {
      try {
        const context = await getPolicyContext();
        const region = context?.country || context?.region || "GLOBAL";
        const plansResponse = await getPlans(region);
        const options = (plansResponse?.plans || []).map((plan) => ({
          value: normalizeTier(plan?.code),
          label: `${plan?.name || formatTierLabel(plan?.code)} - ${plan?.price_amount ?? "0"} ${plan?.currency || "USD"} / month`,
        }));

        if (!active || options.length === 0) return;
        setPlanOptions(options);
        setForm((prev) => {
          if (options.some((opt) => opt.value === prev.subscription)) {
            return prev;
          }
          return { ...prev, subscription: options[0].value };
        });
      } catch {
        if (!active) return;
        setPlanOptions(DEFAULT_PLAN_OPTIONS);
      }
    };

    loadPlans();
    return () => {
      active = false;
    };
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    setFormError("");
    setSuccessMessage("");

    const nextErrors = validateAll();
    setErrors(nextErrors);
    setTouched({
      companyName: true,
      fullName: true,
      username: true,
      email: true,
      password: true,
      phone: true,
      country: true,
      system: true,
      role: true,
    });

    if (Object.keys(nextErrors).length > 0) {
      return;
    }

    setIsSubmitting(true);

    try {
      const normalizedPhone = normalizePhone(form.phone);
      const payload = {
        email: form.email.trim(),
        password: form.password,
        full_name: form.fullName.trim(),
        username: form.username.trim(),
        company_name: form.companyName.trim(),
        country: form.country?.iso2 || "",
        phone_number: `${form.country?.callingCode || ""}${normalizedPhone}`,
        system_type: form.system,
        subscription_tier: form.subscription,
        role: form.role || "user",
      };
      const res = await axiosClient.post("/auth/register", payload);
      if (res.data && res.data.ok) {
        setSuccessMessage("Registration successful! Please sign in.");
        navigate("/login", { replace: true });
        return;
      }
      setFormError("Registration failed. Please try again.");
    } catch (err) {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail;
      if (status === 400 && detail && typeof detail === "object") {
        const fieldMap = {
          company_name: "companyName",
          full_name: "fullName",
          phone_number: "phone",
        };
        const fieldKey = fieldMap[detail.field] || detail.field;
        setErrors((curr) => ({ ...curr, [fieldKey]: detail.message || "Invalid value." }));
      } else if (status === 422) {
        setFormError("Please review the highlighted fields.");
      } else if (status === 401 || status === 403) {
        setFormError("Access denied. Please check your details.");
      } else if (typeof detail === "string") {
        setFormError(detail);
      } else if (err?.response?.data?.message) {
        setFormError(err.response.data.message);
      } else {
        setFormError("Registration failed. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="relative min-h-screen h-screen overflow-hidden"
      style={{
        backgroundImage: `url(${truckBg})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      <div className="absolute inset-0 bg-black/10" />

      <div className="relative z-10 w-full h-full flex items-center justify-center px-4">
        <div className="w-full max-w-3xl">
          <div className="text-center mb-6">
            <h1 className="text-white text-xl font-semibold">Create Account</h1>
            <p className="text-white/70 mt-2">
              Create your GTS account, choose your system and plan, then sign in immediately after registration.
            </p>
          </div>

          <GlassCard className="w-full max-w-3xl max-h-[calc(100vh-140px)] flex flex-col overflow-hidden">
            {registrationClosed ? (
              <div className="flex flex-col items-center gap-4 text-center text-white">
                <h2 className="text-2xl font-semibold">Registration is paused</h2>
                <p className="text-sm text-white/80">{notice}</p>
                {reopenLabel && (
                  <p className="text-xs text-white/60">
                    Expected to reopen on {reopenLabel}.
                  </p>
                )}
                <p className="text-xs text-white/60">
                  Contact{" "}
                  <a
                    href={`mailto:${contactEmail}`}
                    className="text-white underline"
                  >
                    {contactEmail}
                  </a>{" "}
                  for expedited approval.
                </p>
                <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => navigate("/login")}
                    className="rounded-full border border-white/30 px-4 py-2 text-sm font-semibold text-white transition hover:border-white"
                  >
                    Back to login
                  </button>
                  <button
                    type="button"
                    onClick={() => navigate("/")}
                    className="rounded-full border border-white/30 px-4 py-2 text-sm font-semibold text-white transition hover:border-white"
                  >
                    Back to portal
                  </button>
                </div>
              </div>
            ) : (
              <>
                {successMessage && (
                  <div className="mb-4 rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">
                    {successMessage}
                  </div>
                )}
                <FormError message={formError} className="mb-3 text-center" />
                <form onSubmit={submit} className="flex flex-col gap-4">
                  <div className="space-y-4 overflow-y-auto max-h-[calc(100vh-260px)] pr-2">
                    {/* Basic info */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <input
                          className="w-full rounded-xl border border-white/20 bg-white/5 backdrop-blur-md px-4 py-3 text-white placeholder:text-white/50 outline-none focus:border-white/40"
                          placeholder="Company Name"
                          name="companyName"
                          autoComplete="organization"
                          value={form.companyName}
                          onChange={onChange}
                          onBlur={onBlur}
                          aria-invalid={Boolean(touched.companyName && errors.companyName)}
                          disabled={isSubmitting}
                          ref={companyRef}
                          required
                        />
                        <FormError message={touched.companyName ? errors.companyName : ""} className="mt-1" />
                      </div>
                      <div>
                        <input
                          className="w-full rounded-xl border border-white/20 bg-white/5 backdrop-blur-md px-4 py-3 text-white placeholder:text-white/50 outline-none focus:border-white/40"
                          placeholder="Username"
                          name="username"
                          autoComplete="username"
                          value={form.username}
                          onChange={onChange}
                          onBlur={onBlur}
                          aria-invalid={Boolean(touched.username && errors.username)}
                          disabled={isSubmitting}
                          required
                        />
                        <FormError message={touched.username ? errors.username : ""} className="mt-1" />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <input
                          className="w-full rounded-xl border border-white/20 bg-white/5 backdrop-blur-md px-4 py-3 text-white placeholder:text-white/50 outline-none focus:border-white/40"
                          placeholder="Full Name"
                          name="fullName"
                          autoComplete="name"
                          value={form.fullName}
                          onChange={onChange}
                          onBlur={onBlur}
                          aria-invalid={Boolean(touched.fullName && errors.fullName)}
                          disabled={isSubmitting}
                          required
                        />
                        <FormError message={touched.fullName ? errors.fullName : ""} className="mt-1" />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <input
                          className="w-full rounded-xl border border-white/20 bg-white/5 backdrop-blur-md px-4 py-3 text-white placeholder:text-white/50 outline-none focus:border-white/40"
                          placeholder="Email"
                          type="email"
                          name="email"
                          autoComplete="email"
                          value={form.email}
                          onChange={onChange}
                          onBlur={onBlur}
                          aria-invalid={Boolean(touched.email && errors.email)}
                          disabled={isSubmitting}
                          required
                        />
                        <FormError message={touched.email ? errors.email : ""} className="mt-1" />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <div className="flex">
                          <span className="inline-flex items-center rounded-l-xl border border-white/20 bg-white/5 backdrop-blur-md px-3 text-white/80">
                            {form.country?.callingCode || "+--"}
                          </span>
                          <input
                            className="w-full rounded-r-xl border border-white/20 bg-white/5 backdrop-blur-md border-l-0 px-4 py-3 text-white placeholder:text-white/50 outline-none focus:border-white/40"
                            placeholder="Phone"
                            name="phone"
                            autoComplete="tel"
                            value={form.phone}
                            onChange={onChange}
                            onBlur={onBlur}
                            aria-invalid={Boolean(touched.phone && errors.phone)}
                            disabled={isSubmitting}
                            required
                          />
                        </div>
                        <FormError message={touched.phone ? errors.phone : ""} className="mt-1" />
                      </div>
                      <div>
                        <div className="relative">
                          <input
                            className="w-full rounded-xl border border-white/20 bg-white/5 backdrop-blur-md px-4 py-3 text-white placeholder:text-white/50 outline-none focus:border-white/40 pr-12"
                            placeholder="Password"
                            type={showPassword ? "text" : "password"}
                            name="password"
                            autoComplete="new-password"
                            value={form.password}
                            onChange={onChange}
                            onBlur={onBlur}
                            aria-invalid={Boolean(touched.password && errors.password)}
                            disabled={isSubmitting}
                            required
                          />
                          <button
                            type="button"
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-white/60 hover:text-white/90 text-xs"
                            tabIndex={-1}
                            onClick={() => setShowPassword((v) => !v)}
                            disabled={isSubmitting}
                          >
                            {showPassword ? "Hide" : "Show"}
                          </button>
                        </div>
                        <FormError message={touched.password ? errors.password : ""} className="mt-1" />
                      </div>
                    </div>

                    <div>
                      <CountrySelect
                        value={form.country}
                        invalid={Boolean(touched.country && errors.country)}
                        disabled={isSubmitting}
                        onChange={(next) => {
                          setForm((prev) => ({ ...prev, country: next }));
                          setTouched((prev) => ({ ...prev, country: true }));
                          setErrors((curr) => ({
                            ...curr,
                            country: validateField("country", next?.iso2 || "", { ...form, country: next }),
                          }));
                        }}
                      />
                      <FormError message={touched.country ? errors.country : ""} className="mt-1" />
                    </div>

                    <details className="rounded-xl border border-white/20">
                      <summary className="cursor-pointer px-4 py-3 text-white/80 font-medium">
                        Account setup (required)
                      </summary>
                      <div className="px-4 pb-4 pt-2 space-y-3">
                        <div>
                          <label className="block text-white/80 text-sm font-medium mb-2">
                            Subscription Plan
                          </label>
                          <select
                            name="subscription"
                            value={form.subscription}
                            onChange={onChange}
                            disabled={isSubmitting}
                            className="w-full rounded-xl border border-white/20 bg-white/5 backdrop-blur-md px-4 py-3 text-white placeholder:text-white/50 outline-none focus:border-white/40"
                          >
                            {planOptions.map((opt) => (
                              <option key={opt.value} value={opt.value}>
                                {opt.label}
                              </option>
                            ))}
                          </select>
                          <p className="text-white/60 text-xs mt-1">
                            This list is synced with the same pricing model shown on the pricing page.
                          </p>
                        </div>

                        <div>
                          <label className="block text-white/80 text-sm font-medium mb-2">
                            System
                          </label>
                          <select
                            name="system"
                            value={form.system}
                            onChange={onChange}
                            onBlur={onBlur}
                            aria-invalid={Boolean(touched.system && errors.system)}
                            disabled={isSubmitting}
                            required
                            className="w-full rounded-xl border border-white/20 bg-white/5 backdrop-blur-md px-4 py-3 text-white placeholder:text-white/50 outline-none focus:border-white/40"
                          >
                            <option value="" disabled>
                              Select system
                            </option>
                            <option value="tms">TMS</option>
                            <option value="loadboard">LoadBoard</option>
                          </select>
                          <FormError message={touched.system ? errors.system : ""} className="mt-1" />
                        </div>

                        <div>
                          <label className="block text-white/80 text-sm font-medium mb-2">
                            Role
                          </label>
                          <select
                            name="role"
                            value={form.role}
                            onChange={onChange}
                            onBlur={onBlur}
                            aria-invalid={Boolean(touched.role && errors.role)}
                            disabled={isSubmitting}
                            required
                            className="w-full rounded-xl border border-white/20 bg-white/5 backdrop-blur-md px-4 py-3 text-white placeholder:text-white/50 outline-none focus:border-white/40"
                          >
                            <option value="" disabled>
                              Select role
                            </option>
                            <option value="shipper">Shipper</option>
                            <option value="carrier">Carrier</option>
                            <option value="broker">Broker</option>
                          </select>
                          <FormError message={touched.role ? errors.role : ""} className="mt-1" />
                        </div>
                      </div>
                    </details>

                    <details className="rounded-xl border border-white/20">
                      <summary className="cursor-pointer px-4 py-3 text-white/80 font-medium">
                        More details (optional)
                      </summary>
                      <div className="px-4 pb-4 pt-2">
                        <textarea
                          className="w-full min-h-[80px] rounded-xl border border-white/20 bg-white/5 backdrop-blur-md px-4 py-3 text-white placeholder:text-white/50 outline-none focus:border-white/40 resize-none"
                          placeholder="Tell us anything else (optional)"
                          name="comment"
                          value={form.comment}
                          onChange={onChange}
                          disabled={isSubmitting}
                        />
                      </div>
                    </details>
                  </div>

                  <button
                    type="submit"
                    disabled={isSubmitting || requiredMissing || hasValidationErrors}
                    className="w-full rounded-xl bg-black/30 hover:bg-black/40 text-white font-semibold py-3 border border-white/20 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isSubmitting ? "Processing..." : "Create Account"}
                  </button>

                  <div className="pt-3 border-t border-white/10 flex justify-between text-sm">
                    <button
                      type="button"
                      className="text-white/70 hover:text-white transition"
                      onClick={() => navigate("/login")}
                    >
                      Already have an account? Sign In
                    </button>
                    <button
                      type="button"
                      className="text-white/70 hover:text-white transition"
                      onClick={() => navigate("/")}
                    >
                      Back to Portal
                    </button>
                  </div>
                </form>
              </>
            )}
          </GlassCard>

          <p className="text-center text-white/40 text-xs mt-4">
            Your system, role, and plan are stored during registration for a cleaner first login.
          </p>
        </div>
      </div>
    </div>
  );
}
