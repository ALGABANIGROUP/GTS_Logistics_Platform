# Midnight Navy Glass - Color Scheme Documentation

## 🎨 Color System: Smoked Glass Navy

**Base Color Name:** Midnight Navy / Deep Navy / Smoked Glass Navy  
**Hex Value:** `#111B2C`  
**Perception:** Dark Navy Blue with subtle depth, smoky translucent glass effect

---

## CSS Custom Properties (Tokens)

### Base Token
```css
--glass-navy-base: #111B2C;
```

### Opacity Overlays (Frosted Glass)
```css
--glass-navy-950: rgba(17, 27, 44, 0.97);  /* Nearly opaque - main panels */
--glass-navy-900: rgba(17, 27, 44, 0.95);  /* Primary glass - headers, footers */
--glass-navy-800: rgba(17, 27, 44, 0.80);  /* Medium glass - navigation */
--glass-navy-700: rgba(17, 27, 44, 0.70);  /* Lighter glass - hover states */
--glass-navy-600: rgba(17, 27, 44, 0.60);  /* Transparent glass - cards */
--glass-navy-500: rgba(17, 27, 44, 0.50);  /* Half-transparent - buttons */
--glass-navy-400: rgba(17, 27, 44, 0.40);  /* Subtle overlay - controls */
--glass-navy-300: rgba(17, 27, 44, 0.30);  /* Minimal overlay - accents */
```

### Supporting Tokens
```css
--glass-border: rgba(148, 163, 184, 0.22);    /* Subtle separation lines */
--glass-highlight: rgba(255, 255, 255, 0.05); /* Shine effect (optional) */
--glass-shadow: rgba(0, 0, 0, 0.30);          /* Depth shadows */
```

### Naming Aliases
```css
--glass-midnight: var(--glass-navy-base);
--glass-navy: var(--glass-navy-base);
--smoked-glass-navy: var(--glass-navy-base);
```

---

## Usage Patterns

### Main Background
```css
background: linear-gradient(135deg, var(--glass-navy-900) 0%, rgba(17, 27, 44, 0.90) 50%, var(--glass-navy-900) 100%);
```
**Effect:** Subtle gradient with center slightly lighter for depth

### Primary Panels (Headers, Footers, Main Content)
```css
background: linear-gradient(135deg, var(--glass-navy-900) 0%, var(--glass-navy-800) 100%);
backdrop-filter: blur(20px);
border: 1px solid var(--glass-border);
box-shadow: 0 20px 40px var(--glass-shadow);
```

### Navigation Tabs
```css
/* Container */
background: linear-gradient(135deg, var(--glass-navy-800) 0%, var(--glass-navy-800) 100%);

/* Tab Buttons (inactive) */
background: var(--glass-navy-500);

/* Tab Buttons (hover) */
background: var(--glass-navy-700);

/* Tab Buttons (active) */
background: linear-gradient(135deg, var(--glass-navy-900) 0%, var(--glass-navy-700) 100%);
```

### Cards & Control Panels
```css
background: var(--glass-navy-600);
border: 1px solid var(--glass-border);
backdrop-filter: blur(10px);
```

### Interactive Elements (Select, Buttons)
```css
/* Default state */
background: var(--glass-navy-600);

/* Hover state */
background: var(--glass-navy-700);
```

### Results & Data Panels
```css
/* Container */
background: var(--glass-navy-900);

/* Table headers */
background: var(--glass-navy-500);

/* Code blocks */
background: var(--glass-navy-500);
```

---

## Color Psychology & Design Intent

### Visual Properties
- **Hue:** Navy blue (deep, professional, trustworthy)
- **Saturation:** Low (muted, sophisticated)
- **Lightness:** Very dark (elegant, modern)
- **Transparency:** Variable (frosted glass effect)

### Perception
- **English:** Midnight Navy, Deep Navy, Smoked Glass
- **Arabic:** Dark Navy / Smoked Navy
- **Emotional:** Professional, sophisticated, calm, trustworthy
- **Industry fit:** Logistics, enterprise, finance, tech

### Contrast Strategy
- **Text on navy-900:** #e2e8f0 (light slate-100) - excellent contrast (WCAG AAA)
- **Text on navy-600:** #e2e8f0 (light slate-100) - good contrast (WCAG AA+)
- **Borders:** rgba(148, 163, 184, 0.22) - subtle but visible
- **Accents:** Bright colors (blue #3B82F6, green #4CAF50) pop against navy

---

## Component Mapping

| Component | Token | Opacity | Blur |
|-----------|-------|---------|------|
| Main background | `navy-900` | 95% | - |
| Header/Footer | `navy-900` | 95% | 20px |
| Navigation bar | `navy-800` | 80% | 20px |
| Tab buttons (inactive) | `navy-500` | 50% | 10px |
| Tab buttons (hover) | `navy-700` | 70% | 10px |
| Tab buttons (active) | `navy-900` gradient | 95%→70% | - |
| Content panels | `navy-900` | 95% | 20px |
| Control sections | `navy-400` | 40% | 10px |
| Cards (prediction, report) | `navy-600` | 60% | 10px |
| Select inputs | `navy-600` | 60% | 10px |
| Results panel | `navy-900` | 95% | 20px |
| Table headers | `navy-500` | 50% | - |
| Code blocks | `navy-500` | 50% | - |
| Footer buttons | `navy-500` | 50% | 10px |

---

## Browser Compatibility

### Backdrop Filter Support
- ✅ Chrome 76+
- ✅ Firefox 103+
- ✅ Safari 9+ (with -webkit- prefix)
- ✅ Edge 79+
- ⚠️ Older browsers: Degrades to solid background

### Fallback Strategy
If `backdrop-filter` not supported, the solid `rgba()` background provides sufficient opacity for readability.

---

## Comparison: Slate vs. Navy

### Previous (Slate Glass)
```css
#0f172a  /* slate-950 */
#1e293b  /* slate-900 */
#334155  /* slate-800 */
```
- Cooler tone, slightly purple/gray tint
- Less saturated blue

### Current (Navy Glass)
```css
#111B2C  /* glass-navy-base */
rgba(17, 27, 44, 0.95)  /* navy-900 */
rgba(17, 27, 44, 0.60)  /* navy-600 */
```
- Warmer navy blue tone
- Richer, more saturated blue
- Closer to "midnight navy" / "smoked glass" aesthetic

**RGB Breakdown:**
- R: 17 (very dark)
- G: 27 (slightly lighter)
- B: 44 (dominant blue channel)
- Ratio: 1 : 1.6 : 2.6 (blue-dominant)

---

## Design System Naming

### For Design Tokens
```
glass-midnight-950
glass-midnight-900
glass-midnight-800
...
glass-midnight-300
```

### For Figma/Sketch
```
Colors/Glass/Navy/950
Colors/Glass/Navy/900
Colors/Glass/Navy/600
...
```

### For Documentation
```
Midnight Navy (Primary)
Deep Navy Glass (Alternate)
Smoked Glass Navy (Descriptive)
```

---

## Quick Reference Card

```css
/* Primary background gradient */
background: linear-gradient(135deg, 
    var(--glass-navy-900) 0%, 
    rgba(17, 27, 44, 0.90) 50%, 
    var(--glass-navy-900) 100%
);

/* Panel/Card */
background: var(--glass-navy-600);
border: 1px solid var(--glass-border);
backdrop-filter: blur(10px);

/* Button/Interactive */
background: var(--glass-navy-500);
color: #cbd5e1;

/* Button hover */
background: var(--glass-navy-700);
color: #f1f5f9;

/* Text primary */
color: #e2e8f0;

/* Text secondary */
color: #cbd5e1;
```

---

## Implementation Files

**Updated:** `frontend/src/components/bots/MapleLoadCanadaControl.css`
- Line 5-24: CSS custom properties (tokens)
- All components: Converted from slate to navy tokens

**Backup:** `frontend/src/components/bots/MapleLoadCanadaControl.css.backup` (slate version)

---

## Visual Verification

To verify the midnight navy glass effect is applied:

1. Open `http://127.0.0.1:5174/ai-bots/mapleload-canada`
2. Inspect any panel/card background in DevTools
3. Check computed style for `background` - should show `rgba(17, 27, 44, ...)`
4. Verify `backdrop-filter: blur(...)` is active
5. Compare to attached screenshot - should match dark navy tone

---

**Last Updated:** January 8, 2026  
**Version:** 1.0 Midnight Navy Glass  
**Color Code:** `#111B2C` Dark Navy
