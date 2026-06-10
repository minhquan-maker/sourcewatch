# SourceWatch — Design Specification

## Design Philosophy

**"Investigation meets clarity."** — SourceWatch feels like a digital forensics lab. Dark, focused, precise. Every element communicates trust and authority. The UI should feel like a tool built by journalists for journalists — serious but accessible.

Based on: VANGUARD agency aesthetics + securify SaaS data density + modern dark-mode dashboard patterns.

---

## Color System

### Palette (OKLCH / Hex equivalents)

```css
/* Core */
--color-bg:           #080b12;   /* Deep dark navy-black */
--color-surface:      #0f1520;   /* Card/panel background */
--color-surface-alt:  #161d2e;   /* Elevated surface */
--color-border:       #1e2a3d;   /* Subtle borders */
--color-border-light: #2a3a52;   /* Visible borders */

/* Text */
--color-text-primary:   #f0f4f8;  /* Near-white */
--color-text-secondary: #94a3b8;  /* Muted text */
--color-text-tertiary: #64748b;   /* Disabled/placeholder */

/* Accent — Electric Cyan (trust, investigation) */
--color-accent:        #22d3ee; /* Primary accent */
--color-accent-dim:   #0e7490;   /* Dimmed accent */
--color-accent-glow:  rgba(34, 211, 238, 0.15); /* Glow effect */

/* Semantic */
--color-verified:   #22c55e;  /* Green — verified claims */
--color-disputed:   #f59e0b;  /* Amber — disputed */
--color-false:      #ef4444;  /* Red — false claims */
--color-unverified:#94a3b8;  /* Gray — unverified */

/* Score gradient */
--color-score-high:   #22c55e;  /* 7-10 */
--color-score-mid:     #f59e0b;  /* 4-6 */
--color-score-low:     #ef4444;  /* 0-3 */

/* Graph nodes */
--color-node-trustworthy: #22d3ee;  /* High trust sources */
--color-node-neutral:    #64748b;  /* Medium trust */
--color-node-untrusted:  #ef4444;  /* Low trust / fake news */

/* Graph edges */
--color-edge-origin:    #22d3ee;  /* Origin connection */
--color-edge-copy:      #f59e0b;  /* Copy connection */
--color-edge-amplify:   #ef4444;  /* Amplify connection */
```

### Typography

```css
/* Display — Headlines, brand name */
font-family: 'Syne', sans-serif;       /* Geometric, bold, distinctive */
font-weight: 700-800;

/* Body — UI text, descriptions */
font-family: 'DM Sans', sans-serif;   /* Clean, modern, readable */
font-weight: 400-500;

/* Mono — Scores, timestamps, technical data */
font-family: 'JetBrains Mono', monospace;
font-weight: 400-500;
```

**Font sizes (using clamp for fluid typography):**

| Token | Mobile | Desktop | Use |
|-------|--------|---------|-----|
| `text-display` | `clamp(2.5rem, 8vw, 5rem)` | — | Hero title |
| `text-heading` | `clamp(1.5rem, 4vw, 2.5rem)` | — | Section headings |
| `text-title` | `1.25rem` | `1.5rem` | Card titles |
| `text-body` | `0.875rem` | `1rem` | Body text |
| `text-small` | `0.75rem` | `0.875rem` | Labels, captions |
| `text-micro` | `0.625rem` | `0.75rem` | Badges, timestamps |
| `text-score` | `clamp(3rem, 10vw, 6rem)` | — | Credibility score number |

**Letter-spacing:**

```css
--tracking-tight:  -0.04em;  /* Display headings */
--tracking-normal:  0em;     /* Body text */
--tracking-wide:     0.08em;  /* Labels */
--tracking-widest: 0.15em;  /* Badges, uppercase labels */
```

---

## Layout System

### Grid

```
Full-width container, max-width: 1280px, centered
Gutters: 16px (mobile) / 24px (tablet) / 32px (desktop)
Sections separated by 48px (mobile) / 80px (desktop)
```

### Viewport Sections

```
┌─────────────────────────────────────────────────────┐
│  NAVBAR (sticky, backdrop-blur, z-50)                │
│  Logo left | Nav links center | CTA right           │
├─────────────────────────────────────────────────────┤
│                                                     │
│  HERO SECTION (100vh) │
│  ┌─────────────────────────────────────────────┐   │
│  │  SourceWatch brand (top-left)               │   │
│  │ │   │
│  │  [ Giant headline + tagline ] │   │
│  │                                             │   │
│  │ ┌─────────────────────────────────────┐   │   │
│  │  │  🔍 Paste a news link... [Analyze] │   │   │
│  │  └─────────────────────────────────────┘   │   │
│  │                                             │   │
│  │  [ Stats row: articles analyzed, sources ] │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  RESULTS SECTION (appears after analysis)          │
│                                                     │
│  ┌──────────────┐  ┌──────────────────────────┐   │
│  │              │  │                          │   │
│  │  SCORE CARD  │  │  PROPAGATION TIMELINE     │   │
│  │  (left)      │  │  (right, scrollable)      │   │
│  │              │  │                          │   │
│  └──────────────┘  └──────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  SOURCE NETWORK GRAPH (D3.js, full-width)  │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  CLAIMS + FACT-CHECK BADGES (cards grid)   │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
├─────────────────────────────────────────────────────┤
│  FOOTER (minimal)                                  │
└─────────────────────────────────────────────────────┘
```

### Responsive Breakpoints

| Breakpoint | Width | Layout changes |
|------------|-------|----------------|
| Mobile | `< 640px` | Single column, stacked |
| Tablet | `640px - 1024px` | 2-column grid |
| Desktop | `> 1024px` | Full layout, side-by-side |

---

## Component Specifications

### Navbar

```
Height: 64px (mobile) / 72px (desktop)
Background: bg-bg/80 backdrop-blur-lg
Border-bottom: 1px solid border-color
Position: sticky top-0 z-50

Left: "SourceWatch" in Syne Bold, text-accent, tracking-widest
Center (md+): Nav links — "How it works", "About", "GitHub"
Right: "Analyze" CTA button

Mobile: hamburger icon, fullscreen overlay menu
```

### Hero Section

```
Height: 100vh, bg-bg
Content: vertically centered, left-aligned

Top-left badge: "🔍 Vietnamese News Verifier" — micro text, tracking-widest, text-text-secondary

Headline: "Know the source.\nKnow the truth."
 - Syne Bold, clamp(2.5rem, 8vw, 5rem)
  - tracking-tight, leading-[0.95]
  - "Know the source." in text-primary
  - "Know the truth." in text-accent

Subtext: "Paste any Vietnamese news link. Get instant propagation timeline, source network, and credibility score."
  - DM Sans, text-body, text-text-secondary, max-w-lg, leading-relaxed

Input bar (centered, max-w-2xl):
  - bg-surface border border-border rounded-2xl
  - Hover: border-border-light
  - Focus-within: ring-2 ring-accent/30
  - Input: placeholder "Paste a news link...", DM Sans, text-body
  - Button: "Analyze" — bg-accent text-bg font-semibold px-6 py-3 rounded-xl
  - Button hover: bg-accent/90, slight scale

Stats row (bottom of hero):
  -3 pills with diagonal dividers
  - "10+ Sources tracked" | "Real-time analysis" | "Free forever"
  - Micro text, text-text-tertiary, tracking-widest
```

### Score Card

```
bg-surface border border-border rounded-2xl p-6
Width: 280px (left sidebar)

Circular gauge (SVG):
  - Outer ring: bg-border
  - Progress ring: stroke-dasharray, color based on score
  - Score number: center, JetBrains Mono, text-score, bold
  - Label below: "Credibility Score", text-small, text-text-secondary

Breakdown bars (below gauge):
  - "Source Reputation" — bar 80%, score 8.0
  - "Claim Consistency" — bar 65%, score 6.5
  - "Amplification" — bar 70%, score 7.0
  - Each bar: bg-border track, bg-accent fill, rounded-full h-1.5
  - Score value right-aligned, JetBrains Mono, text-micro

Color coding:
  - Score7-10: text-score-high, ring color-score-high
  - Score 4-6:  text-score-mid,  ring color-score-mid
  - Score 0-3:  text-score-low,  ring color-score-low
```

### Propagation Timeline

```
bg-surface border border-border rounded-2xl p-6
Max-width: 600px

Header: "📡 Propagation Timeline" — text-title, Syne Bold

Vertical timeline:
  - Left line: 2px, bg-border
  - Each node:
    - Circle: 12px, colored by role (origin=accent, copy=amber, amplify=red)
    - Source name: DM Sans semibold, text-body
    - Time: JetBrains Mono, text-micro, text-text-tertiary
    - Role badge: micro text, tracking-widest, uppercase
      - "ORIGIN" — bg-accent/20 text-accent
      - "COPY"   — bg-amber/20 text-amber
      - "AMPLIFY"— bg-red/20 text-red
    - Altered indicator: "⚠️ altered" if altered=true
 - Connecting line between nodes: dashed if copy, solid if origin
```

### Source Network Graph

```
bg-surface border border-border rounded-2xl p-6
Full-width, min-height: 400px

Header: "🕸️ Source Network" — text-title, Syne Bold

D3.js force-directed graph:
  - Canvas/SVG full-width
  - Nodes:
    - Circle radius:20-40px based on article count
    - Fill: node color based on trust score
    - Border: 2px solid matching color
    - Label: source name below node, DM Sans, text-micro
    - Hover: scale1.2, show tooltip with stats
  - Edges:
    - Lines with arrows showing direction
    - Stroke: edge color based on role
    - Width: 1-3px based on connection strength
    - Animated: pulse effect on recent connections
  - Interactions:
    - Drag nodes
    - Zoom/pan
    - Click node: highlight all connections
    - Hover node: dim unconnected nodes
```

### Claims + Fact-Check Cards

```
Grid: 1 column (mobile) / 2 columns (tablet) / 3 columns (desktop)
Gap: 16px

Each card:
  - bg-surface border border-border rounded-xl p-5
  - Claim text: DM Sans, text-body, text-primary
 - Fact-check badge (top-right corner):
    - ✅ VERIFIED   — bg-verified/20 text-verified
    - ❓ UNVERIFIED — bg-unverified/20 text-unverified
    - ⚠️ DISPUTED   — bg-disputed/20 text-disputed
    - ❌ FALSE      — bg-false/20 text-false
  - Source attribution: "via Google Fact Check" or "via Custom DB"
  - Link to external source if available
```

### Footer

```
Minimal, centered
"Built for Vietnamese internet" — text-micro, text-text-tertiary
GitHub link, privacy note
```

---

## Animations

### CSS Keyframes

```css
@keyframes fade-up {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fade-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes scale-in {
  from { opacity: 0; transform: scale(0.95); }
  to   { opacity: 1; transform: scale(1); }
}
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 0 0 var(--color-accent-glow); }
  50%       { box-shadow: 0 0 20px 4px var(--color-accent-glow); }
}
@keyframes draw-line {
  from { stroke-dashoffset: 1000; }
  to   { stroke-dashoffset: 0; }
}
@keyframes count-up {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

### Animation Classes

```css
.animate-fade-up { animation: fade-up 0.6s ease-out forwards; }
.animate-fade-up-1     { animation: fade-up 0.6s ease-out 0.1s forwards; opacity:0; }
.animate-fade-up-2     { animation: fade-up 0.6s ease-out 0.2s forwards; opacity:0; }
.animate-fade-up-3     { animation: fade-up 0.6s ease-out 0.3s forwards; opacity:0; }
.animate-fade-up-4     { animation: fade-up 0.6s ease-out 0.4s forwards; opacity:0; }
.animate-fade-in       { animation: fade-in 0.4s ease-out forwards; }
.animate-scale-in      { animation: scale-in 0.5s ease-out forwards; }
.animate-pulse-glow    { animation: pulse-glow 2s ease-in-out infinite; }
.animate-draw-line     { animation: draw-line 1s ease-out forwards; stroke-dasharray: 1000; }
```

### Component-specific Animations

- **Input bar focus**: border glow transition 200ms
- **Analyze button**: scale0.98 on press, 100ms
- **Score ring**: stroke-dashoffset animation 1.5s ease-out on mount
- **Timeline nodes**: staggered fade-up, 80ms delay between nodes
- **Graph edges**: draw-line animation on mount
- **Fact-check badge**: scale-in on mount
- **Results section**: fade-up stagger when results appear

---

## Spacing & Layout Tokens

```css
/* Section padding */
--section-py: 48px;   /* mobile */
--section-py: 80px;   /* desktop */

/* Card padding */
--card-px: 20px;
--card-py: 24px;

/* Grid gap */
--grid-gap: 16px;    /* mobile */
--grid-gap: 24px;    /* desktop */

/* Border radius */
--radius-sm:  8px;
--radius-md:  12px;
--radius-lg:  16px;
--radius-xl:  24px;
--radius-full: 9999px;
```

---

## Tailwind Configuration

```js
// tailwind.config.js
{
  fontFamily: {
    display: ['Syne', 'sans-serif'],
    body: ['DM Sans', 'sans-serif'],
    mono: ['JetBrains Mono', 'monospace'],
  },
  colors: {
    bg: '#080b12',
    surface: '#0f1520',
    'surface-alt': '#161d2e',
    border: '#1e2a3d',
    'border-light': '#2a3a52',
    accent: '#22d3ee',
    'accent-dim': '#0e7490',
    verified: '#22c55e',
    disputed: '#f59e0b',
    false: '#ef4444',
    unverified: '#94a3b8',
  },
  fontSize: {
    display: 'clamp(2.5rem, 8vw, 5rem)',
    heading: 'clamp(1.5rem, 4vw, 2.5rem)',
    score: 'clamp(3rem, 10vw, 6rem)',
  },
  letterSpacing: {
    tight: '-0.04em',
    wide: '0.08em',
    widest: '0.15em',
  },
  borderRadius: {
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
  },
  animation: {
    'fade-up': 'fade-up 0.6s ease-out forwards',
    'fade-in': 'fade-in 0.4s ease-out forwards',
    'scale-in': 'scale-in 0.5s ease-out forwards',
    'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
  },
}
```

---

## Responsive Behavior

| Element | Mobile | Tablet | Desktop |
|---------|--------|--------|---------|
| Navbar | Hamburger menu | Full links | Full links |
| Hero headline | 2.5rem |4rem | 5rem |
| Input bar | Full width | Centered max-w-xl | Centered max-w-2xl |
| Results layout | Stacked | 2 columns | Side-by-side |
| Timeline | Full width | Full width | 40% width |
| Score card | Full width | 280px fixed | 280px fixed |
| Source graph | Min-h 300px | Min-h 400px | Min-h 500px |
| Claims grid | 1 col | 2 cols | 3 cols |

---

## Icon Library

Use `lucide-react` for all icons:

| Icon | Use |
|------|-----|
| `Search`, `Link` | Input bar |
| `ChevronRight`, `ArrowRight` | CTA buttons |
| `Radio`, `GitBranch` | Propagation timeline |
| `Network`, `GitFork` | Source network |
| `Shield`, `ShieldCheck`, `ShieldX` | Credibility score |
| `CheckCircle`, `AlertCircle`, `XCircle`, `HelpCircle` | Fact-check badges |
| `Clock`, `Globe`, `ExternalLink` | Timestamps, sources |
| `Menu`, `X` | Mobile nav |
| `Github`, `Twitter` | Footer links |
| `Zap`, `Sparkles` | Brand accents |

---

## Dark Mode

SourceWatch is **dark-mode only** — no light mode toggle. Dark mode is core to the brand identity (forensics lab aesthetic).

```css
/* Always dark — no .dark: prefix needed */
body {
  background: #080b12;
  color: #f0f4f8;
}
```

---

## Accessibility

- All interactive elements have `:focus-visible` states (ring-2 ring-accent/50)
- Color is never the only indicator — always paired with icons/text
- Score colors have sufficient contrast ratios (WCAG AA)
- Timeline has screen-reader-friendly structure (`<ol>` with `role="list"`)
- D3 graph has keyboard navigation fallback
- Animations respect `prefers-reduced-motion`
