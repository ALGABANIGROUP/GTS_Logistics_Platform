export const COUNTRIES = [
  { code: "US", iso2: "US", name: "United States", callingCode: "+1", flag: "🇺🇸" },
  { code: "CA", iso2: "CA", name: "Canada", callingCode: "+1", flag: "🇨🇦" },
  { code: "MX", iso2: "MX", name: "Mexico", callingCode: "+52", flag: "🇲🇽" },
  { code: "GB", iso2: "GB", name: "United Kingdom", callingCode: "+44", flag: "🇬🇧" },
  { code: "IE", iso2: "IE", name: "Ireland", callingCode: "+353", flag: "🇮🇪" },
  { code: "FR", iso2: "FR", name: "France", callingCode: "+33", flag: "🇫🇷" },
  { code: "DE", iso2: "DE", name: "Germany", callingCode: "+49", flag: "🇩🇪" },
  { code: "ES", iso2: "ES", name: "Spain", callingCode: "+34", flag: "🇪🇸" },
  { code: "IT", iso2: "IT", name: "Italy", callingCode: "+39", flag: "🇮🇹" },
  { code: "NL", iso2: "NL", name: "Netherlands", callingCode: "+31", flag: "🇳🇱" },
  { code: "BE", iso2: "BE", name: "Belgium", callingCode: "+32", flag: "🇧🇪" },
  { code: "CH", iso2: "CH", name: "Switzerland", callingCode: "+41", flag: "🇨🇭" },
  { code: "SE", iso2: "SE", name: "Sweden", callingCode: "+46", flag: "🇸🇪" },
  { code: "NO", iso2: "NO", name: "Norway", callingCode: "+47", flag: "🇳🇴" },
  { code: "DK", iso2: "DK", name: "Denmark", callingCode: "+45", flag: "🇩🇰" },
  { code: "TR", iso2: "TR", name: "Turkey", callingCode: "+90", flag: "🇹🇷" },
  { code: "RU", iso2: "RU", name: "Russia", callingCode: "+7", flag: "🇷🇺" },
  { code: "IN", iso2: "IN", name: "India", callingCode: "+91", flag: "🇮🇳" },
  { code: "PK", iso2: "PK", name: "Pakistan", callingCode: "+92", flag: "🇵🇰" },
  { code: "BD", iso2: "BD", name: "Bangladesh", callingCode: "+880", flag: "🇧🇩" },
  { code: "CN", iso2: "CN", name: "China", callingCode: "+86", flag: "🇨🇳" },
  { code: "JP", iso2: "JP", name: "Japan", callingCode: "+81", flag: "🇯🇵" },
  { code: "KR", iso2: "KR", name: "South Korea", callingCode: "+82", flag: "🇰🇷" },
  { code: "SG", iso2: "SG", name: "Singapore", callingCode: "+65", flag: "🇸🇬" },
  { code: "AU", iso2: "AU", name: "Australia", callingCode: "+61", flag: "🇦🇺" },
  { code: "NZ", iso2: "NZ", name: "New Zealand", callingCode: "+64", flag: "🇳🇿" },
  { code: "SA", iso2: "SA", name: "Saudi Arabia", callingCode: "+966", flag: "🇸🇦" },
  { code: "AE", iso2: "AE", name: "United Arab Emirates", callingCode: "+971", flag: "🇦🇪" },
  { code: "QA", iso2: "QA", name: "Qatar", callingCode: "+974", flag: "🇶🇦" },
  { code: "KW", iso2: "KW", name: "Kuwait", callingCode: "+965", flag: "🇰🇼" },
  { code: "OM", iso2: "OM", name: "Oman", callingCode: "+968", flag: "🇴🇲" },
  { code: "BH", iso2: "BH", name: "Bahrain", callingCode: "+973", flag: "🇧🇭" },
  { code: "EG", iso2: "EG", name: "Egypt", callingCode: "+20", flag: "🇪🇬" },
  { code: "SD", iso2: "SD", name: "Sudan", callingCode: "+249", flag: "🇸🇩" },
  { code: "ZA", iso2: "ZA", name: "South Africa", callingCode: "+27", flag: "🇿🇦" },
  { code: "NG", iso2: "NG", name: "Nigeria", callingCode: "+234", flag: "🇳🇬" },
  { code: "KE", iso2: "KE", name: "Kenya", callingCode: "+254", flag: "🇰🇪" },
  { code: "BR", iso2: "BR", name: "Brazil", callingCode: "+55", flag: "🇧🇷" },
  { code: "AR", iso2: "AR", name: "Argentina", callingCode: "+54", flag: "🇦🇷" },
  { code: "CL", iso2: "CL", name: "Chile", callingCode: "+56", flag: "🇨🇱" },
];

const PLACEHOLDER = { code: "SELECT_PLACEHOLDER", name: "Select a Country", iso2: "", callingCode: "", flag: "" };

export const COUNTRIES_TMS = [
  PLACEHOLDER,
  ...COUNTRIES.filter(c => c.code && c.code !== "")
];

export const COUNTRIES_LOADBOARD = [
  PLACEHOLDER,
  ...COUNTRIES.filter(c => ["US", "CA"].includes(c.iso2))
];
