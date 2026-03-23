import { useState } from "react";
import { useNavigate } from "react-router-dom";
import portalBg from "../../assets/bg_login.png";

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
        // Step 2: System Selection
        system: "", // "tms" or "loadboard"
        // Step 3: Role Selection
        role: "", // "shipper", "carrier", "broker"
    });
    const [loading, setLoading] = useState(false);

    const handleNext = () => {
        if (step === 1 && validateStep1()) {
            setStep(2);
        } else if (step === 2 && formData.system) {
            setStep(3);
        }
    };

    const handleBack = () => {
        if (step > 1) {
            setStep(step - 1);
        }
    };

    const validateStep1 = () => {
        return formData.name && formData.email && formData.phone && formData.password;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            // Simulate registration API
            const userData = {
                ...formData,
                id: Date.now(),
                createdAt: new Date().toISOString(),
            };
            // Save to localStorage (temporary)
            const existingUsers = JSON.parse(localStorage.getItem("users") || "[]");
            existingUsers.push(userData);
            localStorage.setItem("users", JSON.stringify(existingUsers));
            // Save current user data
            localStorage.setItem("currentUser", JSON.stringify({
                id: userData.id,
                email: userData.email,
                name: userData.name,
                system: userData.system,
                role: userData.role,
            }));
            alert("Registration successful! Please wait up to 72 hours for security checks. You can now sign in.");
            navigate("/login?registered=true");
        } catch (error) {
            console.error("Registration error:", error);
            alert("Registration failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

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
                    <div className="rounded-2xl border border-white/20 bg-white/10 backdrop-blur-xl shadow-2xl p-8">
                        {step === 1 && (
                            <div className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <label className="block text-white/80 text-sm font-medium mb-2">
                                            Full Name *
                                        </label>
                                        <input
                                            type="text"
                                            className="w-full rounded-xl bg-white/10 border border-white/20 px-4 py-3.5 text-white placeholder:text-white/40 outline-none focus:border-white/40 transition"
                                            placeholder="John Doe"
                                            value={formData.name}
                                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-white/80 text-sm font-medium mb-2">
                                            Company *
                                        </label>
                                        <input
                                            type="text"
                                            className="w-full rounded-xl bg-white/10 border border-white/20 px-4 py-3.5 text-white placeholder:text-white/40 outline-none focus:border-white/40 transition"
                                            placeholder="Company Name"
                                            value={formData.company}
                                            onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                                            required
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-white/80 text-sm font-medium mb-2">
                                        Email Address *
                                    </label>
                                    <input
                                        type="email"
                                        className="w-full rounded-xl bg-white/10 border border-white/20 px-4 py-3.5 text-white placeholder:text-white/40 outline-none focus:border-white/40 transition"
                                        placeholder="you@company.com"
                                        value={formData.email}
                                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                        required
                                    />
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <label className="block text-white/80 text-sm font-medium mb-2">
                                            Phone Number *
                                        </label>
                                        <input
                                            type="tel"
                                            className="w-full rounded-xl bg-white/10 border border-white/20 px-4 py-3.5 text-white placeholder:text-white/40 outline-none focus:border-white/40 transition"
                                            placeholder="+1234567890"
                                            value={formData.phone}
                                            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-white/80 text-sm font-medium mb-2">
                                            Password *
                                        </label>
                                        <input
                                            type="password"
                                            className="w-full rounded-xl bg-white/10 border border-white/20 px-4 py-3.5 text-white placeholder:text-white/40 outline-none focus:border-white/40 transition"
                                            placeholder="••••••••"
                                            value={formData.password}
                                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                            required
                                        />
                                    </div>
                                </div>
                                <button
                                    type="button"
                                    onClick={handleNext}
                                    disabled={!validateStep1()}
                                    className="w-full py-3.5 rounded-xl bg-white/15 hover:bg-white/25 border border-white/20 text-white font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Next: Choose System
                                </button>
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
                                        <div className="mt-4">
                                            <ul className="text-white/70 text-sm space-y-1">
                                                <li>• Manage shipments & tracking</li>
                                                <li>• Handle documents & invoices</li>
                                                <li>• Dispatch & fleet management</li>
                                            </ul>
                                        </div>
                                    </div>
                                    {/* LoadBoard option */}
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
                                        <div className="mt-4">
                                            <ul className="text-white/70 text-sm space-y-1">
                                                <li>• Post & find loads</li>
                                                <li>• Bidding & negotiation</li>
                                                <li>• Market rates & matching</li>
                                            </ul>
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
                                        disabled={!formData.system}
                                        className="flex-1 py-3.5 rounded-xl bg-white/15 hover:bg-white/25 border border-white/20 text-white font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
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
                                {/* Selected system note */}
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
                                        type="button"
                                        onClick={handleSubmit}
                                        disabled={!formData.role || loading}
                                        className="flex-1 py-3.5 rounded-xl bg-white/15 hover:bg-white/25 border border-white/20 text-white font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {loading ? "Submitting..." : "Submit Request"}
                                    </button>
                                </div>
                            </div>
                        )}
                        {/* Back link */}
                        <div className="mt-6 text-center">
                            <button
                                onClick={() => navigate("/")}
                                className="text-white/70 hover:text-white text-sm transition"
                                type="button"
                            >
                                ← Back to Portal
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
