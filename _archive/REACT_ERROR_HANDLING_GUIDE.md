# 🔧 React Error Handling - EN

## EN

```
Objects are not valid as a React child (found: [object Object])
```

EN React EN JSX.

---

## EN

API EN Pydantic validation errors):
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "input": "notanemail"
    }
  ]
}
```

EN React EN:
```jsx
// ❌ EN
<div>{error.response.data}</div>  // EN!
```

---

## EN

### 1. EN `normalizeError()` EN

```javascript
// ✅ EN
import { normalizeError } from "../utils/dataFormatter";

try {
  const response = await axiosClient.post("/api/v1/users", data);
} catch (error) {
  const message = normalizeError(error);  // EN!
  setError(message);
}
```

### 2. EN `SafeErrorDisplay` EN

```jsx
import { SafeErrorDisplay } from "../components/SafeDisplay";

function MyComponent() {
  const [error, setError] = useState(null);

  return (
    <>
      {/* ✅ EN */}
      {error && (
        <SafeErrorDisplay 
          error={error}
          onDismiss={() => setError(null)}
        />
      )}
    </>
  );
}
```

### 3. EN `EnhancedErrorBoundary` EN App.jsx

```jsx
import EnhancedErrorBoundary from "./components/EnhancedErrorBoundary";

function App() {
  return (
    <EnhancedErrorBoundary>
      <YourApp />
    </EnhancedErrorBoundary>
  );
}
```

---

## EN

### 1. `frontend/src/utils/dataFormatter.js`
EN.

**EN:**
- `formatErrorMessage(error)` - EN
- `normalizeError(error)` - EN
- `handleAxiosError(error)` - EN Axios
- `safeRenderData(data)` - EN

### 2. `frontend/src/components/SafeDisplay.jsx`
EN React EN.

**EN:**
- `<SafeErrorDisplay />` - EN
- `<SafeSuccessDisplay />` - EN
- `<SafeDataDisplay />` - EN

### 3. `frontend/src/components/EnhancedErrorBoundary.jsx`
EN.

**EN:**
- EN Sentry (EN

---

## EN

### EN 1: EN Promise

```javascript
// ❌ EN
.catch(error => setError(error.response.data))

// ✅ EN
.catch(error => setError(normalizeError(error)))
```

### EN 2: EN Validation Error EN Pydantic

```javascript
try {
  await axiosClient.post("/users", formData);
} catch (error) {
  if (error.response?.status === 422) {
    const details = error.response.data?.detail;  // EN
    if (Array.isArray(details)) {
      details.forEach(err => {
        const field = err.loc[1];
        const message = err.msg;
        setFieldError(field, message);  // EN
      });
    }
  }
}
```

### EN 3: EN JSX

```jsx
function LoginForm() {
  const [error, setError] = useState(null);

  return (
    <>
      {/* ✅ EN "Objects are not valid..." */}
      {error && <SafeErrorDisplay error={error} />}
      
      {/* ❌ EN */}
      {/* {error && <div>{error}</div>} */}
    </>
  );
}
```

---

## EN

### EN normalizeError()
- EN: Axios errors, Error objects, Objects, Arrays, Strings
- EN Pydantic validation errors
- EN

### EN SafeErrorDisplay
- EN JSX
- EN

### EN EnhancedErrorBoundary
- EN React EN crash EN development mode

---

## EN:

- [ ] EN `error.response.data` EN `normalizeError(error)`
- [ ] EN `<SafeErrorDisplay />` EN
- [ ] EN `<EnhancedErrorBoundary />` EN App.jsx
- [ ] EN
- [ ] EN validation errors EN
- [ ] EN

---

## EN:

1. EN console EN
2. EN `normalizeError()` EN
3. EN `<SafeErrorDisplay />` EN
4. EN: support@gts-logistics.com

---

**EN! ✅**
