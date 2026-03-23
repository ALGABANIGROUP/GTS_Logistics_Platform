import { useEffect, useState } from "react";

const STORAGE_KEY = "system_selection";

const options = [
    { key: "global_transport_solutions", label: "Gabani Transport Solutions (GTS)" },
];

export default function SystemSwitcher({ className = "" }) {
    const [value, setValue] = useState(() => localStorage.getItem(STORAGE_KEY) || "global_transport_solutions");

    useEffect(() => {
        localStorage.setItem(STORAGE_KEY, value);
        window.dispatchEvent(new CustomEvent("system:switch", { detail: { system: value } }));
    }, [value]);

    return (
        <div className={`flex items-center gap-2 ${className}`}>
            <span className="text-sm text-gray-500">System</span>
            <select
                className="px-2 py-1 border rounded text-sm"
                value={value}
                onChange={(e) => setValue(e.target.value)}
            >
                {options.map((opt) => (
                    <option key={opt.key} value={opt.key}>
                        {opt.label}
                    </option>
                ))}
            </select>
        </div>
    );
}
