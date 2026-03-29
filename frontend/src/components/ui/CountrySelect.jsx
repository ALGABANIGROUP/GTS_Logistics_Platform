import React, { useEffect, useMemo, useRef, useState } from "react";
import { COUNTRIES } from "../../constants/countries";

export default function CountrySelect({
  value,
  onChange,
  invalid = false,
  countries,
  disabled = false,
}) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const containerRef = useRef(null);
  const sourceCountries = Array.isArray(countries) && countries.length > 0 ? countries : COUNTRIES;

  const options = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return sourceCountries;
    return sourceCountries.filter((c) => {
      return (
        c.name.toLowerCase().includes(q) ||
        c.iso2.toLowerCase().includes(q) ||
        c.callingCode.toLowerCase().includes(q)
      );
    });
  }, [query, sourceCountries]);

  useEffect(() => {
    const handleClick = (event) => {
      if (!containerRef.current) return;
      if (!containerRef.current.contains(event.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const label = value
    ? `${value.flag} ${value.name} (${value.callingCode})`
    : "Select country";

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        disabled={disabled}
        onClick={() => setOpen((v) => !v)}
        className="w-full rounded-xl border border-white/20 px-4 py-3 text-left text-white outline-none disabled:opacity-60 disabled:cursor-not-allowed"
        aria-invalid={invalid}
      >
        <span className="block truncate">{label}</span>
      </button>

      {open ? (
        <div className="absolute z-20 mt-2 w-full rounded-xl border border-white/20 bg-black/70 backdrop-blur-xl shadow-xl">
          <div className="p-2">
            <input
              className="w-full rounded-lg border border-white/20 bg-transparent px-3 py-2 text-white placeholder:text-white/50 outline-none"
              placeholder="Search country"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <div className="max-h-56 overflow-y-auto">
            {options.map((c) => (
              <button
                key={c.iso2}
                type="button"
                onClick={() => {
                  onChange?.(c);
                  setOpen(false);
                  setQuery("");
                }}
                className="w-full px-3 py-2 text-left text-white/90 hover:bg-white/10"
              >
                <span className="mr-2">{c.flag}</span>
                {c.name} <span className="text-white/60">({c.callingCode})</span>
              </button>
            ))}
            {options.length === 0 ? (
              <div className="px-3 py-2 text-sm text-white/60">No results</div>
            ) : null}
          </div>
        </div>
      ) : null}
    </div>
  );
}
