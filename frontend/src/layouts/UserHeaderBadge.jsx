// frontend/src/layouts/UserHeaderBadge.jsx
import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
    Settings as SettingsIcon,
    User as UserIcon,
    LogOut as LogOutIcon,
    Moon as MoonIcon,
    Sun as SunIcon,
    Bell as BellIcon,
    Mic as MicIcon,
} from "lucide-react";
import { useAuth } from "../contexts/AuthContext.jsx";
import { getUserRole } from "../utils/userRole";

const formatRoleLabel = (role) => {
    const normalized = String(role || "").trim().toLowerCase();
    if (!normalized) return "User";
    if (normalized === "super_admin") return "Super Admin";
    if (normalized === "admin") return "Admin";
    if (normalized === "owner") return "Owner";
    return normalized.replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
};

const resolveRoleBadgeLabel = (role, userType) => {
    const normalizedRole = String(role || "").trim().toLowerCase();
    const normalizedUserType = String(userType || "").trim();

    // If backend role is the generic "user", show the business account type instead.
    if (normalizedRole === "user" && normalizedUserType) {
        return normalizedUserType;
    }

    return formatRoleLabel(role);
};

const UserHeaderBadge = () => {
    const navigate = useNavigate();
    const menuRef = useRef(null);
    const { user, logout } = useAuth();

    // ====== Basic profile / session ======
    const stored = typeof window !== "undefined"
        ? localStorage.getItem("gts_user_profile")
        : null;
    const storedUserRaw = typeof window !== "undefined"
        ? window.sessionStorage.getItem("user")
        : null;

    let profile = {};
    try {
        profile = stored ? JSON.parse(stored) : {};
    } catch {
        profile = {};
    }
    let storedUser = null;
    if (storedUserRaw) {
        try {
            storedUser = JSON.parse(storedUserRaw);
        } catch {
            storedUser = null;
        }
    }

    const roleSource = user || storedUser || profile;
    const fullName =
        user?.full_name ||
        user?.fullName ||
        user?.name ||
        storedUser?.full_name ||
        storedUser?.fullName ||
        storedUser?.name ||
        profile.fullName ||
        profile.name ||
        storedUser?.email ||
        profile.email ||
        "Guest User";
    const country =
        user?.country ||
        storedUser?.country ||
        profile.country ||
        "Unknown";
    const userType =
        user?.user_type ||
        user?.userType ||
        storedUser?.user_type ||
        storedUser?.userType ||
        profile.userType ||
        "Logistics User";
    const role = getUserRole(roleSource) || "user";
    const roleLabel = resolveRoleBadgeLabel(role, userType);

    const initials = fullName
        .split(" ")
        .filter(Boolean)
        .map((p) => p[0].toUpperCase())
        .slice(0, 2)
        .join("");

    // ====== UI / dropdown state ======
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    // Online / offline indicator
    const [isOnline, setIsOnline] = useState(
        typeof navigator !== "undefined" ? navigator.onLine : true
    );

    // Theme (light / dark)
    const [theme, setTheme] = useState(
        typeof window !== "undefined"
            ? localStorage.getItem("theme") || "dark"
            : "dark"
    );

    // Notifications count
    const [notifications, setNotifications] = useState(0);

    // Voice command
    const [isListening, setIsListening] = useState(false);

    // Real-time clock
    const [currentTime, setCurrentTime] = useState(new Date());

    // Gamification
    const [userPoints, setUserPoints] = useState(0);
    const userLevel = Math.floor(userPoints / 500) + 1;

    // AI suggestions (live only)
    const [suggestions, setSuggestions] = useState([]);

    // Fleet quick stats (live only)
    const [fleetStats, setFleetStats] = useState({
        totalVehicles: 0,
        activeDrivers: 0,
        pendingMaintenance: 0,
    });

    const quickActions = [
        { icon: "📊", label: "Dashboard", onClick: () => navigate("/dashboard") },
        { icon: "🚚", label: "Shipments", onClick: () => navigate("/shipments") },
        { icon: "📁", label: "Documents", onClick: () => navigate("/documents") },
        { icon: "💰", label: "Finance", onClick: () => navigate("/finance") },
        { icon: "🤖", label: "AI Bots", onClick: () => navigate("/ai-bots") },
        { icon: "⚙️", label: "Settings", onClick: () => navigate("/settings") },
    ];

    // ====== Effects ======

    // Online / offline listeners
    useEffect(() => {
        const handleOnline = () => setIsOnline(true);
        const handleOffline = () => setIsOnline(false);

        window.addEventListener("online", handleOnline);
        window.addEventListener("offline", handleOffline);

        return () => {
            window.removeEventListener("online", handleOnline);
            window.removeEventListener("offline", handleOffline);
        };
    }, []);

    // Theme init / sync
    useEffect(() => {
        if (typeof document === "undefined") return;
        document.documentElement.setAttribute('data-theme', theme);
    }, [theme]);

    // Clock
    useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    // Suggestions are provided by live backend only

    // Close menu when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (menuRef.current && !menuRef.current.contains(event.target)) {
                setIsMenuOpen(false);
            }
        };

        if (isMenuOpen) {
            document.addEventListener("mousedown", handleClickOutside);
        } else {
            document.removeEventListener("mousedown", handleClickOutside);
        }

        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [isMenuOpen]);

    // ====== Handlers ======

    const handleLogout = async () => {
        try {
            await logout?.();
        } finally {
            if (typeof window !== "undefined") {
                localStorage.removeItem("gts_user_profile");
            }
            navigate("/login");
        }
    };

    const toggleTheme = () => {
        const newTheme = theme === "light" ? "dark" : "light";
        setTheme(newTheme);
        localStorage.setItem("theme", newTheme);
        if (typeof document !== "undefined") {
            document.documentElement.setAttribute('data-theme', newTheme);
        }
    };

    const handleVoiceCommand = (command) => {
        const cmd = command.toLowerCase();

        if (cmd.includes("logout") || cmd.includes("sign out")) {
            handleLogout();
        }
        if (cmd.includes("settings")) {
            navigate("/settings");
        }
        if (cmd.includes("dashboard")) {
            navigate("/dashboard");
        }
        if (cmd.includes("shipments")) {
            navigate("/shipments");
        }
    };

    const startVoiceCommand = () => {
        if (typeof window === "undefined") return;

        const SpeechRecognition =
            window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            // Browser not supported
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.lang = "en-US";

        recognition.onstart = () => setIsListening(true);
        recognition.onend = () => setIsListening(false);

        recognition.onresult = (event) => {
            const command = event.results[0][0].transcript;
            handleVoiceCommand(command);
        };

        recognition.start();
    };

    // ====== Render ======

    return (
        <div className="relative" ref={menuRef}>
            <div className="flex items-center gap-4">
                {/* Real-time time display */}
                <div className="hidden md:flex flex-col items-end mr-2">
                    <span className="text-xs text-slate-400">
                        {currentTime.toLocaleTimeString()}
                    </span>
                    <span className="text-[11px] text-slate-500">
                        {isOnline ? "Online" : "Offline"}
                    </span>
                </div>

                {/* Voice button */}
                <button
                    type="button"
                    onClick={startVoiceCommand}
                    className={`hidden sm:flex items-center justify-center h-8 w-8 rounded-full border border-slate-700/80 bg-slate-900/80 hover:bg-slate-800 transition-all ${isListening ? "ring-2 ring-emerald-500" : ""
                        }`}
                    title="Voice commands"
                >
                    <MicIcon className="h-4 w-4 text-slate-200" />
                </button>

                {/* Notification bell */}
                <button
                    type="button"
                    className="relative flex items-center justify-center h-9 w-9 rounded-full border border-slate-700/80 bg-slate-900/80 hover:bg-slate-800 transition-all"
                >
                    <BellIcon className="h-4 w-4 text-slate-100" />
                    {notifications > 0 && (
                        <div className="absolute -top-1 -right-1 h-4 min-w-[16px] px-1 bg-red-500 rounded-full flex items-center justify-center text-[10px] text-white font-bold animate-pulse">
                            {notifications > 9 ? "9+" : notifications}
                        </div>
                    )}
                </button>

                {/* Avatar + online dot + click to open menu */}
                <button
                    type="button"
                    onClick={() => setIsMenuOpen((v) => !v)}
                    className="relative flex items-center gap-3"
                >
                    <div className="relative">
                        <div className="h-9 w-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-sm font-semibold text-white shadow-lg transition-all duration-300 hover:scale-110 hover:rotate-6 cursor-pointer">
                            {initials}
                        </div>

                        {/* Online dot */}
                        <div
                            className={`absolute -bottom-1 -right-1 h-3 w-3 rounded-full border-2 border-slate-900 ${isOnline ? "bg-emerald-400" : "bg-slate-500"
                                }`}
                        />
                    </div>

                    {/* Basic info (shown even if dropdown is closed) */}
                    <div className="hidden sm:flex flex-col items-start leading-tight">
                        <div className="flex items-center gap-2">
                            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-100 uppercase tracking-wide">
                                {roleLabel}
                            </span>
                            <span className="px-2 py-0.5 bg-amber-400 text-amber-900 text-[11px] rounded-full font-semibold">
                                ⭐ Level {userLevel}
                            </span>
                        </div>

                        <div className="flex items-center gap-2">
                            <span className="text-sm font-semibold text-slate-100">
                                {fullName}
                            </span>
                        </div>

                        <div className="text-xs text-slate-400">
                            {userType} • {country}
                        </div>
                    </div>
                </button>
            </div>

            {/* ===== Dropdown Menu ===== */}
            {isMenuOpen && (
                <div className="absolute right-0 mt-3 w-80 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl z-50 overflow-hidden">
                    {/* Header */}
                    <div className="px-4 py-3 border-b border-slate-700/70 bg-slate-900/90 flex items-center justify-between">
                        <div>
                            <p className="text-sm font-semibold text-slate-50">{fullName}</p>
                            <p className="text-xs text-slate-400">
                                {userType} • {country}
                            </p>
                            <p className="text-[11px] text-slate-500">
                                Points: {userPoints} • Level {userLevel}
                            </p>
                        </div>
                        <div className="text-right text-[11px] text-slate-500">
                            <div>Vehicles: {fleetStats.totalVehicles}</div>
                            <div>Active drivers: {fleetStats.activeDrivers}</div>
                            <div>Maintenance: {fleetStats.pendingMaintenance}</div>
                        </div>
                    </div>

                    {/* Main actions */}
                    <div className="py-2">
                        <button
                            className="w-full flex items-center gap-2 px-4 py-2 text-sm text-slate-100 hover:bg-slate-800/80 transition"
                            onClick={() => navigate("/settings")}
                        >
                            <SettingsIcon size={16} className="text-slate-300" />
                            Settings
                        </button>

                        <button
                            className="w-full flex items-center gap-2 px-4 py-2 text-sm text-slate-100 hover:bg-slate-800/80 transition"
                            onClick={() => navigate("/profile")}
                        >
                            <UserIcon size={16} className="text-slate-300" />
                            Profile
                        </button>

                        <button
                            onClick={toggleTheme}
                            className="w-full flex items-center gap-2 px-4 py-2 text-sm text-slate-100 hover:bg-slate-800/80 transition"
                        >
                            {theme === "light" ? (
                                <MoonIcon size={16} className="text-slate-300" />
                            ) : (
                                <SunIcon size={16} className="text-slate-300" />
                            )}
                            {theme === "light" ? "Switch to dark mode" : "Switch to light mode"}
                        </button>

                        <button
                            onClick={handleLogout}
                            className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-400 hover:bg-red-950/40 transition"
                        >
                            <LogOutIcon size={16} />
                            Logout
                        </button>
                    </div>

                    {/* Quick actions grid */}
                    <div className="grid grid-cols-3 gap-2 p-3 border-t border-slate-700/70 bg-slate-950/60">
                        {quickActions.map((action, index) => (
                            <button
                                key={index}
                                onClick={action.onClick}
                                className="flex flex-col items-center p-2 rounded-lg hover:bg-slate-800/80 transition"
                            >
                                <span className="text-lg mb-1">{action.icon}</span>
                                <span className="text-[11px] text-slate-200 text-center">
                                    {action.label}
                                </span>
                            </button>
                        ))}
                    </div>

                    {/* AI suggestions */}
                    {suggestions.length > 0 && (
                        <div className="border-t border-slate-700/70 px-4 py-3 bg-slate-900/90">
                            <p className="text-xs font-semibold text-slate-400 mb-2">
                                Smart suggestions
                            </p>
                            {suggestions.map((suggestion, index) => (
                                <div
                                    key={index}
                                    className="text-xs text-slate-300 mb-1 flex items-start gap-2"
                                >
                                    <span className="text-emerald-400 mt-0.5">•</span>
                                    {suggestion}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default UserHeaderBadge;
