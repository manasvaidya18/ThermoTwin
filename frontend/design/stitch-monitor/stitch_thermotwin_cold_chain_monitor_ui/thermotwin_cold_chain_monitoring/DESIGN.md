---
name: ThermoTwin Cold-Chain Monitoring
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#3f4947'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#6f7977'
  outline-variant: '#bec9c7'
  surface-tint: '#216963'
  primary: '#004541'
  on-primary: '#ffffff'
  primary-container: '#115e59'
  on-primary-container: '#91d5ce'
  inverse-primary: '#8fd3cc'
  secondary: '#006a61'
  on-secondary: '#ffffff'
  secondary-container: '#86f2e4'
  on-secondary-container: '#006f66'
  tertiary: '#044541'
  on-tertiary: '#ffffff'
  tertiary-container: '#265d59'
  on-tertiary-container: '#9cd4ce'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#abefe8'
  primary-fixed-dim: '#8fd3cc'
  on-primary-fixed: '#00201e'
  on-primary-fixed-variant: '#00504b'
  secondary-fixed: '#89f5e7'
  secondary-fixed-dim: '#6bd8cb'
  on-secondary-fixed: '#00201d'
  on-secondary-fixed-variant: '#005049'
  tertiary-fixed: '#b5ede7'
  tertiary-fixed-dim: '#9ad1cb'
  on-tertiary-fixed: '#00201e'
  on-tertiary-fixed-variant: '#144f4b'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  display-metric-lg:
    fontFamily: Manrope
    fontSize: 3.5rem
    fontWeight: '700'
    lineHeight: 3.75rem
    letterSpacing: -0.03em
  display-metric-sm:
    fontFamily: Manrope
    fontSize: 2.25rem
    fontWeight: '700'
    lineHeight: 2.5rem
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Manrope
    fontSize: 1.75rem
    fontWeight: '700'
    lineHeight: 2.25rem
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Manrope
    fontSize: 1.375rem
    fontWeight: '600'
    lineHeight: 1.75rem
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Manrope
    fontSize: 1.125rem
    fontWeight: '600'
    lineHeight: 1.5rem
  body-lg:
    fontFamily: Public Sans
    fontSize: 1rem
    fontWeight: '400'
    lineHeight: 1.5rem
  body-md:
    fontFamily: Public Sans
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: 1.375rem
  body-sm:
    fontFamily: Public Sans
    fontSize: 0.75rem
    fontWeight: '400'
    lineHeight: 1.125rem
  label-lg:
    fontFamily: Public Sans
    fontSize: 0.875rem
    fontWeight: '600'
    lineHeight: 1.25rem
    letterSpacing: 0.01em
  label-md:
    fontFamily: Public Sans
    fontSize: 0.75rem
    fontWeight: '600'
    lineHeight: 1rem
    letterSpacing: 0.02em
  label-numeric:
    fontFamily: Manrope
    fontSize: 0.875rem
    fontWeight: '700'
    lineHeight: 1.25rem
    letterSpacing: 0.02em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
  space-2xl: 2rem
---

## Brand & Style

This design system establishes a clinical, high-dependability operational environment tailored for cold-chain officers, auxiliary nurse midwives, and medical officers across Indian Primary Health Centres (PHCs). Operating in challenging field realities—ranging from glare-heavy direct daylight to low-cost outdoor tablet displays—the UI delivers immediate situational awareness without visual fatigue.

The aesthetic fuses Institutional Clarity with Modern Clinical Precision. It relies on crisp spatial separation, utilitarian legibility, and high-contrast status feedback. Glancing at the screen must answer three vital questions in under two seconds: Is the vaccine stock safe right now? What will happen in the next four hours? Which specific refrigerator or cold box requires manual intervention? Decorative flourish is eliminated in favor of structured data density, unambiguous operational signals, and tactile, high-affordance control surfaces designed for field handlers wearing medical gloves.

## Colors

The palette is engineered around `#115E59` (Deep Clinical Teal), providing an authoritative, calm anchor that balances urgency against institutional reliability.

Every semantic alert state is strictly accompanied by a 3-part token set: a prominent foreground accent, a tinted surface container, and a high-contrast perimeter stroke. Color is never deployed as the sole signifier of state; every status color is mandatory-paired with distinct iconography and textual verification to guarantee accessibility for color-vision deficiencies.

- **Normal (`#16A34A`)**: Parameters strictly between 2.0°C and 8.0°C.
- **Advisory (`#2563EB`)**: Non-critical notices such as scheduled defrosts, power fluctuations, or routine battery upkeep.
- **Early Warning (`#D97706`)**: Predictive drift models anticipating breaches within 1–4 hours based on ambient thermal acceleration.
- **Critical (`#DC2626`)**: Direct excursion outside the safe threshold (<2.0°C or >8.0°C) or sustained lid-open events.
- **Sensor Anomaly (`#7C3AED`)**: Telemetry loss, detached probes, or battery depletion.

Surfaces employ a clean slate-neutral scale (`#F8FAFC` base) to avoid the wash-out and glaring reflections common on budget TN/IPS field screens.

## Typography

The typographic hierarchy implements Manrope for high-impact numeric instrumentation and headlines, paired with Public Sans for dense operational prose, tabular data, and contextual field logs.

Field constraints demand instantaneous digit recognition. Manrope provides open counters, distinct geometric apexes, and robust tabular numeric alignment that prevents layout jitter when live telemetry updates. Public Sans offers exceptional optical legibility at reduced sizes on degraded hardware, retaining clear separation between numerals and Latin characters.

### Numerical Standards
- All temperature readouts must strictly render to one decimal point (e.g., `4.2°C`, `7.8°C`).
- Negative readings or sub-zero states must feature an explicit minus sign with non-breaking whitespace (`-0.4 °C`).
- Tabular figures (`tnum`) and slashed zeros are strictly enforced on all dashboard metric displays.

## Layout & Spacing

A structured 4-column layout on mobile scales to 8 columns on tablets and 12 columns on desktop supervisor dashboards. A strict 4px base increment underpins all layout rhythm.

Due to physical constraints—handling hardware while carrying vaccine vials, ice-packs, or log books—the primary mobile tap canvas mandates an absolute minimum target of 48×48px for all touch interactive elements, bounded by at least `space-sm` (8px) exterior clear space.

- **Mobile (<640px)**: 4 columns, single-stack cards, primary metrics locked full-width with critical metrics anchored within the thumb zone.
- **Tablet (641px - 1024px)**: 8 columns, side-by-side unit comparison (ILR vs Deep Freezer), split alert/action columns.
- **Desktop (>1025px)**: 12 columns, multi-PHC fleet overview matrix with fixed contextual inspector drawers.

## Elevation & Depth

To maintain high contrast and prevent visual muddying under bright Indian daylight, this system rejects complex skeuomorphic drop-shadows and heavy multi-stop blurs. Depth is produced via crisp structural boundaries, tonal stepping, and thin, deliberate perimeter outlines.

1. **Base Flat (Level 0)**: `#F8FAFC` canvas.
2. **Structural Cards (Level 1)**: Pure white `#FFFFFF` surface enclosed by a 1px solid `#E2E8F0` border. Ambient shadow is clipped to an ultra-crisp offset: `0 1px 3px 0 rgba(15, 23, 42, 0.06), 0 1px 2px -1px rgba(15, 23, 42, 0.04)`.
3. **Elevated & Draggable Cards (Level 2)**: Used for equipment priority reordering and contextual sheets. Enclosed by a 1px solid `#CBD5E1` border with a clean shadow: `0 4px 6px -1px rgba(15, 23, 42, 0.08), 0 2px 4px -2px rgba(15, 23, 42, 0.04)`.
4. **Modal Overlays & Emergency Drawers (Level 3)**: Pure white `#FFFFFF` surface with `0 20px 25px -5px rgba(15, 23, 42, 0.12), 0 8px 10px -6px rgba(15, 23, 42, 0.08)`. Accompanied by a 40% `#0F172A` backdrop scrim.
5. **Alert Boundary Highlight**: Critical and Warning states bypass soft elevation entirely, relying on a 2px high-visibility solid border directly matched to their respective semantic token.

## Shapes

The design system enforces a soft, controlled geometry (roundedness level 1) to convey precision, institutional stability, and utilitarian strength.

- **Base Components**: Inputs, metric tags, chips, and primary alert buttons use `0.25rem` (4px) corner radii.
- **Containers & Device Cards (`rounded-lg`)**: Structural equipment panels, sensor detail modules, and data visualization viewports utilize `0.5rem` (8px).
- **Surface Panels (`rounded-xl`)**: Slide-up triage sheets, emergency override trays, and master modal viewports use `0.75rem` (12px).
- **Fully Rounded Elements**: Status indicator pips, icon circular badges, and numeric count tags utilize `9999px` to distinguish auxiliary meta-indicators from structural operational content.

## Components

### 1. Temperature Telemetry Triad (Primary Domain Component)
Every cold-chain equipment module must distinctly display three discrete data points with explicit typographic and structural differentiation:
- **Measured Air Temp**: Real-time ambient internal cavity reading. Label: `MEASURED AIR`. Font: `Manrope` 700 bold. Displayed as primary large scale readout.
- **Estimated Vaccine Core Temp**: Thermal twin mathematical simulation of vial core fluid. Label: `EST. VIAL CORE`. Placed in an isolated micro-panel with a distinct thermometer fluid icon; neutral background, medium text size.
- **Predicted Trajectory**: Projected thermal curve over the subsequent 2, 4, and 8 hours. Displayed with a predictive trend icon (e.g., `↗ +1.2°C in 2h`) with automatic early-warning coloring if the vector intersects <2.0°C or >8.0°C.

### 2. Buttons & Actions
- **Primary Field Action**: `#115E59` background, white label, 48px height minimum, 4px corner radius. States: Hover `#0D9488`, Active `#134E4A`, Disabled `#E2E8F0` with `#94A3B8` label.
- **Critical Emergency Action**: `#DC2626` background, white label. Used exclusively for incident acknowledgments, generator failovers, or cold box emergency relocations.
- **Secondary Action**: White surface, 1px solid `#CBD5E1` outline, `#0F172A` label.

### 3. Metric & Status Cards
Structured card system utilizing `rounded-lg` (8px) corners, white background, and a 1px structural outline.
- Must include a designated header with: Cold-Chain Equipment ID (e.g., `ILR-02 (Small)`), location (e.g., `Vaccine Room 1`), connection health pill, and telemetry timestamp (e.g., `Updated 2m ago`).
- Normal state: 1px `#E2E8F0` border.
- Warning/Critical state: 2px solid semantic border, paired with an emergency banner anchored inside the top edge of the card.

### 4. Status Chips & Badges
Chips feature a pill shape (`9999px`), 1px solid border matching the status token, tinted low-saturation surface, and uppercase `Public Sans` 11px bold text.
- Must include a 12px status icon prefix (e.g., Shield for Normal, Triangle Alert for Warning, Octagon Alert for Critical, Wrench/Signal-Slash for Sensor Anomaly).

### 5. Input Fields & Calibration Forms
- 48px height touch target. 1px solid `#CBD5E1` border on `#FFFFFF` base. 
- Focus state: 2px solid `#115E59` ring with 1px white offset. 
- Numeric steppers for threshold adjustments must feature oversized `+` and `-` physical buttons (44×44px) flanking the input area.

### 6. Threshold Reference Rails
Visual linear bar under every telemetry metric illustrating the hard boundary markers:
- Safe baseline (2.0°C to 8.0°C) highlighted with a clear green track.
- Freezing danger zone (<2.0°C) and Heat breach zone (>8.0°C) clearly patterned with hash-marks or distinct tinting.
- The current temperature is plotted as a high-contrast cursor with an explicit numerical callout badge.