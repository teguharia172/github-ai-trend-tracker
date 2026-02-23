---
name: frontend-design-enhanced
description: Create distinctive, production-grade frontend interfaces with high design quality. Use when building web components, pages, artifacts, dashboards, React components, or styling web UI. Generates creative, polished code that avoids generic AI aesthetics.
---

# Frontend Design Enhanced

Create distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

## Design Process

### 1. Context Analysis (Do this FIRST, before any code)

Analyze the request:
- **Purpose & Audience**: What problem does this solve? Who uses it? What's their context?
- **Industry/Domain**: What visual language fits? (fintech = precision/trust, creative = bold/expressive, B2B SaaS = clean/professional)
- **Content Requirements**: What specific information must be displayed? Don't miss user-specified details.
- **Technical Constraints**: Framework preferences, device targets, performance needs.

### 2. Aesthetic Direction (Choose ONE clear direction)

Pick a cohesive aesthetic that serves the context:

**Refined Minimalism**: Generous whitespace, sophisticated typography, subtle shadows, monochromatic palettes with single accent, precise alignment.

**Brutalist/Raw**: Asymmetric layouts, exposed structure, monospace fonts, harsh contrasts, ungridded elements.

**Editorial/Magazine**: Strong typography hierarchy, multi-column layouts, generous line-height, serif headlines.

**Retro-Futuristic**: Neon accents on dark backgrounds, geometric shapes, glows, synthwave palettes (NOT generic purple gradients).

**Organic/Natural**: Earthy tones, rounded corners, flowing shapes, textures, warm palettes, soft shadows.

**Luxury/Refined**: Premium serif typography, gold/champagne accents, ample negative space, elegant restraint.

**Industrial/Utilitarian**: Grid systems, monospace fonts, neutral grays, functional layouts, sharp edges.

**CRITICAL**: Your choice must serve the content and audience. A crypto app should NOT look like a toy store. A portfolio should NOT look like enterprise software.

### 3. Implementation

Build working code with:
- Complete functionality (all user requirements)
- Aesthetic cohesion (every element reinforces the direction)
- Detail obsession (typography scales, spacing rhythm, color harmony)
- Context appropriateness (design serves the use case)

## Typography System

**FORBIDDEN FONTS** (overused): Inter, Roboto, Arial, Helvetica, System UI, San Francisco, Segoe UI, Space Grotesk.

**USE INSTEAD** (Google Fonts):

Display/Headlines:
- Serif: Playfair Display, Crimson Pro, Lora, Cormorant Garamond, Libre Baskerville
- Sans: Outfit, Manrope, Plus Jakarta Sans, Sora, Epilogue, Work Sans, DM Sans
- Geometric: Montserrat, Archivo, Raleway
- Decorative: Bebas Neue, Righteous, Orbitron, Oswald

Body/Interface:
- Sans: Source Sans 3, Nunito Sans, Open Sans
- Serif: Merriweather, Libre Franklin, IBM Plex Sans

**Typography Rules**:
1. Pair distinctive display font with neutral body font
2. Use font-weight variations (300, 400, 600, 700) for hierarchy
3. Line-height: 1.2-1.3 for headlines, 1.5-1.6 for body
4. Letter-spacing: tighter (-0.02em) for large text, normal for body
5. Size hierarchy: h1 should be 2-3x larger than body text

## Color System

**Always use CSS Variables**:
```css
:root {
  --color-primary: ...;
  --color-accent: ...;
  --color-background: ...;
  --color-surface: ...;
  --color-text: ...;
  --color-text-secondary: ...;
}
```

**Color Strategies**:
- **Dominant + Accent**: One main (60%), neutral (30%), sharp accent (10%)
- **Monochromatic**: Shades of single hue + neutral for text
- **Analogous**: Adjacent hues (blue-cyan-teal) for harmony
- **Complementary**: Opposite hues for energy (blue + orange, NOT purple + yellow)

**AVOID**:
- Purple gradients on white (#667eea to #764ba2 is overdone)
- Evenly distributed rainbow colors
- Pure black on pure white (use #1a1a1a on #fafafa)
- Generic blue (#3B82F6) without context

**Context-Driven Palettes**:
- Fintech/Crypto: Deep navy, electric blue, cyan accents, dark mode
- Creative/Agency: Bold primaries, high contrast, unexpected combos
- B2B SaaS: Professional blues/grays, trust-building colors
- Health/Wellness: Soft greens, warm neutrals, calming tones

## Layout & Composition

**Break the Grid**:
- Asymmetric element placement
- Overlapping sections with z-index layering
- Diagonal flows and angled dividers
- Off-center focal points
- Mixed column widths

**Spacing System** (use consistent scale):
```css
--space-xs: 0.25rem;  /* 4px */
--space-sm: 0.5rem;   /* 8px */
--space-md: 1rem;     /* 16px */
--space-lg: 2rem;     /* 32px */
--space-xl: 4rem;     /* 64px */
--space-2xl: 8rem;    /* 128px */
```

## Motion & Animation

**CSS Animations**:
```css
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.element {
  animation: fadeInUp 0.6s ease-out forwards;
  animation-delay: 0.2s;
}
```

**Framer Motion** (React):
```jsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.6, delay: 0.2 }}
>
```

**Animation Principles**:
- Use easing: ease-out for entrances, ease-in for exits
- Stagger child elements with animation-delay
- One orchestrated page load beats scattered micro-interactions
- Hover states: instant trigger, smooth transition (0.2s)
- Keep duration under 0.8s

## Visual Effects & Depth

**Backgrounds**:
```css
/* Gradient mesh */
background: radial-gradient(at 20% 30%, #colorA 0%, transparent 50%),
            radial-gradient(at 80% 70%, #colorB 0%, transparent 50%),
            #baseColor;

/* Subtle pattern */
background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(0,0,0,.03) 10px, rgba(0,0,0,.03) 20px);
```

**Shadows & Depth**:
```css
/* Soft elevation */
box-shadow: 0 2px 8px rgba(0,0,0,0.08);

/* Dramatic depth */
box-shadow: 0 20px 60px rgba(0,0,0,0.3);

/* Layered shadows */
box-shadow: 0 1px 2px rgba(0,0,0,0.06), 0 4px 8px rgba(0,0,0,0.1);

/* Colored shadows */
box-shadow: 0 8px 24px rgba(59, 130, 246, 0.2);
```

**Glass/Blur Effects**:
```css
backdrop-filter: blur(12px);
background: rgba(255, 255, 255, 0.1);
border: 1px solid rgba(255, 255, 255, 0.2);
```

## Anti-Patterns (NEVER DO THIS)

❌ **Generic SaaS**: Purple gradient, Inter font, centered cards, predictable 3-column layouts

❌ **Overused Combos**: 
- Inter + purple gradient + soft shadows
- Poppins + pastel colors + rounded everything
- Space Grotesk + neon colors + dark mode

❌ **Missing Context**: Minimalist design for maximalist brand. Playful design for enterprise security.

❌ **Implementation Mismatch**: 
- Elaborate design but simple code (no animations, flat colors)
- Minimalist design but overcomplicated code (unnecessary animations)

❌ **Content Blindness**: Ignoring user-specified requirements like metrics, product names, features.

❌ **Lazy Defaults**: First Google Font that comes to mind, default Tailwind colors, center-aligned everything.

## Quality Checklist

Before finalizing:

✅ Functionality: All user requirements implemented, no broken features  
✅ Typography: Distinctive font pairing, proper hierarchy, intentional choices  
✅ Color: Cohesive palette using CSS variables, context-appropriate  
✅ Layout: Breaks predictable patterns, uses space intentionally  
✅ Motion: At least one well-executed animation or transition  
✅ Effects: Backgrounds, shadows, or textures add atmosphere  
✅ Cohesion: Every element reinforces the aesthetic direction  
✅ Context: Design serves the specific industry/audience/purpose  
✅ Memorability: One distinctive element that makes it unforgettable  

## Execution Philosophy

Each design should be:

1. **Contextually Intelligent**: Serve the specific use case, not generic aesthetics
2. **Aesthetically Coherent**: Every choice reinforces a clear direction
3. **Technically Excellent**: Production-ready code, proper structure, performance-conscious
4. **Visually Distinctive**: Impossible to mistake for generic AI output

Don't hold back. Show what's possible when design thinking meets implementation excellence.
