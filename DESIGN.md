---
name: AgriVision AI
colors:
  surface: '#f9f9ff'
  surface-dim: '#cfdaf2'
  surface-bright: '#f9f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f0f3ff'
  surface-container: '#e7eeff'
  surface-container-high: '#dee8ff'
  surface-container-highest: '#d8e3fb'
  on-surface: '#111c2d'
  on-surface-variant: '#3d4a3d'
  inverse-surface: '#263143'
  inverse-on-surface: '#ecf1ff'
  outline: '#6d7b6c'
  outline-variant: '#bccbb9'
  surface-tint: '#006e2f'
  primary: '#006e2f'
  on-primary: '#ffffff'
  primary-container: '#22c55e'
  on-primary-container: '#004b1e'
  inverse-primary: '#4ae176'
  secondary: '#5d5f5f'
  on-secondary: '#ffffff'
  secondary-container: '#dfe0e0'
  on-secondary-container: '#616363'
  tertiary: '#005ac2'
  on-tertiary: '#ffffff'
  tertiary-container: '#82abff'
  on-tertiary-container: '#003d88'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#6bff8f'
  primary-fixed-dim: '#4ae176'
  on-primary-fixed: '#002109'
  on-primary-fixed-variant: '#005321'
  secondary-fixed: '#e2e2e2'
  secondary-fixed-dim: '#c6c6c7'
  on-secondary-fixed: '#1a1c1c'
  on-secondary-fixed-variant: '#454747'
  tertiary-fixed: '#d8e2ff'
  tertiary-fixed-dim: '#adc6ff'
  on-tertiary-fixed: '#001a42'
  on-tertiary-fixed-variant: '#004395'
  background: '#f9f9ff'
  on-background: '#111c2d'
  surface-variant: '#d8e3fb'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  title-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  caption:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  container-margin: 20px
  gutter: 16px
---

## Brand & Style
The brand personality is **Empathetic, Precise, and Vital**. This design system bridges the gap between high-end artificial intelligence and the tactile, grounded world of agriculture. It targets a diverse user base, from tech-savvy agribusiness managers to rural farmers, requiring a UI that is both sophisticated and exceptionally accessible.

The design style is **Modern Professionalism with High-Tactile Clarity**. It draws inspiration from the friendly, high-radius components of modern educational apps while maintaining the structured, data-driven reliability of enterprise SaaS. The aesthetic avoids heavy shadows in favor of tonal depth and clean, structural borders to ensure legibility under high-glare outdoor conditions. 

The emotional response should be one of **calm confidence**. The interface does not shout; it assists. By utilizing generous whitespace and a "content-first" hierarchy, the system reduces cognitive load, allowing users to focus on crop health and data insights without distraction.

## Colors
The palette is rooted in the "Nature Green" primary color, symbolizing growth and health. 

- **Primary (#22C55E):** Used for key actions, success states, and growth indicators.
- **Surface & Background:** A heavy reliance on pure white (#FFFFFF) for cards and #F8FAFC for background grouping to maintain a "clean-room" feel.
- **Accent Blue (#3B82F6):** Reserved for informational callouts, technical data points, and AI-driven insights to differentiate "software intelligence" from "biological health."
- **Neutral Dark (#1E293B):** Used for high-contrast typography to ensure readability across all lighting conditions.
- **Semantic Colors:** Strict adherence to Green (Success), Orange (Warning), and Red (Error) for immediate diagnostic recognition.

## Typography
**Inter** is selected for its exceptional legibility and neutral, systematic character. It supports a wide range of weights and provides the clarity needed for multi-language support (English, Hindi, Marathi).

- **Hierarchy:** Use `display-lg` sparingly for hero stats or welcome screens. `headline-lg` is the primary entry point for section headers.
- **Accessibility:** Body text never drops below 16px to ensure readability for users in the field. 
- **Multilingual Note:** For Hindi and Marathi scripts, line heights are increased by 15% automatically to accommodate taller character ascenders and descenders without crowding the layout.

## Layout & Spacing
The system utilizes a **Fluid Grid** model based on an 8px scale. For mobile devices, a 4-column grid is standard, while tablets transition to an 8-column grid.

- **Safe Zones:** A 20px outer margin ensures content doesn't bleed into screen edges or get obscured by rugged phone cases.
- **Touch Targets:** All interactive elements maintain a minimum hit area of 48x48px.
- **Vertical Rhythm:** Use `md (16px)` for internal component padding and `lg (24px)` for spacing between distinct content blocks.
- **Scanning:** Information is grouped in vertical stacks to facilitate quick scrolling and scanning while walking through fields.

## Elevation & Depth
This design system utilizes **Tonal Layers** rather than heavy shadows to signify depth. This ensures the UI remains crisp under direct sunlight.

1.  **Level 0 (Background):** #F8FAFC. The lowest layer.
2.  **Level 1 (Cards/Surfaces):** #FFFFFF. These elements feature a subtle 1px border in #E2E8F0 to define their edges without relying on shadow.
3.  **Level 2 (Modals/Overlays):** White with a very soft, highly diffused ambient shadow (Color: #1E293B, Opacity: 6%, Blur: 12px).
4.  **Interactive State:** On tap/press, elements transition with a subtle inner-tint of the primary color rather than an outward shadow, simulating a "pressed" physical feel.

## Shapes
The shape language is **Friendly and Intentional**. A medium roundedness (8px) is the standard for most components, providing a modern, approachable feel that isn't overly "bubbly."

- **Standard Components:** 8px (0.5rem) radius for cards and input fields.
- **Buttons:** 12px (0.75rem) radius to make them distinct and inviting to touch.
- **Feedback Tags/Chips:** Fully rounded (pill-shaped) to differentiate them from actionable buttons.

## Components
- **Buttons:** Large, high-contrast surfaces. Primary buttons use Nature Green with White text. Secondary buttons use a White background with a 1px Grey-200 border and Dark Gray text.
- **AI Diagnostic Cards:** Use a 16px internal padding. Headers within cards should use `title-md`. Include a "Status Bar" at the very top of the card (2px height) using semantic colors (Green/Orange/Red) for instant recognition.
- **Input Fields:** Minimum height of 56px. Labels are persistent `label-md` placed above the field. Border-based focus states use the Primary Green at 2px thickness.
- **Status Chips:** Low-saturation backgrounds with high-saturation text (e.g., Light Green background with Dark Green text) for non-interactive indicators.
- **Language Switcher:** A prominent, accessible toggle or bottom-sheet trigger, using clear native-script labels (e.g., "हिन्दी", "मराठी", "English").
- **Data Visualization:** Simple, high-contrast bar charts and line graphs using Primary Green and Accent Blue. Avoid complex legends; use direct labeling.