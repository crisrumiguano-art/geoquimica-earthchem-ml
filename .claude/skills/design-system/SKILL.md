---
name: design-system
description: Full-stack Design Intelligence. Encompasses UX Shaping (discovery & briefs), Brand Design (logos, palettes, typography), Design System Generation/Auditing, and Emil Kowalski's philosophy on UI polish and animation decisions.
version: 3.0.0
user-invocable: true
argument-hint: "[feature to shape] or [brand to design] or [system to audit]"
---

# The Full-Stack Design System Engineer

This master skill governs the entire design lifecycle: from understanding the user need (Shape), to creating the brand identity (Brand Designer), systematizing it into tokens (System Generation), and applying ultra-high-end interactions (UI Polish & Animation).

---

## PHASE 1: Shape (UX & UI Planning)

Shape the UX and UI for a feature before any code is written. This phase produces a **design brief**: a structured artifact that guides implementation through discovery, not guesswork. Most AI-generated UIs fail because they skip thinking. This phase inverts that.

### 1.1 Discovery Interview
**Do NOT write any code or make any design decisions during this phase.** Ask these questions in natural conversation to understand the feature deeply.

**Purpose & Context**
- What is this feature for? What problem does it solve?
- Who specifically will use it? (role, context, frequency)
- What does success look like?
- What's the user's state of mind when they reach this feature?

**Content & Data**
- What content/data does this feature display or collect?
- What are the realistic ranges? (0 items, 5 items, 500 items)
- What are the edge cases? (Empty state, error state, first-time use)
- Is any content dynamic?

**Design Goals & Constraints**
- What's the single most important thing a user should do here?
- What should this feel like? (Fast, calm, premium?)
- Technical constraints? (Framework, performance, mobile)
- Anti-goals: What should this NOT be?

### 1.2 The Design Brief Output
Synthesize the interview into this structure:
1. **Feature Summary**: What this is and who it's for.
2. **Primary User Action**: The single most important task.
3. **Design Direction**: Desired aesthetic and feeling.
4. **Layout Strategy**: Spatial approach and visual hierarchy.
5. **Key States**: Default, empty, loading, error, success.
6. **Interaction Model**: Click, hover, scroll feedback.
7. **Content Requirements**: Copy, labels, dynamic ranges.
8. **Open Questions**: Anything unresolved for implementation.

---

## PHASE 2: Brand Designer

Guides the creation of complete brand identity systems. Perfect for B2B, industrial, educational, and tech companies. Output is design-ready specifications (Figma/Canva) or SVG generation.

### 2.1 Gather Brand Brief
Ask for: Company name/sector, Brand values, Target audience, Competitors, Visual preferences, Applications needed.

### 2.2 Logo Concept & Construction
**Concept = [Initial/Symbol] + [Industry metaphor] + [Value accent]**
- *Example:* M (letter) + Mountain (terrain) + Diamond (value) = Minexfield.
- **Rules:** Geometric grid (60° for industrial, 45° tech). Filled areas wider than empty gaps. Typography ALL CAPS sans-serif.

### 2.3 Logo Variants & DON'Ts
**Produce all variants:** Horizontal full, Horizontal short, Stacked full, Stacked short, Isologo only.
**Color rules per bg:** Dark bg (white icon/text + accent tagline). Light bg (navy icon/text + accent tagline).
**6 DON'Ts (Uso Incorrecto):** 1. Reorganizar, 2. Deformar, 3. Cambiar color, 4. Sombra, 5. Bordes añadidos, 6. Inclinación.

### 2.4 Color Palette Architecture
```text
PRIMARY: Deep/Dark (backgrounds) + Mid (modernity) + Accent (energy/CTA)
SUPPORTING: White/Light (body on dark) + Gray text + Dark text (headings)
```
- **Usage:** Backgrounds use Deep/Mid. Accent is ONLY for small elements/CTAs.
- Provide HEX + CMYK equivalents.

### 2.5 Typography System
- **Family:** One geometric sans-serif (e.g., Poppins, Montserrat, Inter).
- **Titles:** Bold (700) / Semi-Bold (600), UPPERCASE for brand names.
- **Body:** Regular (400) / Light (300), Sentence case.
- *Size ratio:* Page titles 2.5x body. Section headers 1.5x body. Captions 0.85x.

### 2.6 Applications & Layout Style
- **Geometric Diagonal System:** Strips at 45–60° angles. Layered brand colors.
- **Photo treatment:** B&W desaturated photos masked against colored geometric shapes.
- **Course/Product Cards:** Rounded corners (16px), photo top, CTA pill button.
- **Output:** Detail layout for Business Cards, Letterhead, Certificates, Social Media Posts, Website Heros.

---

## PHASE 3: Design System Generation & Auditing

### 3.1 Mode 1: Generate Design System
Analyzes the codebase and generates a cohesive token set:
1. Scan CSS/Tailwind for existing patterns.
2. Extract colors, typography, spacing, border-radius, shadows.
3. Propose a JSON + CSS design token set.
4. Output `DESIGN.md` + `design-tokens.json` + `design-preview.html`.

### 3.2 Mode 2: Visual Audit
Scores UI across 10 dimensions (0-10 each):
1. Color consistency, 2. Typography hierarchy, 3. Spacing rhythm, 4. Component consistency, 5. Responsive behavior, 6. Dark mode, 7. Animation purpose, 8. Accessibility (contrast, targets), 9. Information density, 10. Polish (hover, empty states).
*Output: Score + Specific File/Line fix.*

### 3.3 Mode 3: AI Slop Detection
Identifies generic AI-generated patterns:
- Gratuitous gradients / Purple-to-blue defaults.
- "Glass morphism" with no purpose.
- Rounded corners on things that shouldn't be rounded.
- Excessive scroll animations.
- Sans-serif stacks with no personality.

---

## PHASE 4: Emil Kowalski UI Polish & Engineering

### 4.1 Core Philosophy
- **Taste is trained, not innate.** Study why the best interfaces feel good. Reverse engineer animations.
- **Unseen details compound.** When features function exactly as someone assumes, they proceed without a second thought.
- **Beauty is leverage.** Use it as leverage to stand out in a world where software is just "good enough".

### 4.2 Code Review Format (Required)
When reviewing UI code, you MUST use a markdown table with Before/After columns. Never use lists.

| Before | After | Why |
| --- | --- | --- |
| `transition: all 300ms` | `transition: transform 200ms ease-out` | Specify exact properties; avoid `all` |
| `transform: scale(0)` | `transform: scale(0.95); opacity: 0` | Nothing in the real world appears from nothing |
| `ease-in` on dropdown | `ease-out` with custom curve | `ease-in` feels sluggish; `ease-out` gives instant feedback |

### 4.3 The Animation Decision Framework
**1. Should this animate at all?**
- *100+ times/day (keyboard shortcuts)*: No animation. Ever.
- *Tens of times/day (hovers, lists)*: Remove or drastically reduce.
- *Occasional (modals, toasts)*: Standard animation.

**2. What is the purpose?**
Valid purposes: Spatial consistency, state indication, feedback (button press). NOT just "looks cool".

**3. What easing should it use?**
- Entering? → `ease-out`
- Moving on screen? → `ease-in-out`
- Hover/color? → `ease`
- Constant motion? → `linear`
*CRITICAL: Use custom curves. Never use `ease-in` for UI (it feels sluggish).*
```css
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
```

**4. How fast should it be?**
Rule: UI animations stay under 300ms.
- Button press: 100-160ms.
- Tooltips: 125-200ms.
- Modals/Drawers: 200-500ms.

### 4.4 Spring Animations
Springs feel natural. Use for drag momentum, alive elements, interruptible gestures.
*Apple's approach:* `{ type: "spring", duration: 0.5, bounce: 0.2 }`
*Advantage:* Springs maintain velocity when interrupted, unlike CSS keyframes which restart from zero.

### 4.5 Component Building Principles
- **Buttons must feel responsive:** `transform: scale(0.97)` on `:active`.
- **Never animate from `scale(0)`:** Start from `scale(0.95)` with `opacity: 0`. It looks like it comes from nowhere otherwise.
- **Make popovers origin-aware:** Scale from their trigger, not from center. (`transform-origin: var(--radix-popover-content-transform-origin)`). Modals are the exception.
- **Tooltips:** Delay the first one. Skip animation (`transition-duration: 0ms`) on adjacent tooltips once one is open.
- **CSS Transitions > Keyframes for UI:** Transitions can be interrupted and retargeted mid-animation. Keyframes restart from zero.
- **Use blur to mask imperfect transitions:** Add `filter: blur(2px)` during crossfades to blend states naturally.
- **Enter states:** Use `@starting-style` where supported to animate entry without JS `useEffect`.

### 4.6 CSS Transform Mastery
- **`translateY` with percentages:** Relative to the element's own size. Use `translateY(100%)` to move an element exactly by its height.
- **`scale()` scales children too:** Font sizes and icons scale proportionally on button press. This is a feature.
- **`preserve-3d`:** Use `rotateX()`, `rotateY()` with `transform-style: preserve-3d` for genuine depth effects without JS.

### 4.7 `clip-path` for Animation
- **The inset shape:** `clip-path: inset(0 100% 0 0)` eats into the element from the right.
- **Tabs:** Duplicate the list, style as active, clip to show only the active one, and animate the clip. Perfect color transition.
- **Hold-to-delete:** Transition `inset(0 100% 0 0)` to `inset(0 0 0 0)` over 2s linear on `:active`. Snap back on release.
- **Scroll reveal:** Animate from `inset(0 0 100% 0)` to `inset(0 0 0 0)` on enter viewport.

### 4.8 Gesture and Drag Interactions
- **Momentum-based dismissal:** If velocity > 0.11, dismiss regardless of distance.
- **Damping at boundaries:** Apply friction when dragging past the natural boundary.
- **Pointer capture:** Set element to capture all pointer events during drag.
- **Multi-touch protection:** Ignore additional touch points after initial drag begins.

### 4.9 Performance Rules
- **Only animate `transform` and `opacity`:** These run on the GPU. Padding/margin/height triggers layout and paint.
- **CSS variables are inheritable:** Don't update variables on parents rapidly if they have many children; update `transform` on the child directly.
- **Framer Motion shorthand:** `x`, `y`, `scale` are NOT hardware-accelerated. Use `transform: "translateX()"` to push it off the main thread.
- **CSS beats JS under load:** Frame drops happen in JS during page loads. CSS animations stay smooth. Use Web Animations API (WAAPI) for JS-controlled CSS performance.

### 4.10 Accessibility
- **prefers-reduced-motion:** Remove motion/transform. Keep opacity and color transitions for comprehension.
- **Touch device hovers:** Gate hovers behind `@media (hover: hover) and (pointer: fine)` to avoid sticky states on mobile tap.

### 4.11 The Sonner Principles
1. Developer experience is key.
2. Good defaults matter more than options.
3. Naming creates identity ("Sonner" > "react-toast").
4. Handle edge cases invisibly (pause timers when tab hidden).
5. Use transitions, not keyframes, for dynamic UI.

**Asymmetric Timing:** Pressing should be slow and deliberate (e.g., 2s linear). Release should always be snappy (200ms ease-out).
**Stagger Animations:** Delay items 30-80ms for a cascading entry effect.

### 4.12 Debugging Animations
- **Slow motion testing:** Play at 2-5x slower. Do colors crossfade cleanly? Is the easing right?
- **Frame-by-frame:** Step through in Chrome DevTools Animations panel to catch sync issues.
- **Real devices:** For touch/drawers, test on a physical phone, not just the Xcode Simulator.
