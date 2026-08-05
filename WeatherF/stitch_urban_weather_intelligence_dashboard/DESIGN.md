---
name: Thermal Synapse
colors:
  surface: '#faf9f5'
  surface-dim: '#dbdad6'
  surface-bright: '#faf9f5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f4f0'
  surface-container: '#efeeea'
  surface-container-high: '#e9e8e4'
  surface-container-highest: '#e3e2df'
  on-surface: '#1b1c1a'
  on-surface-variant: '#434840'
  inverse-surface: '#2f312e'
  inverse-on-surface: '#f2f1ed'
  outline: '#73796f'
  outline-variant: '#c3c8bd'
  surface-tint: '#496640'
  primary: '#334f2b'
  on-primary: '#ffffff'
  primary-container: '#4a6741'
  on-primary-container: '#c2e4b4'
  inverse-primary: '#afd0a1'
  secondary: '#50606f'
  on-secondary: '#ffffff'
  secondary-container: '#d1e1f4'
  on-secondary-container: '#556474'
  tertiary: '#5a4425'
  on-tertiary: '#ffffff'
  tertiary-container: '#735c3a'
  on-tertiary-container: '#f6d6ac'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#caecbc'
  primary-fixed-dim: '#afd0a1'
  on-primary-fixed: '#062104'
  on-primary-fixed-variant: '#324e2a'
  secondary-fixed: '#d4e4f6'
  secondary-fixed-dim: '#b8c8da'
  on-secondary-fixed: '#0d1d2a'
  on-secondary-fixed-variant: '#394857'
  tertiary-fixed: '#feddb3'
  tertiary-fixed-dim: '#e1c299'
  on-tertiary-fixed: '#281801'
  on-tertiary-fixed-variant: '#584324'
  background: '#faf9f5'
  on-background: '#1b1c1a'
  surface-variant: '#e3e2df'
typography:
  display-lg:
    fontFamily: Newsreader
    fontSize: 48px
    fontWeight: '600'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Newsreader
    fontSize: 32px
    fontWeight: '500'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Newsreader
    fontSize: 28px
    fontWeight: '500'
    lineHeight: 36px
  body-md:
    fontFamily: Work Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Work Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.08em
  data-tabular:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-desktop: 64px
  margin-mobile: 16px
  max-width: 1440px
---

## Brand & Style
The design system transitions from a high-energy digital aesthetic to a **Calm & Classic** research-oriented atmosphere. It is tailored for environmental scientists and health researchers who require long-duration focus without visual fatigue.

The visual style is a hybrid of **Minimalism** and **Modern Corporate**, utilizing a "Technical Paper" metaphor. It maintains its data-driven roots through disciplined grid structures and monospaced accents, but softens the delivery with a light, organic palette. The emotional response is one of reliability, precision, and environmental stewardship.

## Colors
The palette is rooted in earth-toned serenity to promote "environmental health."
- **Primary (Sage Green):** Used for key actions and brand presence. It signifies growth and ecological focus.
- **Secondary (Slate):** Used for technical UI elements, icons, and secondary supporting data.
- **Tertiary (Sand):** An accent for highlighting specific data points or "warning" states that require attention without causing alarm.
- **Neutral (Soft White/Cream):** The primary background color, specifically chosen to reduce the harsh blue-light glare of pure white.

Surface colors should follow a tonal layering approach: 
- `Surface`: #FDFCF8 (Base)
- `Surface-Container`: #F4F2E9 (Sidebar/Cards)
- `Surface-Outline`: #E2E0D4 (Dividers/Grids)

## Typography
The typography strategy creates a "Research Journal" feel. 
- **Newsreader** provides an authoritative, editorial voice for headlines, grounding the application in classic credibility.
- **Work Sans** serves as the workhorse for body text, offering high legibility and a professional, neutral tone.
- **JetBrains Mono** is utilized sparingly for data points, coordinates, and technical labels, maintaining the "Synapse" technical heritage while ensuring clarity in dense environmental reports.

## Layout & Spacing
The layout follows a **Fixed Grid** philosophy to mirror the structured nature of scientific documents. 
- **Desktop:** A 12-column grid with a max-width of 1440px. Gutters are generous (24px) to allow the content to "breathe."
- **Tablet:** 8-column grid with 20px gutters.
- **Mobile:** 4-column grid with 16px margins. 

Vertical rhythm is strictly maintained using a 4px baseline unit. All components and spacing increments should be multiples of 4 (8px, 16px, 24px, etc.). Technical data sections should use subtle 1px dividers in `Surface-Outline` to create a "grid-map" feel without the aggression of the previous dark-mode version.

## Elevation & Depth
In this light-mode iteration, the design system moves away from shadows in favor of **Tonal Layers** and **Low-contrast Outlines**. 
- **Depth:** Hierarchical levels are defined by slight shifts in background saturation (e.g., a card is 2% darker or lighter than the background) rather than heavy drop shadows.
- **Outlines:** Use 1px solid borders in #E2E0D4 for all containers. This reinforces the "technical blueprint" aesthetic.
- **Interactive States:** When an element is hovered or active, use a subtle "Sand" (#D2B48C) tint or a slightly thicker 2px border rather than a lift effect.

## Shapes
The shape language is **Soft**. 
A 0.25rem (4px) base radius is applied to buttons, input fields, and small UI components. This provides a professional, "precision-machined" look that is approachable but not overly casual. Larger containers like cards or modals may use `rounded-lg` (8px) to soften the overall interface composition.

## Components
- **Buttons:** Primary buttons use a solid Sage Green background with white Work Sans text. Secondary buttons are outlined in Slate with no fill.
- **Chips/Tags:** Use the JetBrains Mono font at a small scale. Backgrounds should be very desaturated versions of the primary/secondary colors (e.g., Pale Sage).
- **Inputs:** Fields are rectangular with a 1px border. On focus, the border color changes to Sage Green, and the label (in JetBrains Mono) shifts to a "tab" position at the top-left.
- **Cards:** Cards should not have shadows. They are defined by a 1px border and a slightly different tonal background than the page body.
- **Data Tables:** High-density grids are essential. Use alternate row striping in a very faint Sand tint. Headers should be in uppercase JetBrains Mono with a bottom border.
- **Progress Indicators:** Use thin, horizontal bars rather than circular loaders to maintain the linear, technical feel of the system.