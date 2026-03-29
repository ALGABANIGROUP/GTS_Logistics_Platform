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

const ALLOWED_COUNTRY_CODES = ["CA", "US"];
const PLANS_BY_ROLE = {
  carrier: {
    name: "Pro",
    planCode: "pro",
    priceCAD: 49,
    priceUSD: 36,
    period: "month",
    system: "loadboard",
    systemDescription:
      "Load board marketplace for posting loads, matching carriers, and managing spot opportunities.",
    subtitle: "Find loads and get paid faster",
    features: [
      "Load Search (unlimited)",
      "Truck Post (unlimited)",
      "Advanced Rate Insights",
      "Book It Now",
      "Real-Time Live Loads",
    ],
  },
  broker: {
    name: "Pro",
    planCode: "pro",
    priceCAD: 49,
    priceUSD: 36,
    period: "month",
    system: "tms",
    systemDescription:
      "Transportation Management System for shipment planning, tracking, and fleet operations.",
    subtitle: "Fill capacity and reduce risk",
    features: [
      "Everything in Basic",
      "Advanced Rate Insights",
      "Book It Now",
      "Real-Time Live Loads",
    ],
  },
  shipper: {
    name: "Basic",
    planCode: "basic",
    priceCAD: 19,
    priceUSD: 14,
    period: "month",
    system: "tms",
    systemDescription:
      "Transportation Management System for shipment planning, tracking, and fleet operations.",
    subtitle: "Streamline operations",
    features: [
      "Load Search (unlimited)",
      "Truck Post (unlimited)",
      "Basic Rate Insights",
    ],
  },
};

/**
 * Registration requirements:
 * - Choose ONE system: tms OR loadboard
 * - Choose role: shipper / carrier / broker
 * - Choose subscription plan
 * - After submit -> go to /login
 * - Save chosen system+role+plan so Login can redirect directly
 */
export default function Register() {
  const defaultRole = "carrier";
  const defaultRolePlan = PLANS_BY_ROLE[defaultRole];
  const navigate = useNavigate();
  const { disabled: registrationClosed, notice, reopenLabel, contactEmail } =
    registrationStatus;
  const companyRef = useRef(null);
  const defaultCountry = COUNTRIES.find((c) => c.iso2 === "CA") || COUNTRIES[0];
  const allowedCountries = useMemo(
    () => COUNTRIES.filter((country) => ALLOWED_COUNTRY_CODES.includes(country.iso2)),
    []
  );
  const defaultAllowedCountry =
    allowedCountries.find((c) => c.iso2 === "CA") || allowedCountries[0] || defaultCountry;

  const [form, setForm] = useState({
    companyName: "",
    fullName: "",
    username: "",
    email: "",
    phone: "",
    password: "",
    system: defaultRolePlan.system,
    role: defaultRole,
    subscription: defaultRolePlan.planCode,
    country: defaultCountry,
    comment: "",
  });
  const [role, setRole] = useState(defaultRole);
  const [selectedPlan, setSelectedPlan] = useState(defaultRolePlan);
  const [selectedSystem, setSelectedSystem] = useState(defaultRolePlan.system);
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [formError, setFormError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [emailExistsError, setEmailExistsError] = useState("");
  const [companyExistsError, setCompanyExistsError] = useState("");
  const [checkingEmail, setCheckingEmail] = useState(false);
  const [checkingCompany, setCheckingCompany] = useState(false);
  const hasValidationErrors = useMemo(
    () => Object.values(errors).some(Boolean),
    [errors]
  );
  const hasAvailabilityErrors = Boolean(emailExistsError || companyExistsError);

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
      if (name === "email") {
        setEmailExistsError("");
      }
      if (name === "companyName") {
        setCompanyExistsError("");
      }
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
    if (name === "email") {
      checkEmailAvailability(value);
    }
    if (name === "companyName") {
      checkCompanyAvailability(value);
    }
  };

  const handleRoleChange = (newRole) => {
    const rolePlan = PLANS_BY_ROLE[newRole];
    if (!rolePlan) {
      return;
    }

    setRole(newRole);
    setSelectedPlan(rolePlan);
    setSelectedSystem(rolePlan.system);
    setForm((prev) => ({
      ...prev,
      role: newRole,
      subscription: rolePlan.planCode,
      system: rolePlan.system,
    }));
    setTouched((prev) => ({ ...prev, role: true, subscription: true, system: true }));
    setErrors((prev) => ({ ...prev, role: "", system: "" }));
  };

  useEffect(() => {
    handleRoleChange(defaultRole);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    companyRef.current?.focus();
  }, []);

  useEffect(() => {
    setForm((prev) => {
      if (prev.country?.iso2 && ALLOWED_COUNTRY_CODES.includes(prev.country.iso2)) {
        return prev;
      }
      return { ...prev, country: defaultAllowedCountry };
    });
  }, [defaultAllowedCountry]);

  const checkEmailAvailability = async (emailValue) => {
    const normalized = String(emailValue || "").trim().toLowerCase();
    if (!normalized || !isValidEmail(normalized)) {
      setEmailExistsError("");
      return;
    }

    try {
      setCheckingEmail(true);
      const response = await axiosClient.get("/api/v1/auth/check-email", {
        params: { email: normalized },
      });
      if (response?.data?.exists) {
        setEmailExistsError("This email is already registered");
        return;
      }
      setEmailExistsError("");
    } catch {
      setEmailExistsError("");
    } finally {
      setCheckingEmail(false);
    }
  };

  const checkCompanyAvailability = async (companyValue) => {
    const normalized = String(companyValue || "").trim();
    if (!normalized) {
      setCompanyExistsError("");
      return;
    }

    try {
      setCheckingCompany(true);
      const response = await axiosClient.get("/api/v1/auth/check-company", {
        params: { company_name: normalized },
      });
      if (response?.data?.exists) {
        setCompanyExistsError("This company name is already registered");
        return;
      }
      setCompanyExistsError("");
    } catch {
      setCompanyExistsError("");
    } finally {
      setCheckingCompany(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      if (form.email) {
        checkEmailAvailability(form.email);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [form.email]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (form.companyName) {
        checkCompanyAvailability(form.companyName);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [form.companyName]);

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

    if (emailExistsError || companyExistsError) {
      setFormError("Please resolve duplicate email/company errors before continuing.");
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
        system_type: selectedSystem,
        subscription_tier: selectedPlan?.planCode || form.subscription,
        role: role,
        system: selectedSystem,
        plan: selectedPlan?.planCode || form.subscription,
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
          country: "country",
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
                        <FormError
                          message={companyExistsError || (touched.companyName ? errors.companyName : "")}
                          className="mt-1"
                        />
                        {checkingCompany ? (
                          <p className="mt-1 text-xs text-white/60">Checking company availability...</p>
                        ) : null}
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
                        <FormError
                          message={emailExistsError || (touched.email ? errors.email : "")}
                          className="mt-1"
                        />
                        {checkingEmail ? (
                          <p className="mt-1 text-xs text-white/60">Checking email availability...</p>
                        ) : null}
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
                        countries={allowedCountries}
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
                      <p className="mt-1 text-xs text-white/60">
                        Registration is available only for Canada and the United States.
                      </p>
                    </div>

                    <details className="rounded-xl border border-white/20">
                      <summary className="cursor-pointer px-4 py-3 text-white/80 font-medium">
                        Account setup (required)
                      </summary>
                      <div className="px-4 pb-4 pt-2 space-y-3">
                        <div className="mb-2">
                          <h3 className="text-lg font-semibold text-white mb-3">What type of trucking business are you?</h3>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                            {Object.entries(PLANS_BY_ROLE).map(([roleKey, rolePlan]) => (
                              <button
                                key={roleKey}
                                type="button"
                                onClick={() => handleRoleChange(roleKey)}
                                disabled={isSubmitting}
                                className={`rounded-xl border-2 p-4 text-left transition ${
                                  role === roleKey
                                    ? "border-red-500 bg-red-500/10"
                                    : "border-white/20 bg-white/5 hover:bg-white/10"
                                }`}
                              >
                                <h4 className="text-white font-semibold capitalize">I am a {roleKey}</h4>
                                <p className="text-xs text-white/70 mt-1">{rolePlan.subtitle}</p>
                                <p className="text-sm text-red-400 mt-2 font-semibold">
                                  Starting at ${rolePlan.priceCAD} CAD / month
                                </p>
                              </button>
                            ))}
                          </div>
                          <FormError message={touched.role ? errors.role : ""} className="mt-1" />
                        </div>

                        {selectedPlan ? (
                          <div className="rounded-xl border border-white/20 bg-white/5 p-4">
                            <div className="flex items-start justify-between gap-3 mb-3">
                              <div>
                                <h4 className="text-xl font-bold text-white">{selectedPlan.name}</h4>
                                <p className="text-sm text-white/80">
                                  ${selectedPlan.priceCAD} CAD / {selectedPlan.period}
                                  <span className="text-xs text-white/60 ml-2">≈ ${selectedPlan.priceUSD} USD</span>
                                </p>
                              </div>
                              <span className="text-xs px-2 py-1 rounded-full bg-white/10 text-white/80">
                                {selectedPlan.planCode.toUpperCase()}
                              </span>
                            </div>
                            <ul className="space-y-1.5">
                              {selectedPlan.features.map((feature, idx) => (
                                <li key={idx} className="text-sm text-white/80 flex items-center gap-2">
                                  <span className="text-green-400">✓</span>
                                  {feature}
                                </li>
                              ))}
                            </ul>
                          </div>
                        ) : null}

                        <div>
                          <h3 className="text-base font-semibold text-white mb-2">Select System</h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <button
                              type="button"
                              disabled={isSubmitting}
                              onClick={() => {
                                setSelectedSystem("tms");
                                setForm((prev) => ({ ...prev, system: "tms" }));
                                setTouched((prev) => ({ ...prev, system: true }));
                                setErrors((prev) => ({ ...prev, system: "" }));
                              }}
                              className={`rounded-lg border p-3 text-left transition ${
                                selectedSystem === "tms"
                                  ? "border-red-500 bg-red-500/10"
                                  : "border-white/15 bg-white/5 hover:bg-white/10"
                              }`}
                            >
                              <p className="text-sm font-semibold text-white">TMS</p>
                              <p className="mt-1 text-xs text-white/70">
                                Transportation Management System for shipment planning, tracking, and fleet operations.
                              </p>
                              {selectedSystem === "tms" ? (
                                <span className="inline-block mt-2 text-xs text-red-400">Recommended for you</span>
                              ) : null}
                            </button>
                            <button
                              type="button"
                              disabled={isSubmitting}
                              onClick={() => {
                                setSelectedSystem("loadboard");
                                setForm((prev) => ({ ...prev, system: "loadboard" }));
                                setTouched((prev) => ({ ...prev, system: true }));
                                setErrors((prev) => ({ ...prev, system: "" }));
                              }}
                              className={`rounded-lg border p-3 text-left transition ${
                                selectedSystem === "loadboard"
                                  ? "border-red-500 bg-red-500/10"
                                  : "border-white/15 bg-white/5 hover:bg-white/10"
                              }`}
                            >
                              <p className="text-sm font-semibold text-white">LoadBoard</p>
                              <p className="mt-1 text-xs text-white/70">
                                Load board marketplace for posting loads, matching carriers, and managing spot opportunities.
                              </p>
                              {selectedSystem === "loadboard" ? (
                                <span className="inline-block mt-2 text-xs text-red-400">Recommended for you</span>
                              ) : null}
                            </button>
                          </div>
                          <p className="mt-2 text-xs text-white/60">Recommended system for this role: {selectedPlan?.system?.toUpperCase()}</p>
                          <FormError message={touched.system ? errors.system : ""} className="mt-1" />
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
                    disabled={isSubmitting || requiredMissing || hasValidationErrors || hasAvailabilityErrors}
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
