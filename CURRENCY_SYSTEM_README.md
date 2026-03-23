# EN - GTS

## EN.

## EN

### 1. EN
- 🇨🇦 **CAD** - EN)
- 🇺🇸 **USD** - EN
- 🇪🇺 **EUR** - EN
- 🇬🇧 **GBP** - EN
- 🇸🇦 **SAR** - EN
- 🇦🇪 **AED** - EN
- 🇯🇵 **JPY** - EN
- 🇨🇳 **CNY** - EN

### 2. EN
```javascript
Default Currency: CAD
Default Country: CA
```

### 3. EN localStorage

## EN

### 1. Store (EN)
📁 `frontend/src/stores/useCurrencyStore.js`
- EN

### 2. Components (EN)
📁 `frontend/src/components/admin/CurrencySelector.jsx`
- EN

📁 `frontend/src/components/CurrencySwitcher.jsx`
- EN

📁 `frontend/src/components/CurrencyDisplay.jsx`
- EN

### 3. Utilities (EN)
📁 `frontend/src/utils/currencyHelpers.js`
- EN
- Hook EN

### 4. Styles (EN)
📁 `frontend/src/components/admin/CurrencySelector.css`
- EN

## EN

### EN React:

```javascript
import { useCurrencyStore } from "../stores/useCurrencyStore";

function MyComponent() {
  const { currency, currencySymbol, formatCurrency } = useCurrencyStore();
  
  return (
    <div>
      <p>Current Currency: {currency}</p>
      <p>Price: {formatCurrency(1234.56)}</p>
    </div>
  );
}
```

### EN Component EN:

```javascript
import CurrencyDisplay from "../components/CurrencyDisplay";

function MyComponent() {
  return <CurrencyDisplay amount={1234.56} showCode={true} />;
}
```

### EN:

```javascript
import CurrencySelector from "../components/admin/CurrencySelector";

function Settings() {
  return <CurrencySelector />;
}
```

## EN

### 1. Dashboard
- ✅ EN

### 2. Platform Settings
- ✅ EN CurrencySelector EN Branding
- EN

### 3. App.jsx
- ✅ EN

## EN (Events)

### currencyChanged
EN:

```javascript
window.addEventListener("currencyChanged", (event) => {
  console.log("New currency:", event.detail.currency);
});
```

## EN. EN API EN:

```javascript
const { fetchExchangeRates } = useCurrencyStore();
await fetchExchangeRates(); // EN API EN
```

## EN

1. ✨ EN API EN
2. ✨ EN
3. ✨ EN
4. ✨ EN Backend

## EN

1. EN
2. EN **Platform Settings → Branding**
3. EN CAD EN
4. EN Dashboard
5. EN 🎉

---

**EN:** 4 EN 2026
**EN:** 1.0.0
