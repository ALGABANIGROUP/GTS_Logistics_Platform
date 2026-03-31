import { useState } from "react";
import { useNavigate } from "react-router-dom";
import portalBg from "../../assets/bg_login.png";

/**
 * Multi-step Register component
 * - Validation is performed at final submit (as requested)
 * - Subdomain input was added because backend signup API requires it
 * - On submit: POST /api/v1/signup/register
 */

export default function Register() {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        // Step 1: Basic Info
        name: "",
        email: "",
        phone: "",
        password: "",
        company: "",
        subdomain: "",
        // Step 2: System Selection
        system: "", // "tms" or "loadboard"
        // Step 3: Role Selection
        role: "", // "shipper", "carrier", "broker"
    });
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    // Move between steps without blocking. Final validation on submit.
    const handleNext = () => {
        if (step < 3) setStep(step + 1);
    };

    const handleBack = () => {
        if (step > 1) setStep(step - 1);
    };

    // Helper validators
    const _isEmail = (value) => {
        if (!value) return false;
        // simple regex
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    };

    const _isPhone = (value) => {
        if (!value) return false;
        // allow + and digits and common separators (basic)
        return /^[+\d][\d\s\-()]{6,}$/.test(value);
    };

    const _validateSubdomain = (value) => {
        if (!value) return false;
        const s = value.trim();
        if (s.length < 3 || s.length > 20) return false;
        if (!/^[a-zA-Z0-9-]+$/.test(s)) return false;
        if (s.startsWith("-") || s.endsWith("-")) return false;
        const reserved = new Set(["www", "app", "api", "admin", "mail", "ftp", "localhost", "example"]);
        if (reserved.has(s.toLowerCase())) return false;
        return true;
    };

    const validateAll = () => {
        const e = {};
        if (!formData.name || formData.name.trim().length < 2) {
            e.name = "Please enter your full name (min 2 chars).";
        }
        if (!formData.company || formData.company.trim().length < 2) {
            e.company = "Please enter company name (min 2 chars).";
        }
        if (!formData.subdomain || !_validateSubdomain(formData.subdomain)) {
            e.subdomain = "Subdomain must be 3–20 chars, alphanumeric and hyphens only. No leading/trailing hyphens.";
        }
        if (!formData.email || !_isEmail(formData.email)) {
            e.email = "Please enter a valid email address.";
        }
        if (!formData.phone || !_isPhone(formData.phone)) {
            e.phone = "Please enter a valid phone number.";
        }
        if (!formData.password || formData.password.length < 8) {
            e.password = "Password must be at least 8 characters.";
        }
        if (!formData.system) {
            e.system = "Please choose a primary system.";
        }
        if (!formData.role) {
            e.role = "Please choose a role.";
        }

        setErrors(e);
        return Object.keys(e).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // final validation
        if (!validateAll()) {
            // jump to the first problematic step
            if (errors.subdomain || errors.name || errors.company || errors.email || errors.phone || errors.password) {
                setStep(1);
            } else if (errors.system) {
                setStep(2);
            } else if (errors.role) {
                setStep(3);
            }
            return;
        }

        setLoading(true);
        try {
            // Map to backend signup payload
            const payload = {
                company_name: formData.company,
                subdomain: formData.subdomain,
                owner_email: formData.email,
                owner_name: formData.name,
                owner_password: formData.password,
            };

            const resp = await fetch("/api/v1/signup/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            const body = await resp.json().catch(() => ({}));

            if (!resp.ok) {
                // backend returns a detail message for validation errors
                const serverErr = body.detail || body.message || "Registration failed";
                alert(`Registration failed: ${serverErr}`);
                // If subdomain taken or email taken, surface it
                if (serverErr.toLowerCase().includes("subdomain")) {
                    setErrors((prev) => ({ ...prev, subdomain: serverErr }));
                    setStep(1);
                } else if (serverErr.toLowerCase().includes("email")) {
                    setErrors((prev) => ({ ...prev, email: serverErr }));
                    setStep(1);
                }
                return;
            }

            // success path
            // backend returns message and tenant_id on success
            alert(body.message || "Registration successful! Please check your email to verify.");
            // redirect to login (or a "check your email" page)
            navigate("/login?registered=true");
        } catch (err) {
            console.error("Registration error:", err);
            alert("Registration failed (network error). Please try again.");
        } finally {
            setLoading(false);
        }
    };

    // small helper to render input with error
    const InputWithError = ({ label, type = "text", value, onChange, placeholder = "", name }) => (
        <div>
            <label className="block text-white/80 text-sm font-medium mb-2">{label}</label>
            <input
                type={type}
                name={name}
                className={`w-full rounded-xl bg-white/10 border px-4 py-3.5 text-white placeholder:text-white/40 outline-none focus:border-white/40 transition
                    ${errors[name] ? "border-red-400/80" : "border-white/20"}`}
                placeholder={placeholder}
                value={value}
                onChange={onChange}
            />
            {errors[name] && <p className="text-red-400 text-xs mt-2">{errors[name]}</p>}
        </div>
    );

    return (
        <div
            className="min-h-screen w-full bg-cover bg-center bg-no-repeat relative"
            style={{ backgroundImage: `url(${portalBg})` }}
        >
            <div className="absolute inset-0 bg-black/45" />
            <div className="relative z-10 min-h-screen flex items-center justify-center px-4">
                <div className="w-full max-w-2xl">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <h2 className="text-white text-3xl font-bold">Request Access</h2>
                        <p className="text-white/70 mt-2">
                            {step === 1 && "Enter your basic information"}
                            {step === 2 && "Choose your primary system"}
                            {step === 3 && "Select your role"}
                        </p>
                    </div>

                    {/* Step indicator */}
                    <div className="flex justify-between mb-10 max-w-md mx-auto">
                        {[1, 2, 3].map((s) => (
                            <div key={s} className="flex flex-col items-center">
                                <div
                                    className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${step >= s
                                        ? "bg-white/20 border-white/30"
                                        : "bg-white/5 border-white/10"
                                        }`}
                                >
                                    <span className={`text-sm font-semibold ${step >= s ? "text-white" : "text-white/30"}`}>
                                        {s}
                                    </span>
                                </div>
                                <span className="text-white/50 text-xs mt-2">
                                    {s === 1 && "Info"}
                                    {s === 2 && "System"}
                                    {s === 3 && "Role"}
                                </span>
                            </div>
                        ))}
                    </div>

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="rounded-2xl border border-white/20 bg-white/10 backdrop-blur-xl shadow-2xl p-8">
                        {step === 1 && (
                            <div className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <InputWithError
                                        label="Full Name *"
                                        value={formData.name}
                                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                        placeholder="John Doe"
                                        name="name"
                                    />
                                    <InputWithError
                                        label="Company *"
                                        value={formData.company}
                                        onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                                        placeholder="Company Name"
                                        name="company"
                                    />
                                </div>

                                <InputWithError
                                    label="Subdomain *"
                                    value={formData.subdomain}
                                    onChange={(e) => setFormData({ ...formData, subdomain: e.target.value })}
                                    placeholder="your-company-subdomain"
                                    name="subdomain"
                                />

                                <InputWithError
                                    label="Email Address *"
                                    type="email"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    placeholder="you@company.com"
                                    name="email"
                                />

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <InputWithError
                                        label="Phone Number *"
                                        type="tel"
                                        value={formData.phone}
                                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                        placeholder="+1234567890"
                                        name="phone"
                                    />
                                    <InputWithError
                                        label="Password *"
                                        type="password"
                                        value={formData.password}
                                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                        placeholder="••••••••"
                                        name="password"
                                    />
                                </div>

                                <div className="flex gap-4">
                                    <button
                                        type="button"
                                        onClick={handleNext}
                                        className="flex-1 py-3.5 rounded-xl bg-white/15 hover:bg-white/25 border border-white/20 text-white font-semibold transition"
                                    >
                                        Next: Choose System
                                    </button>
                                </div>
                            </div>
                        )}

                        {step === 2 && (
                            <div className="space-y-6">
                                <h3 className="text-white text-xl font-semibold text-center mb-6">
                                    Select Your Primary System
                                </h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {/* TMS option */}
                                    <div
                                        className={`p-6 rounded-xl border cursor-pointer transition ${formData.system === "tms"
                                            ? "border-blue-400/50 bg-blue-500/10"
                                            : "border-white/20 hover:border-white/30"
                                            }`}
                                        onClick={() => setFormData({ ...formData, system: "tms" })}
                                    >
                                        <div className="flex items-center gap-4">
                                            <div className={`p-3 rounded-lg ${formData.system === "tms" ? "bg-blue-500/20" : "bg-white/5"
                                                }`}>
                                                <span className="text-2xl">🚚</span>
                                            </div>
                                            <div>
                                                <h4 className="text-white font-semibold">TMS System</h4>
                                                <p className="text-white/60 text-sm mt-1">
                                                    Transport Management System
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                    {/* LoadBoard */}
                                    <div
                                        className={`p-6 rounded-xl border cursor-pointer transition ${formData.system === "loadboard"
                                            ? "border-amber-400/50 bg-amber-500/10"
                                            : "border-white/20 hover:border-white/30"
                                            }`}
                                        onClick={() => setFormData({ ...formData, system: "loadboard" })}
                                    >
                                        <div className="flex items-center gap-4">
                                            <div className={`p-3 rounded-lg ${formData.system === "loadboard" ? "bg-amber-500/20" : "bg-white/5"
                                                }`}>
                                                <span className="text-2xl">📊</span>
                                            </div>
                                            <div>
                                                <h4 className="text-white font-semibold">LoadBoard</h4>
                                                <p className="text-white/60 text-sm mt-1">
                                                    Load Matching Platform
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex gap-4">
                                    <button
                                        type="button"
                                        onClick={handleBack}
                                        className="flex-1 py-3.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white font-semibold transition"
                                    >
                                        Back
                                    </button>
                                    <button
                                        type="button"
                                        onClick={handleNext}
                                        className="flex-1 py-3.5 rounded-xl bg-white/15 hover:bg-white/25 border border-white/20 text-white font-semibold transition"
                                    >
                                        Next: Select Role
                                    </button>
                                </div>
                            </div>
                        )}

                        {step === 3 && (
                            <div className="space-y-6">
                                <h3 className="text-white text-xl font-semibold text-center mb-6">
                                    Select Your Role
                                </h3>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    {[
                                        { id: "shipper", label: "Shipper", icon: "📦", desc: "Ship goods" },
                                        { id: "carrier", label: "Carrier", icon: "🚛", desc: "Transport goods" },
                                        { id: "broker", label: "Broker", icon: "🤝", desc: "Connect parties" },
                                    ].map((role) => (
                                        <div
                                            key={role.id}
                                            className={`p-5 rounded-xl border cursor-pointer transition ${formData.role === role.id
                                                ? "border-white/40 bg-white/10"
                                                : "border-white/20 hover:border-white/30"
                                                }`}
                                            onClick={() => setFormData({ ...formData, role: role.id })}
                                        >
                                            <div className="text-center">
                                                <div className="text-3xl mb-3">{role.icon}</div>
                                                <h4 className="text-white font-semibold">{role.label}</h4>
                                                <p className="text-white/60 text-sm mt-1">{role.desc}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                {formData.system && (
                                    <div className="rounded-xl bg-white/5 border border-white/10 p-4">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-white/70 text-sm">Selected System:</p>
                                                <p className="text-white font-medium">
                                                    {formData.system === "tms" ? "TMS System" : "LoadBoard"}
                                                </p>
                                            </div>
                                            <div className={`px-3 py-1 rounded-full ${formData.system === "tms"
                                                ? "bg-blue-500/20 text-blue-300"
                                                : "bg-amber-500/20 text-amber-300"
                                                }`}>
                                                {formData.system === "tms" ? "🚚 TMS" : "📊 LoadBoard"}
                                            </div>
                                        </div>
                                    </div>
                                )}

                                <div className="flex gap-4">
                                    <button
                                        type="button"
                                        onClick={handleBack}
                                        className="flex-1 py-3.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white font-semibold transition"
                                    >
                                        Back
                                    </button>

                                    <button
                                        type="submit"
                                        disabled={loading}
                                        className="flex-1 py-3.5 rounded-xl bg-amber-500 hover:bg-amber-600 border border-amber-400 text-white font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {loading ? "Submitting..." : "Submit Registration"}
                                    </button>
                                </div>

                                <p className="text-white/60 text-xs mt-3">After completing registration, please check your email to verify — registration may take up to 72 hours for security checks.</p>
                            </div>
                        )}
                    </form>
                </div>
            </div>
        </div>
    );
}
