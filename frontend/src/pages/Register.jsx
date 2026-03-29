import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axiosClient from "../api/axiosClient";
import truckBg from "../assets/bg_login.png";
import Header from "../components/Header.jsx";
import Footer from "../components/Footer.jsx";
import GlassCard from "../components/ui/GlassCard.jsx";
import CountrySelect from "../components/ui/CountrySelect.jsx";
import { COUNTRIES } from "../constants/countries";
import FormError from "../components/ui/FormError.jsx";
import { isStrongPassword, isValidEmail, isValidPhone, normalizePhone } from "../utils/validators";
import { registrationStatus } from "../config/registration";

const ALLOWED_COUNTRY_CODES = ["CA", "US"];
const ROLE_PLANS = {
  carrier: [
    {
      name: "Basic",
      planCode: "basic",
      priceCAD: 19,
      priceUSD: 14,
      period: "month",
      system: "loadboard",
      features: ["Load Search", "Truck Post", "Basic Rate Insights"],
    },
    {
      name: "Pro",
      planCode: "pro",
      priceCAD: 49,
      priceUSD: 36,
      period: "month",
      system: "loadboard",
      popular: true,
      features: ["Everything in Basic", "Advanced Rate Insights", "Book It Now", "Real-Time Live Loads"],
    },
    {
      name: "Premium",
      planCode: "premium",
      priceCAD: 99,
      priceUSD: 73,
      period: "month",
      system: "loadboard",
      features: ["Everything in Pro", "Carrier Monitoring", "Predictive Sourcing", "Multi-Trip Search"],
    },
  ],
  broker: [
    {
      name: "Basic",
      planCode: "basic",
      priceCAD: 29,
      priceUSD: 21,
      period: "month",
      system: "tms",
      features: ["Load Search", "Broker Tools", "Basic Analytics"],
    },
    {
      name: "Pro",
      planCode: "pro",
      priceCAD: 79,
      priceUSD: 58,
      period: "month",
      system: "tms",
      popular: true,
      features: ["Everything in Basic", "Advanced Analytics", "API Access", "Priority Support"],
    },
    {
      name: "Enterprise",
      planCode: "enterprise",
      priceCAD: 199,
      priceUSD: 147,
      period: "month",
      system: "tms",
      features: ["Everything in Pro", "Dedicated Account Manager", "Custom Integration"],
    },
  ],
  shipper: [
    {
      name: "Basic",
      planCode: "basic",
      priceCAD: 29,
      priceUSD: 21,
      period: "month",
      system: "tms",
      features: ["Shipment Tracking", "Basic Reporting", "Email Support"],
    },
    {
      name: "Pro",
      planCode: "pro",
      priceCAD: 99,
      priceUSD: 73,
      period: "month",
      system: "tms",
      popular: true,
      features: ["Everything in Basic", "Real-Time Tracking", "Advanced Analytics", "Phone Support"],
    },
    {
      name: "Enterprise",
      planCode: "enterprise",
      priceCAD: 299,
      priceUSD: 221,
      period: "month",
      system: "tms",
      features: ["Everything in Pro", "Dedicated Account Manager", "Custom Integration"],
    },
  ],
};

const ROLE_LABELS = {
  carrier: {
    title: "I am a Carrier",
    description: "Find loads and get paid faster",
  },
  broker: {
    title: "I am a Broker",
    description: "Fill capacity and reduce risk",
  },
  shipper: {
    title: "I am a Shipper",
    description: "Streamline operations",
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
  const defaultSelectedPlan = ROLE_PLANS[defaultRole].find((plan) => plan.popular) || ROLE_PLANS[defaultRole][0];
  const navigate = useNavigate();
  const { disabled: registrationClosed, notice, reopenLabel, contactEmail } =
    registrationStatus;
  const companyRef = useRef(null);
  const redirectTimerRef = useRef(null);
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
    system: defaultSelectedPlan.system,
    role: defaultRole,
    subscription: defaultSelectedPlan.planCode,
    country: defaultCountry,
    comment: "",
  });
  const [step, setStep] = useState("select");
  const [role, setRole] = useState(defaultRole);
  const [selectedPlan, setSelectedPlan] = useState(defaultSelectedPlan);
  const [selectedSystem, setSelectedSystem] = useState(defaultSelectedPlan.system);
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [formError, setFormError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [toastMessage, setToastMessage] = useState({ type: "", text: "" });
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
    const availablePlans = ROLE_PLANS[newRole] || [];
    if (availablePlans.length === 0) {
      return;
    }

    const roleDefaultPlan = availablePlans.find((plan) => plan.popular) || availablePlans[0];
    setRole(newRole);
    setSelectedPlan(roleDefaultPlan);
    setSelectedSystem(roleDefaultPlan.system);
    setForm((prev) => ({
      ...prev,
      role: newRole,
      subscription: roleDefaultPlan.planCode,
      system: roleDefaultPlan.system,
    }));
    setTouched((prev) => ({ ...prev, role: true }));
    setErrors((prev) => ({ ...prev, role: "", system: "" }));
  };

  const handleSelectPlan = (plan) => {
    setSelectedPlan(plan);
    setSelectedSystem(plan.system);
    setForm((prev) => ({
      ...prev,
      role,
      subscription: plan.planCode,
      system: plan.system,
    }));
    setStep("form");
  };

  useEffect(() => {
    handleRoleChange(defaultRole);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (step === "form") {
      companyRef.current?.focus();
    }
  }, [step]);

  useEffect(() => {
    setForm((prev) => {
      if (prev.country?.iso2 && ALLOWED_COUNTRY_CODES.includes(prev.country.iso2)) {
        return prev;
      }
      return { ...prev, country: defaultAllowedCountry };
    });
  }, [defaultAllowedCountry]);

  useEffect(() => {
    return () => {
      if (redirectTimerRef.current) {
        clearTimeout(redirectTimerRef.current);
      }
    };
  }, []);

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
    setToastMessage({ type: "", text: "" });

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
      const res = await axiosClient.post("/api/v1/auth/register", payload);
      if (res?.status >= 200 && res?.status < 300 && res?.data?.ok) {
        const message = "Registration successful! Please check your email to verify your account.";
        setSuccessMessage(message);
        setToastMessage({ type: "success", text: message });
        redirectTimerRef.current = setTimeout(() => {
          navigate("/login", { replace: true });
        }, 3000);
        return;
      }
      setToastMessage({ type: "error", text: "Registration failed. Please try again." });
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
        setToastMessage({ type: "error", text: detail.message || "Invalid value." });
      } else if (status === 422) {
        setFormError("Please review the highlighted fields.");
        setToastMessage({ type: "error", text: "Please review the highlighted fields." });
      } else if (status === 401 || status === 403) {
        setFormError("Access denied. Please check your details.");
        setToastMessage({ type: "error", text: "Access denied. Please check your details." });
      } else if (typeof detail === "string") {
        setFormError(detail);
        setToastMessage({ type: "error", text: detail });
      } else if (err?.response?.data?.message) {
        setFormError(err.response.data.message);
        setToastMessage({ type: "error", text: err.response.data.message });
      } else {
        setFormError("Registration failed. Please try again.");
        setToastMessage({ type: "error", text: "Registration failed. Please try again." });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      {toastMessage.text ? (
        <div
          className={`fixed top-20 right-4 z-50 px-4 py-3 rounded-lg shadow-lg text-white text-sm ${toastMessage.type === "success" ? "bg-green-600" : "bg-red-600"
            }`}
        >
          {toastMessage.text}
        </div>
      ) : null}
      <Header hidePricing={true} />
      <div
        className="relative min-h-screen overflow-hidden"
        style={{
          backgroundImage: `url(${truckBg})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
        }}
      >
        <div className="absolute inset-0 bg-black/10" />

        <div className="relative z-10 w-full min-h-screen flex items-center justify-center px-4 py-8">
          <div className="w-full max-w-3xl">
            <div className="text-center mb-6">
              <h1 className="text-white text-xl font-semibold">
                {step === "select" ? "Choose Your Plan" : "Complete Registration"}
              </h1>
              <p className="text-white/70 mt-2">
                {step === "select"
                  ? "Pick your role and plan, then continue to account setup."
                  : "Finish your details to create your account."}
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
                  {step === "select" ? (
                    <div className="space-y-5 overflow-y-auto max-h-[calc(100vh-220px)] pr-2">
                      <div>
                        <h3 className="text-white text-base font-semibold mb-3">What type of trucking business are you?</h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                          {Object.entries(ROLE_LABELS).map(([roleKey, roleMeta]) => (
                            <button
                              key={roleKey}
                              type="button"
                              onClick={() => handleRoleChange(roleKey)}
                              className={`rounded-xl border-2 p-4 text-left transition ${role === roleKey
                                ? "border-red-500 bg-red-500/10"
                                : "border-white/20 bg-white/5 hover:bg-white/10"
                                }`}
                            >
                              <h4 className="text-white font-semibold">{roleMeta.title}</h4>
                              <p className="text-xs text-white/70 mt-1">{roleMeta.description}</p>
                              <p className="text-sm text-red-400 mt-2 font-semibold">
                                Starting at ${ROLE_PLANS[roleKey][0].priceCAD} CAD / month
                              </p>
                            </button>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h3 className="text-white text-base font-semibold mb-3">Select your plan</h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                          {(ROLE_PLANS[role] || []).map((plan) => (
                            <div
                              key={`${role}-${plan.planCode}`}
                              className={`rounded-xl border p-4 ${plan.popular ? "border-red-500 bg-red-500/10" : "border-white/20 bg-white/5"}`}
                            >
                              {plan.popular ? (
                                <span className="inline-block text-[11px] px-2 py-1 rounded-full bg-red-600 text-white mb-2">
                                  Most Popular
                                </span>
                              ) : null}
                              <h4 className="text-lg font-bold text-white">{plan.name}</h4>
                              <p className="text-white mt-1">
                                <span className="text-2xl font-bold">${plan.priceCAD}</span>
                                <span className="text-sm text-white/70"> CAD / {plan.period}</span>
                              </p>
                              <p className="text-xs text-white/60 mt-1">Approx. ${plan.priceUSD} USD</p>
                              <ul className="mt-3 space-y-1.5 min-h-[84px]">
                                {plan.features.map((feature, idx) => (
                                  <li key={idx} className="text-xs text-white/80 flex items-center gap-2">
                                    <span className="text-green-400">✓</span>
                                    {feature}
                                  </li>
                                ))}
                              </ul>
                              <button
                                type="button"
                                onClick={() => handleSelectPlan(plan)}
                                className="mt-3 w-full rounded-lg bg-red-600 hover:bg-red-700 text-white text-sm font-semibold py-2 transition"
                              >
                                Complete Registration
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <form onSubmit={submit} className="flex flex-col gap-4">
                      <div className="space-y-4 overflow-y-auto max-h-[calc(100vh-260px)] pr-2">
                        {selectedPlan ? (
                          <div className="rounded-xl border border-white/20 bg-white/5 p-4">
                            <div className="flex flex-wrap items-start justify-between gap-3">
                              <div>
                                <p className="text-white/70 text-xs uppercase tracking-wide">Selected plan</p>
                                <h3 className="text-lg font-semibold text-white capitalize">{role} - {selectedPlan.name}</h3>
                                <p className="text-sm text-white/80 mt-1">
                                  ${selectedPlan.priceCAD} CAD / {selectedPlan.period}
                                  <span className="text-xs text-white/60 ml-2">Approx. ${selectedPlan.priceUSD} USD</span>
                                </p>
                                <p className="text-xs text-white/60 mt-1">System: {selectedSystem.toUpperCase()}</p>
                              </div>
                              <button
                                type="button"
                                onClick={() => setStep("select")}
                                className="text-sm text-red-300 hover:text-red-200 transition"
                              >
                                Change Plan
                              </button>
                            </div>
                          </div>
                        ) : null}

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
                            Plan and system summary
                          </summary>
                          <div className="px-4 pb-4 pt-2 space-y-3">
                            <p className="text-sm text-white/80">
                              Role: <span className="font-semibold capitalize">{role}</span>
                            </p>
                            <p className="text-sm text-white/80">
                              Plan: <span className="font-semibold">{selectedPlan?.name}</span>
                            </p>
                            <p className="text-sm text-white/80">
                              System: <span className="font-semibold uppercase">{selectedSystem}</span>
                            </p>
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

                      <div className="text-center mt-2">
                        <p className="text-white/70 text-sm">
                          Already have an account?{" "}
                          <Link to="/login" className="text-red-300 hover:text-red-200 underline underline-offset-2">
                            Sign in
                          </Link>
                        </p>
                      </div>
                    </form>
                  )}
                </>
              )}
            </GlassCard>

            <p className="text-center text-white/40 text-xs mt-4">
              Your system, role, and plan are stored during registration for a cleaner first login.
            </p>
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
}
