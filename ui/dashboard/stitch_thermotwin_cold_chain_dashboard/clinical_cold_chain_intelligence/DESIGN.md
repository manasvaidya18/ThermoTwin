---
name: Clinical Cold-Chain Intelligence
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#3e4947'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#6e7977'
  outline-variant: '#bdc9c6'
  surface-tint: '#006a63'
  primary: '#005c55'
  on-primary: '#ffffff'
  primary-container: '#0f766e'
  on-primary-container: '#a3faef'
  inverse-primary: '#80d5cb'
  secondary: '#0051d5'
  on-secondary: '#ffffff'
  secondary-container: '#316bf3'
  on-secondary-container: '#fefcff'
  tertiary: '#7d4200'
  on-tertiary: '#ffffff'
  tertiary-container: '#a15600'
  on-tertiary-container: '#ffe6d5'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#9cf2e8'
  primary-fixed-dim: '#80d5cb'
  on-primary-fixed: '#00201d'
  on-primary-fixed-variant: '#00504a'
  secondary-fixed: '#dbe1ff'
  secondary-fixed-dim: '#b4c5ff'
  on-secondary-fixed: '#00174b'
  on-secondary-fixed-variant: '#003ea8'
  tertiary-fixed: '#ffdcc3'
  tertiary-fixed-dim: '#ffb77d'
  on-tertiary-fixed: '#2f1500'
  on-tertiary-fixed-variant: '#6e3900'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-xl-mobile:
    fontFamily: Inter
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 34px
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  metric-display:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
  metric-display-mobile:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 36px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 14px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-mobile: 0.75rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-mobile: 1rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style

This design system is engineered for critical public health operations, specifically early-warning thermal simulation and telemetric tracking across distributed cold-chain points.

### Personality & Tone
- **Clinical & Unwavering:** Information is rendered without ornamental distraction. The interface prioritizes high-stakes legibility over expressive decorative trends.
- **Calm & Trustworthy:** High-stress operational environments require reassurance through structure. Layouts emphasize stability, systematic rhythm, and unambiguous states.
- **Strictly Functional & Error-Resistant:** Tap targets are generous, interaction states provide explicit confirmation, and cognitive load is reduced through strict information hierarchy.

### Clinical Language Constraints
- The system delivers predictive alerts, telemetry monitoring, and advisory intelligence.
- The interface **must never** claim definitive biological viability or absolute batch safety. Copy must use observational terms such as:
  - *"Advisory: Excursion risk predicted"*
  - *"Thermal breach warning: Inspection advised"*
  - *"Telemetry within recommended 2.0°C – 8.0°C envelope"*
- Prohibited phrasing: *"Vaccines are safe,"* *"Zero spoilage confirmed,"* or *"Stock guaranteed."*

### Design Movement
- **Modern Clinical Utility:** Combines systematic design tokens with institutional-grade data density. It borrows the rigor of laboratory instruments and the accessibility of public-health field tools.

## Colors

The color palette prioritizes rapid state assessment under direct sunlight, low-grade Android displays, and high-glare environments. Color is never used as the sole conveyor of information; every alert state couples color tokens with distinct iconography and textual status indicators.

### Primary & System Neutrals
- **Primary Teal (`#0F766E`):** Represents institutional cold-chain governance. Used for primary controls, key navigation landmarks, and active primary indicators.
- **Teal Shade (`#115E59`):** Interactive hover/active states for primary actions.
- **Teal Surface Tint (`#F0FDFA`):** Low-contrast selection states and telemetry highlight panels.
- **Canvas (`#F8FAFC`):** Slate-50 background ensuring optimal contrast with card surfaces.
- **Card Surface (`#FFFFFF`):** High-purity white, establishing separation from canvas.
- **Text Dominant (`#0F172A`):** Slate-900 for high-contrast tabular values, headings, and alert headers.
- **Text Muted (`#64748B`):** Slate-500 for field labels, timestamps, and secondary telemetric metadata.
- **Structural Border (`#E2E8F0`):** Slate-200 defining explicit component boundaries.

### Operational Alert & Health Tiers
Alert tokens are strictly grouped in trios (base stroke/icon, container background, and accessible foreground text):

- **Normal (Within Range):**
  - Accent: `#16A34A`
  - Container: `#DCFCE7`
  - Text: `#166534`
  - *Context:* Core sensors logging within the standard 2.0°C to 8.0°C envelope.

- **Advisory (Trending / External Factor):**
  - Accent: `#2563EB`
  - Container: `#DBEAFE`
  - Text: `#1E40AF`
  - *Context:* Ambient temperature climb, prolonged door openings, grid switchover detected.

- **Early Warning (Predicted Excursion):**
  - Accent: `#D97706`
  - Container: `#FEF3C7`
  - Text: `#92400E`
  - *Context:* Internal buffer thermal shift projecting an excursion within a 60–120 minute window.

- **Critical (Out of Range / Thermal Compromise):**
  - Accent: `#DC2626`
  - Container: `#FEE2E2`
  - Text: `#991B1B`
  - *Context:* Temperature reading currently strictly below 2.0°C or above 8.0°C.

- **Sensor Check (Telemetry Loss / Fault):**
  - Accent: `#7C3AED`
  - Container: `#F3E8FF`
  - Text: `#6B21A8`
  - *Context:* Data logger offline, battery critical, or open-circuit probe detected.

### Target Range Band
- **Thermal Safe Envelope Indicator:** Background tint `#DCFCE7` with border `#86EFAC` bounded specifically across the 2.0°C to 8.0°C range on all telemetry charts and digital twin visualizations.

## Typography

Typography relies entirely on the neutral and systematic qualities of `Inter`. Clarity and scanning speed are maximized through strict weight pairing and tabular figures.

### Tabular Formatting
- All temperature readouts, time durations, battery percentages, and device identifiers must enforce `font-feature-settings: "tnum" 1, "cv05" 1`. This eliminates visual shifting during real-time data streaming.
- Temperature metrics are formatted to exactly one decimal place (e.g., `+4.2 °C`, `+0.8 °C`), accompanied by an explicit unit marker.

### Hierarchy & Scale Rules
- **Metric Display:** Reserved exclusively for live telemetry readouts inside device cards and overview headers.
- **Headlines:** Used strictly for view titles, facility names, and unit asset tags.
- **Labels:** Applied to alert badges, status chips, table headers, and sensor probe identifiers. Uppercase transformation with tracking (`letter-spacing: 0.04em`) is applied only to `label-sm`.
- **Body:** Standardized across reading logs, advisory warnings, and configuration documentation.

## Layout & Spacing

The layout system addresses two distinct operational environments: field inspections via rugged mobile handhelds and central district command desks via high-density dashboards.

### Grid Philosophy
- **Responsive Fluid Grid:** 
  - **Mobile (< 768px):** 4 columns, `margin-mobile` (16px), `gutter-mobile` (12px). All telemetry summary units stack vertically.
  - **Tablet (768px – 1199px):** 8 columns, `gutter` (16px), `margin` (24px). Cold-chain cards render in pairs.
  - **Desktop (≥ 1200px):** 12 columns, `margin-desktop` (32px), `gutter-desktop` (24px). Digital twin 3D/schematic views span 8 columns, telemetry and alert streams span 4 columns.

### Spatial Rhythm
- Base scale derives strictly from an 8pt system, using 4pt increments (`space-xs`) only for compact inline chip padding and tabular metrics.
- Component-internal padding adheres to `space-md` (16px) for standard cards and `space-lg` (24px) for critical excursion alarm modules.
- Form controls and action targets adhere to a minimum tap dimension of 48px to accommodate field workers wearing sterile or protective gloves.

## Elevation & Depth

To maintain high contrast and avoid visual ambiguity under bright clinical lighting, depth is established via sharp structural borders backed by low-diffusion ambient shadows.

### Elevation Levels
- **Level 0 (Flat Surface / Canvas):** Neutral `#F8FAFC`. Zero elevation.
- **Level 1 (Clinical Cards & Data Rows):** Background `#FFFFFF`, border `1px solid #E2E8F0`, shadow `0 1px 3px 0 rgba(15, 23, 42, 0.06), 0 1px 2px -1px rgba(15, 23, 42, 0.04)`.
- **Level 2 (Active Metric Cards & Focused Telemetry):** Border `1px solid #CBD5E1`, shadow `0 4px 6px -1px rgba(15, 23, 42, 0.08), 0 2px 4px -2px rgba(15, 23, 42, 0.04)`.
- **Level 3 (Sticky Action Bars & Overlays):** Border `1px solid #E2E8F0`, shadow `0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.04)`.
- **Critical Excursion Modal / Priority Override:** Border `2px solid #DC2626`, shadow `0 20px 25px -5px rgba(220, 38, 38, 0.15), 0 8px 10px -6px rgba(220, 38, 38, 0.1)`.

### Border Integrity
Shadows never float independently; they are paired with a 1px border (`#E2E8F0` or status equivalent) to preserve structural integrity on low-tier screens.

## Shapes

The geometric expression utilizes calibrated corner radii corresponding to `roundedness: 2`. This balance softens structural density while avoiding the non-clinical, consumer-facing look of pill-shaped containers.

### Corner Radius Assignments
- **Base Components (`0.5rem` / 8px):** Input fields, standard buttons, dropdown selectors, alert banners, and telemetry chips.
- **Cards and Containers (`1rem` / 16px):** Primary fridge monitoring cards, twin cross-section panels, chart containers, and modal dialogs.
- **Nested Inner Surfaces (`0.375rem` / 6px):** Telemetry sub-blocks nested within larger parent cards (maintaining concentric corner balance).
- **Indicators and Dot Badges (Full Circle / 9999px):** Live connectivity pings, online/offline LEDs, and map clustering dots.

## Components

### Buttons
- **Primary:** Background `#0F766E`, text `#FFFFFF`, border transparent. Focus ring `2px solid #0F766E` with `2px` offset. Active `#115E59`.
- **Secondary / Outline:** Background `#FFFFFF`, text `#0F172A`, border `1px solid #E2E8F0`. Hover background `#F8FAFC`.
- **Destructive / Urgent:** Background `#DC2626`, text `#FFFFFF`, hover `#B91C1C`.
- **Size Options:** Minimum height 48px on mobile, 40px on desktop dashboards. Padding: 0 16px (12px for compact table actions).

### Status Badges & Chips
- Non-interactive badges communicating health states must strictly combine a 12px SVG icon, uppercase label, and status-specific background/text tokens:
  - **Normal Badge:** `#DCFCE7` background, `#166534` text, icon checkmark.
  - **Advisory Badge:** `#DBEAFE` background, `#1E40AF` text, icon info circle.
  - **Early Warning Badge:** `#FEF3C7` background, `#92400E` text, icon triangle exclamation.
  - **Critical Badge:** `#FEE2E2` background, `#991B1B` text, icon octagon exclamation.
  - **Sensor Check Badge:** `#F3E8FF` background, `#6B21A8` text, icon signal-slash.
- Chips have an internal padding of `space-xs` (top/bottom) and `space-sm` (left/right) with `border-radius: 0.5rem`.

### Telemetry Cards
- **Structure:** Clean white surface, 1px `#E2E8F0` border, `1rem` radius.
- **Header:** Displays equipment identifier (e.g., *ILR-PHC-NANDURBAR-04*) in `label-lg`, alongside the status badge.
- **Primary Readout:** Real-time internal temperature in `metric-display`, accompanied by trend vector arrow (rising, stable, falling).
- **Target Envelope Visual:** Embedded mini-bar chart indicating current reading relative to the shaded `2.0°C – 8.0°C` safe zone.
- **Footer:** Last synced timestamp in `body-sm` (`#64748B`) and battery/compressor state icons.

### Inputs & Selectors
- **Input Field:** Height 48px, background `#FFFFFF`, border `1px solid #CBD5E1`, text `#0F172A`, font size `16px` (prevents auto-zoom on iOS/Android).
- **Placeholder:** `#94A3B8`.
- **Validation:** Error state changes border to `#DC2626` and renders supporting advisory text below the input field with a leading icon.

### Form Checkboxes & Radios
- Size: 20x20px with a 48x48px transparent touch boundary.
- Border `2px solid #64748B`. Selected state fills with `#0F766E` and renders a stark white check/dot.

### List Items & Logs
- Partitioned by 1px solid dividers (`#F1F5F9`).
- Left-aligned metadata (timestamp, excursion incident ID) paired with right-aligned tabular metrics (`+8.4 °C`, `42m duration`).
- Alternating subtle row striping is prohibited; visual clarity relies strictly on whitespace and borders.