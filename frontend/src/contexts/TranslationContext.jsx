import React, { createContext, useContext, useEffect, useState } from "react";

const DICTS = {
    en: {
        greeting: "Hello, {name}!",
        farewell: "Goodbye, {name}!",
        welcome: "Welcome to Gabani Transport Solutions (GTS)",
        dashboard: "Dashboard",
        settings: "Settings",
        notifications: "Notifications",
        language: "Language",
        theme: "Theme",
        timezone: "Timezone",
        "theme.dark": "Dark",
        "theme.light": "Light",
        "theme.auto": "Auto",
        "dashboard.default": "Default Layout",
        "dashboard.compact": "Compact Layout",
        "dashboard.detailed": "Detailed Layout",
        "dashboard.minimal": "Minimal Layout",
        "dashboard.default_desc": "Balanced view with essential widgets",
        "dashboard.compact_desc": "Space-efficient layout for quick overview",
        "dashboard.detailed_desc": "Comprehensive view with all available data",
        "dashboard.minimal_desc": "Minimal interface focusing on key metrics",
    }
};

const AVAILABLE_LANGUAGES = ["en"];

const isLanguageActive = (lang) => {
    return AVAILABLE_LANGUAGES.includes(lang) && DICTS[lang] !== undefined;
};

const TranslationContext = createContext();

export function TranslationProvider({ children }) {
    const [currentLang, setCurrentLang] = useState(() => {
        return localStorage.getItem("gts_language") || "en";
    });

    useEffect(() => {
        localStorage.setItem("gts_language", currentLang);
    }, [currentLang]);

    const setLang = (lang) => {
        if (isLanguageActive(lang)) {
            setCurrentLang(lang);
        }
    };

    const t = (key, params = {}) => {
        const dict = DICTS[currentLang] || DICTS.en;
        let value = dict[key];

        if (value === undefined) {
            value = DICTS.en[key] || key;
        }

        if (typeof value === "string" && params && Object.keys(params).length) {
            for (const [p, v] of Object.entries(params)) {
                value = value.replaceAll(`{${p}}`, String(v));
            }
        }

        return value;
    };

    return (
        <TranslationContext.Provider
            value={{
                t,
                currentLang,
                setLang,
                availableLanguages: AVAILABLE_LANGUAGES
            }}
        >
            {children}
        </TranslationContext.Provider>
    );
}

export function useTranslation() {
    const context = useContext(TranslationContext);

    if (!context) {
        throw new Error("useTranslation must be used within TranslationProvider");
    }

    return context;
}

// ============================================================================
// ASYNC HELPER - Add at the top with imports
// ============================================================================