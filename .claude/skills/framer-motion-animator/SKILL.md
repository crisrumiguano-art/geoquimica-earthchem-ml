---
name: framer-motion-animator
description: Ultimate skill for web animation, 3D experiences, micro-interactions, and Claude.ai artifact generation. Combines Framer Motion, Anime.js, React Three Fiber, scroll-driven motion (scroll-telling), and artifact building constraints.
---

# Web Animation & 3D Artifacts Architect

This skill consolidates comprehensive guidelines for building high-fidelity web animations, 3D experiences, scroll-telling interactions, and Claude.ai HTML artifacts. It fuses the knowledge of 7 previous modular skills.

---

## 1. General Animation Strategy (`animate`)

Analyze a feature and strategically add animations and micro-interactions that enhance understanding, provide feedback, and create delight.

### MANDATORY PREPARATION

Invoke /impeccable — it contains design principles, anti-patterns, and the **Context Gathering Protocol**. Follow the protocol before proceeding — if no design context exists yet, you MUST run /impeccable teach first. Additionally gather: performance constraints.

### Assess Animation Opportunities

Analyze where motion would improve the experience:

1. **Identify static areas**:
   - **Missing feedback**: Actions without visual acknowledgment (button clicks, form submission, etc.)
   - **Jarring transitions**: Instant state changes that feel abrupt (show/hide, page loads, route changes)
   - **Unclear relationships**: Spatial or hierarchical relationships that aren't obvious
   - **Lack of delight**: Functional but joyless interactions
   - **Missed guidance**: Opportunities to direct attention or explain behavior

2. **Understand the context**:
   - What's the personality? (Playful vs serious, energetic vs calm)
   - What's the performance budget? (Mobile-first? Complex page?)
   - Who's the audience? (Motion-sensitive users? Power users who want speed?)
   - What matters most? (One hero animation vs many micro-interactions?)

If any of these are unclear from the codebase, ask the user directly to clarify what you cannot infer.

**CRITICAL**: Respect `prefers-reduced-motion`. Always provide non-animated alternatives for users who need them.

### Plan Animation Strategy

Create a purposeful animation plan:

- **Hero moment**: What's the ONE signature animation? (Page load? Hero section? Key interaction?)
- **Feedback layer**: Which interactions need acknowledgment?
- **Transition layer**: Which state changes need smoothing?
- **Delight layer**: Where can we surprise and delight?

**IMPORTANT**: One well-orchestrated experience beats scattered animations everywhere. Focus on high-impact moments.

### Implement Animations

Add motion systematically across these categories:

#### Entrance Animations
- **Page load choreography**: Stagger element reveals (100-150ms delays), fade + slide combinations
- **Hero section**: Dramatic entrance for primary content (scale, parallax, or creative effects)
- **Content reveals**: Scroll-triggered animations using intersection observer
- **Modal/drawer entry**: Smooth slide + fade, backdrop fade, focus management

#### Micro-interactions
- **Button feedback**:
  - Hover: Subtle scale (1.02-1.05), color shift, shadow increase
  - Click: Quick scale down then up (0.95 → 1), ripple effect
  - Loading: Spinner or pulse state
- **Form interactions**:
  - Input focus: Border color transition, slight scale or glow
  - Validation: Shake on error, check mark on success, smooth color transitions
- **Toggle switches**: Smooth slide + color transition (200-300ms)
- **Checkboxes/radio**: Check mark animation, ripple effect
- **Like/favorite**: Scale + rotation, particle effects, color transition

#### State Transitions
- **Show/hide**: Fade + slide (not instant), appropriate timing (200-300ms)
- **Expand/collapse**: Height transition with overflow handling, icon rotation
- **Loading states**: Skeleton screen fades, spinner animations, progress bars
- **Success/error**: Color transitions, icon animations, gentle scale pulse
- **Enable/disable**: Opacity transitions, cursor changes

#### Navigation & Flow
- **Page transitions**: Crossfade between routes, shared element transitions
- **Tab switching**: Slide indicator, content fade/slide
- **Carousel/slider**: Smooth transforms, snap points, momentum
- **Scroll effects**: Parallax layers, sticky headers with state changes, scroll progress indicators

#### Feedback & Guidance
- **Hover hints**: Tooltip fade-ins, cursor changes, element highlights
- **Drag & drop**: Lift effect (shadow + scale), drop zone highlights, smooth repositioning
- **Copy/paste**: Brief highlight flash on paste, "copied" confirmation
- **Focus flow**: Highlight path through form or workflow

#### Delight Moments
- **Empty states**: Subtle floating animations on illustrations
- **Completed actions**: Confetti, check mark flourish, success celebrations
- **Easter eggs**: Hidden interactions for discovery
- **Contextual animation**: Weather effects, time-of-day themes, seasonal touches

### Technical Implementation

Use appropriate techniques for each animation:

#### Timing & Easing

**Durations by purpose:**
- **100-150ms**: Instant feedback (button press, toggle)
- **200-300ms**: State changes (hover, menu open)
- **300-500ms**: Layout changes (accordion, modal)
- **500-800ms**: Entrance animations (page load)

**Easing curves (use these, not CSS defaults):**
```css
/* Recommended - natural deceleration */
--ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);    /* Smooth, refined */
--ease-out-quint: cubic-bezier(0.22, 1, 0.36, 1);   /* Slightly snappier */
--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);     /* Confident, decisive */

/* AVOID - feel dated and tacky */
/* bounce: cubic-bezier(0.34, 1.56, 0.64, 1); */
/* elastic: cubic-bezier(0.68, -0.6, 0.32, 1.6); */
```

**Exit animations are faster than entrances.** Use ~75% of enter duration.

#### CSS Animations
```css
/* Prefer for simple, declarative animations */
- transitions for state changes
- @keyframes for complex sequences
- transform + opacity only (GPU-accelerated)
```

#### JavaScript Animation
```javascript
/* Use for complex, interactive animations */
- Web Animations API for programmatic control
- Framer Motion for React
- GSAP for complex sequences
```

#### Performance
- **GPU acceleration**: Use `transform` and `opacity`, avoid layout properties
- **will-change**: Add sparingly for known expensive animations
- **Reduce paint**: Minimize repaints, use `contain` where appropriate
- **Monitor FPS**: Ensure 60fps on target devices

#### Accessibility
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**NEVER**:
- Use bounce or elastic easing curves—they feel dated and draw attention to the animation itself
- Animate layout properties (width, height, top, left)—use transform instead
- Use durations over 500ms for feedback—it feels laggy
- Animate without purpose—every animation needs a reason
- Ignore `prefers-reduced-motion`—this is an accessibility violation
- Animate everything—animation fatigue makes interfaces feel exhausting
- Block interaction during animations unless intentional

### Verify Quality

Test animations thoroughly:

- **Smooth at 60fps**: No jank on target devices
- **Feels natural**: Easing curves feel organic, not robotic
- **Appropriate timing**: Not too fast (jarring) or too slow (laggy)
- **Reduced motion works**: Animations disabled or simplified appropriately
- **Doesn't block**: Users can interact during/after animations
- **Adds value**: Makes interface clearer or more delightful

Remember: Motion should enhance understanding and provide feedback, not just add decoration. Animate with purpose, respect performance constraints, and always consider accessibility. Great animation is invisible - it just makes everything feel right.

---

## 2. Framer Motion Integration (`framer-motion-animator`)

Build delightful animations and interactions with Framer Motion's declarative API.

### Core Workflow

1. **Identify animation needs**: Entrance, exit, hover, gestures
2. **Choose animation type**: Simple, variants, gestures, layout
3. **Define motion values**: Opacity, scale, position, rotation
4. **Add transitions**: Duration, easing, spring physics
5. **Orchestrate sequences**: Stagger, delay, parent-child
6. **Optimize performance**: GPU-accelerated properties

### Installation

```bash
npm install framer-motion
```

### Basic Animations

#### Simple Animation

```tsx
import { motion } from 'framer-motion';

// Animate on mount
export function FadeIn({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {children}
    </motion.div>
  );
}

// Animate on hover
export function ScaleOnHover({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
    >
      {children}
    </motion.div>
  );
}
```

#### Exit Animations with AnimatePresence

```tsx
import { motion, AnimatePresence } from 'framer-motion';

export function Modal({ isOpen, onClose, children }: ModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 z-40"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed inset-0 z-50 flex items-center justify-center"
          >
            <div className="bg-white rounded-xl p-6 max-w-md w-full">
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
```

### Variants Pattern

#### Staggered Children

```tsx
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { type: 'spring', stiffness: 300, damping: 24 },
  },
};

export function StaggeredList({ items }: { items: string[] }) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {items.map((item, index) => (
        <motion.li key={index} variants={itemVariants}>
          {item}
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

#### Interactive Variants

```tsx
const buttonVariants = {
  initial: { scale: 1 },
  hover: { scale: 1.05 },
  tap: { scale: 0.95 },
  disabled: { opacity: 0.5, scale: 1 },
};

export function AnimatedButton({
  children,
  disabled,
  onClick,
}: ButtonProps) {
  return (
    <motion.button
      variants={buttonVariants}
      initial="initial"
      whileHover={disabled ? 'disabled' : 'hover'}
      whileTap={disabled ? 'disabled' : 'tap'}
      animate={disabled ? 'disabled' : 'initial'}
      onClick={onClick}
      disabled={disabled}
      className="px-4 py-2 bg-blue-500 text-white rounded-lg"
    >
      {children}
    </motion.button>
  );
}
```

### Page Transitions

#### Next.js App Router

```tsx
// app/template.tsx
'use client';

import { motion } from 'framer-motion';

export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  );
}
```

#### Shared Layout Animations

```tsx
import { motion, LayoutGroup } from 'framer-motion';

export function Tabs({ tabs, activeTab, onTabChange }: TabsProps) {
  return (
    <LayoutGroup>
      <div className="flex gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className="relative px-4 py-2"
          >
            {activeTab === tab.id && (
              <motion.div
                layoutId="activeTab"
                className="absolute inset-0 bg-blue-500 rounded-lg"
                transition={{ type: 'spring', stiffness: 500, damping: 30 }}
              />
            )}
            <span className="relative z-10">{tab.label}</span>
          </button>
        ))}
      </div>
    </LayoutGroup>
  );
}
```

### Gesture Animations

#### Drag

```tsx
export function DraggableCard() {
  return (
    <motion.div
      drag
      dragConstraints={{ left: -100, right: 100, top: -100, bottom: 100 }}
      dragElastic={0.2}
      dragTransition={{ bounceStiffness: 600, bounceDamping: 20 }}
      whileDrag={{ scale: 1.1, cursor: 'grabbing' }}
      className="w-32 h-32 bg-blue-500 rounded-lg cursor-grab"
    />
  );
}
```

#### Swipe to Dismiss

```tsx
export function SwipeToDelete({ onDelete, children }: SwipeProps) {
  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      onDragEnd={(_, info) => {
        if (info.offset.x < -100) {
          onDelete();
        }
      }}
      className="relative"
    >
      {children}
      <motion.div
        className="absolute right-0 inset-y-0 bg-red-500 flex items-center px-4"
        style={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        Delete
      </motion.div>
    </motion.div>
  );
}
```

### Scroll Animations

#### Scroll-Triggered

```tsx
import { motion, useInView } from 'framer-motion';
import { useRef } from 'react';

export function FadeInWhenVisible({ children }: { children: React.ReactNode }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  );
}
```

#### Scroll Progress

```tsx
import { motion, useScroll, useTransform } from 'framer-motion';

export function ParallaxHero() {
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 500], [0, 150]);
  const opacity = useTransform(scrollY, [0, 300], [1, 0]);

  return (
    <motion.div
      style={{ y, opacity }}
      className="h-screen flex items-center justify-center"
    >
      <h1 className="text-6xl font-bold">Parallax Hero</h1>
    </motion.div>
  );
}

export function ScrollProgress() {
  const { scrollYProgress } = useScroll();

  return (
    <motion.div
      style={{ scaleX: scrollYProgress }}
      className="fixed top-0 left-0 right-0 h-1 bg-blue-500 origin-left z-50"
    />
  );
}
```

### Animation Hooks

#### useAnimate (Imperative)

```tsx
import { useAnimate } from 'framer-motion';

export function SubmitButton() {
  const [scope, animate] = useAnimate();

  const handleClick = async () => {
    // Sequence of animations
    await animate(scope.current, { scale: 0.95 }, { duration: 0.1 });
    await animate(scope.current, { scale: 1 }, { type: 'spring' });

    // Success animation
    await animate(
      scope.current,
      { backgroundColor: '#22c55e' },
      { duration: 0.2 }
    );
  };

  return (
    <motion.button ref={scope} onClick={handleClick} className="px-4 py-2">
      Submit
    </motion.button>
  );
}
```

#### useMotionValue & useTransform

```tsx
import { motion, useMotionValue, useTransform } from 'framer-motion';

export function RotatingCard() {
  const x = useMotionValue(0);
  const rotateY = useTransform(x, [-200, 200], [-45, 45]);
  const opacity = useTransform(x, [-200, 0, 200], [0.5, 1, 0.5]);

  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: -200, right: 200 }}
      style={{ x, rotateY, opacity }}
      className="w-64 h-96 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl"
    />
  );
}
```

### Reusable Animation Components

#### AnimatedContainer

```tsx
// components/AnimatedContainer.tsx
import { motion, Variants } from 'framer-motion';

const animations: Record<string, Variants> = {
  fadeIn: {
    hidden: { opacity: 0 },
    visible: { opacity: 1 },
  },
  fadeInUp: {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  },
  fadeInDown: {
    hidden: { opacity: 0, y: -20 },
    visible: { opacity: 1, y: 0 },
  },
  scaleIn: {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { opacity: 1, scale: 1 },
  },
  slideInLeft: {
    hidden: { opacity: 0, x: -50 },
    visible: { opacity: 1, x: 0 },
  },
  slideInRight: {
    hidden: { opacity: 0, x: 50 },
    visible: { opacity: 1, x: 0 },
  },
};

interface AnimatedContainerProps {
  children: React.ReactNode;
  animation?: keyof typeof animations;
  delay?: number;
  duration?: number;
  className?: string;
}

export function AnimatedContainer({
  children,
  animation = 'fadeInUp',
  delay = 0,
  duration = 0.5,
  className,
}: AnimatedContainerProps) {
  return (
    <motion.div
      variants={animations[animation]}
      initial="hidden"
      animate="visible"
      transition={{ duration, delay, ease: 'easeOut' }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
```

#### AnimatedList

```tsx
// components/AnimatedList.tsx
import { motion } from 'framer-motion';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: { opacity: 1, x: 0 },
};

interface AnimatedListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  keyExtractor: (item: T, index: number) => string;
  className?: string;
}

export function AnimatedList<T>({
  items,
  renderItem,
  keyExtractor,
  className,
}: AnimatedListProps<T>) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className={className}
    >
      {items.map((item, index) => (
        <motion.li key={keyExtractor(item, index)} variants={itemVariants}>
          {renderItem(item, index)}
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

### Transition Presets

```tsx
// lib/transitions.ts
export const transitions = {
  spring: {
    type: 'spring',
    stiffness: 300,
    damping: 24,
  },
  springBouncy: {
    type: 'spring',
    stiffness: 500,
    damping: 15,
  },
  springStiff: {
    type: 'spring',
    stiffness: 700,
    damping: 30,
  },
  smooth: {
    type: 'tween',
    duration: 0.3,
    ease: 'easeInOut',
  },
  snappy: {
    type: 'tween',
    duration: 0.15,
    ease: [0.25, 0.1, 0.25, 1],
  },
} as const;

// Usage
<motion.div transition={transitions.spring} />
```

### Reduced Motion Support

```tsx
import { useReducedMotion } from 'framer-motion';

export function AccessibleAnimation({ children }: { children: React.ReactNode }) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: shouldReduceMotion ? 0 : 0.5 }}
    >
      {children}
    </motion.div>
  );
}
```

### Best Practices

1. **Use GPU-accelerated properties**: `opacity`, `transform` (not `width`, `height`)
2. **Add `layout` for smooth resizing**: Automatic layout animations
3. **Use `AnimatePresence`**: For exit animations
4. **Prefer springs**: More natural than tween for UI
5. **Respect reduced motion**: Use `useReducedMotion` hook
6. **Avoid animating layout thrashing**: Don't animate `top`, `left`, `width`
7. **Use `layoutId`**: For shared element transitions
8. **Stagger children**: For list animations

### Output Checklist

Every animation implementation should include:

- [ ] Appropriate animation type (simple, variants, gestures)
- [ ] Smooth transitions with proper easing
- [ ] Exit animations with AnimatePresence
- [ ] Reduced motion support
- [ ] GPU-accelerated properties only
- [ ] Spring physics for natural feel
- [ ] Staggered children for lists
- [ ] Performance tested on low-end devices

---

## 3. Anime.js v4 Animation Skill (`animejs-animation`)

[Anime.js](https://animejs.com/) is a lightweight but powerful JavaScript animation engine. It works with CSS properties, SVG, DOM attributes, and JavaScript objects, and is especially strong for complex timelines, staggering, scroll-linked motion, SVG drawing, morphing, and precise choreography.

### Context

Use this section to create high-fidelity, modern, expressive web animations that go beyond simple CSS transitions. Anime.js is the tool of choice when motion needs to feel bespoke, fluid, responsive, and carefully orchestrated.

Trigger these workflows when:
- Creating complex, multi-stage landing page or product-page orchestrations.
- Implementing staggered animations for revealing grids, text, cards, lists, charts, or data visualizations.
- Animating SVG paths, including line drawing, morphing shapes, or dynamic motion paths.
- Building interactive kinetic UI elements that respond fluidly to user input.
- Creating scroll-based, timeline-based, draggable, spring, keyframe, or JavaScript-controlled animation.

### Installation

**NPM**
```bash
npm install animejs
```

**ES Modules**
```javascript
import { animate } from 'animejs';
```

**CDN, ES Modules**
```javascript
import { animate } from 'https://esm.sh/animejs';
```

### Core Concepts

Anime.js v4 is modular and tree-shakeable. Import only what the project needs.

```javascript
import { animate, createTimeline, stagger, createDraggable } from 'animejs';
import { animate } from 'animejs/animation';
import { createTimeline } from 'animejs/timeline';
import { createTimer } from 'animejs/timer';
```

### Execution Workflow

1. **Identify animation purpose**: Decide what the motion communicates: reveal, focus, continuity, feedback, spatial movement, delight, or state change.
2. **Identify targets**: Select DOM elements, SVG nodes, attributes, CSS variables, or JavaScript objects to animate.
3. **Choose the right primitive**:
   - Use `animate()` for direct animations.
   - Use `createTimeline()` for multi-stage choreography.
   - Use `stagger()` for rhythmic multi-element reveals.
   - Use `onScroll()` for scroll-linked motion.
   - Use SVG utilities for drawing, morphing, or motion paths.
   - Use `createDraggable()` for physical drag interactions.
4. **Define properties and easing**: Prefer refined easing such as spring, elastic, cubic bezier, or expressive built-ins. Avoid defaulting to `linear` or generic `ease-in-out` unless it is intentional.
5. **Orchestrate timelines**: Use timeline offsets, labels, and overlapping stages so motion feels seamless rather than sequential and mechanical.
6. **Respect accessibility**: Account for reduced motion preferences and keep motion supportive rather than disorienting.
7. **Optimize performance**: Prefer transform and opacity, avoid unnecessary layout thrashing, and add `will-change` only where it helps.
8. **Validate in context**: Test the animation in the actual page or component, including responsive layouts and repeated interactions.

### Creative Timeline Example

```javascript
import { createTimeline, stagger } from 'animejs';

const tl = createTimeline({
  defaults: {
    duration: 1000,
    ease: 'outExpo',
  },
});

tl.add('.hero-text > *', {
  translateY: [48, 0],
  opacity: [0, 1],
  delay: stagger(90),
})
  .add(
    '.hero-image',
    {
      scale: [0.92, 1],
      opacity: [0, 1],
      filter: ['blur(12px)', 'blur(0px)'],
    },
    '-=760',
  )
  .add(
    '.hero-action',
    {
      translateY: [16, 0],
      opacity: [0, 1],
    },
    '-=520',
  );
```

### Quick Reference

**Basic Animation**
```javascript
import { animate } from 'animejs';

animate('.element', {
  translateX: 250,
  rotate: '1turn',
  duration: 800,
  ease: 'outExpo',
});
```

**Timeline**
```javascript
import { createTimeline } from 'animejs';

const tl = createTimeline({ defaults: { duration: 500 } });

tl.add('.box1', { x: 100 })
  .add('.box2', { x: 100 }, '<')
  .add('.box3', { x: 100 }, '-=200');
```

**Stagger**
```javascript
import { animate, stagger } from 'animejs';

animate('.item', {
  translateY: [-20, 0],
  opacity: [0, 1],
  delay: stagger(100, { from: 'center' }),
  duration: 600,
});
```

**Scroll Animation**
```javascript
import { animate, onScroll } from 'animejs';

animate('.element', {
  translateX: [0, 500],
  autoplay: onScroll({
    target: '.element',
    sync: true,
  }),
});
```

**SVG Line Drawing**
```javascript
import { animate, createDrawable } from 'animejs';

animate(createDrawable('path'), {
  draw: ['0 0', '0 1'],
  duration: 2000,
  ease: 'inOutQuad',
});
```

**Draggable**
```javascript
import { createDraggable, createSpring } from 'animejs';

createDraggable('.draggable', {
  container: '.container',
  releaseEase: createSpring({ stiffness: 200, damping: 20 }),
});
```

**Keyframes**
```javascript
import { animate } from 'animejs';

animate('.element', {
  translateX: [
    { to: 100, duration: 500 },
    { to: 0, duration: 500, delay: 200 },
  ],
  rotate: ['0turn', '1turn', '0turn'],
});
```

### React Integration

Use `createScope()` to scope animations to a component and clean them up on unmount.

```jsx
import { useEffect, useRef } from 'react';
import { animate, createScope } from 'animejs';

function AnimatedComponent() {
  const root = useRef(null);
  const scope = useRef(null);

  useEffect(() => {
    scope.current = createScope({ root: root.current }).add(() => {
      animate('.box', { rotate: 360 });
    });

    return () => scope.current.revert();
  }, []);

  return (
    <div ref={root}>
      <div className="box" />
    </div>
  );
}
```

### Documentation Sitemap

#### Animation, `animate`
- Targets: CSS selectors, DOM elements, JavaScript objects, and arrays of targets.
- Properties: CSS properties, transforms, CSS variables, JavaScript object properties, HTML attributes, and SVG attributes.
- Tween values: numerical values, unit conversion, relative values, colors, color functions, CSS variables, and function-based values.

#### Timeline, `createTimeline`
- Add timers, animations, WAAPI animations, synced timelines, and function calls.
- Time positions: absolute milliseconds, relative positions (`<`, `>`, `+=`, `-=`), and labels.

#### Utilities
- `stagger()` for time, value, and timeline staggering with grid support.
- `$()` query selector utility.
- `mapRange()`, `lerp()`, `damp()` for interpolation.
- `createSpring({ stiffness, damping, mass, velocity })`.

### Strict Rules
- Use `stagger()` extensively for groups of elements so motion has organic rhythm.
- Clean up animations in component frameworks to avoid leaks and stale DOM references.
- For simple state changes, CSS transitions may be sufficient; use Anime.js when the complexity, choreography, or interaction quality justifies it.

---

## 4. Web 3D Experiences & Scroll-telling (`web-3d-artifacts` & `3d-web-experience`)

Expertise in building 3D experiences for the web - Three.js, React Three Fiber, Spline, WebGL, and interactive 3D scenes. Covers product configurators, 3D portfolios, immersive websites, and bringing depth to web experiences.

### Stack Selection

Choosing the right 3D approach:

| Tool | Best For | Learning Curve | Control |
|------|----------|----------------|---------|
| **Spline** | Quick prototypes, designers | Low | Medium |
| **React Three Fiber (R3F)** | React apps, complex scenes | Medium | High |
| **Three.js vanilla** | Max control, non-React | High | Maximum |

### Prototipado vs. Integración en Proyectos
- **Para prototipado rápido:** Genera SIEMPRE un único archivo HTML autónomo (`index.html`) que contenga todo el código necesario usando import maps y Babel en el navegador.
- **Para proyectos existentes (ej. Next.js, React Vite):** Intégrate a la arquitectura del proyecto generando componentes modulares listos para producción (ej. separando la escena y el contenedor).

### Patrón recomendado para Scroll-Telling integrado (R3F)

```tsx
"use client";
import React, { useEffect, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Environment, PerspectiveCamera } from "@react-three/drei";
import * as THREE from "three";

function MyModel({ progressRef }: { progressRef: React.MutableRefObject<number> }) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    if (!meshRef.current) return;
    const p = progressRef.current; // Va de 0 a 1
    
    // Mapear el progreso del scroll a propiedades 3D
    meshRef.current.position.x = -10 + (p * 20); // Avanza de -10 a 10
    meshRef.current.rotation.y = p * Math.PI * 2; // Rota 360 grados
  });

  return (
    <mesh ref={meshRef} castShadow>
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial color="#f59e0b" roughness={0.5} metalness={0.8} />
    </mesh>
  );
}

function Scene({ progressRef }: { progressRef: React.MutableRefObject<number> }) {
  return (
    <>
      <PerspectiveCamera makeDefault position={[0, 0, 10]} />
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 10]} intensity={2} castShadow />
      <MyModel progressRef={progressRef} />
      <Environment preset="city" />
    </>
  );
}

export function ScrollArtifact() {
  const containerRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef(0);

  useEffect(() => {
    let ticking = false;
    const onScroll = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          if (!containerRef.current) return;
          const rect = containerRef.current.getBoundingClientRect();
          const scrollable = containerRef.current.offsetHeight - window.innerHeight;
          let p = 0;
          if (rect.top <= 0 && scrollable > 0) {
            p = Math.abs(rect.top) / scrollable;
          }
          progressRef.current = Math.max(0, Math.min(1, p));
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    onScroll();

    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, []);

  return (
    <div ref={containerRef} className="relative w-full" style={{ height: "300vh" }}>
      {/* Viewport estático que atrapa el Canvas */}
      <div className="sticky top-0 w-full h-screen overflow-hidden bg-black">
        <div className="absolute inset-0 z-0">
          <Canvas shadows dpr={[1, 2]}>
            <Scene progressRef={progressRef} />
          </Canvas>
        </div>
        {/* Contenido HTML Overlay */}
        <div className="pointer-events-none absolute inset-0 z-10 p-10 text-white">
          <h1 className="text-4xl font-bold">Título Overlay</h1>
        </div>
      </div>
    </div>
  );
}
```

### 3D Model Pipeline & Optimization

Getting models web-ready:

1. Model in Blender/etc
2. Reduce poly count (< 100K for web)
3. Bake textures (combine materials)
4. Export as GLB
5. Compress with gltf-transform
6. Test file size (< 5MB ideal)

**GLTF Compression**
```bash
npm install -g @gltf-transform/cli
gltf-transform optimize input.glb output.glb \
  --compress draco \
  --texture-compress webp
```

### 3D Performance Targets
- **Desktop:** 60fps, Max Triangles 500K
- **Mobile:** 30-60fps, Max Triangles 100K

### Mejores Prácticas y Calidad Visual
- **Lighting:** Usa `Environment` de Drei junto con una `directionalLight` para crear luces dramáticas. Utiliza `ContactShadows` bajo los objetos para anclarlos al suelo visualmente sin costo computacional elevado.
- **Generación de Formas Orgánicas:** Si te piden "un sólido, una piedra o una masa informe", no instancies cientos de cubos. Genera una `IcosahedronGeometry`, lee sus vértices y aplícales funciones senos y cosenos (ruido procedural simple) para deformar la malla en el `useMemo`.
- **Rendimiento:** Evita realizar llamadas DOM dentro del render loop (useFrame). Usa referencias mutables (`useRef`) para pasar el progreso del scroll al entorno de React Three Fiber y mutar las propiedades directamente (`ref.current.rotation.x = ...`).

---

## 5. Web Scroll Down (Image Sequence Stop-Motion)

This section covers high-performance scroll animation using an image sequence. As the user scrolls down, the script maps the scroll progress to a sequence of pre-rendered images, creating a smooth video-like effect similar to Apple product pages.

### HTML & CSS Structure

```html
<main>
    <div class="scroll-container">
        <img id="animation-frame" src="frames/001.webp" alt="Scroll Animation">
    </div>
</main>
```

```css
main {
    /* The height determines how long the scroll animation lasts */
    height: 3000px;
}
.scroll-container {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1;
}
#animation-frame {
    width: 100%; height: 100%; object-fit: cover; object-position: center;
}
```

### JavaScript Logic (`main.js`)

```javascript
const frameImage = document.getElementById('animation-frame');

// 1. Configuration
const totalFrames = 151;
const framesDir = 'frames';
const framePrefix = 'frame_';
const frameExt = '.webp';

// 2. Preload Images (CRITICAL)
const images = [];
function preloadImages() {
    for (let i = 1; i <= totalFrames; i++) {
        const img = new Image();
        const frameNumber = i.toString().padStart(3, '0');
        img.src = `${framesDir}/${framePrefix}${frameNumber}${frameExt}`;
        images.push(img);
    }
}
preloadImages();

// 3. Scroll Logic
let currentFrame = 1;

function updateFrame(frameIndex) {
    const validFrame = Math.min(Math.max(frameIndex, 1), totalFrames);
    if (currentFrame !== validFrame) {
        currentFrame = validFrame;
        const frameNumber = currentFrame.toString().padStart(3, '0');
        frameImage.src = `${framesDir}/${framePrefix}${frameNumber}${frameExt}`;
    }
}

window.addEventListener('scroll', () => {
    const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    if (maxScroll <= 0) return; 

    const scrollFraction = window.scrollY / maxScroll;
    const frameIndex = Math.ceil(scrollFraction * totalFrames);
    
    // Optimization: Use requestAnimationFrame for smoother updates
    requestAnimationFrame(() => updateFrame(frameIndex));
});
```

### Best Practices and Optimizations
- **Use `.webp` format:** Use WebP images instead of JPEG or Base64. A sequence of 150 JPEG images can weigh 17MB, whereas WebP can reduce this to 3-4MB without losing quality. Avoid base64 encoded images at all costs for this effect as they block the main thread and massively inflate bundle size.
- **Preload aggressively:** Always preload the images using `new Image()`. If images are not preloaded, the browser will have to fetch them during the scroll event, causing white flashes or "petardeo" (glitching).
- **Throttling/Debouncing:** If calculations inside the scroll event get heavy, strictly use `requestAnimationFrame` to batch rendering.

---

## 6. Claude.ai Web Artifacts Builder

Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX artifacts.

### Design & Style Guidelines

**VERY IMPORTANT:** To avoid what is often referred to as "AI slop", avoid using excessive centered layouts, purple gradients, uniform rounded corners, and Inter font.

### Artifact Build Flow

1. Initialize the frontend repo using `scripts/init-artifact.sh`
   ```bash
   bash scripts/init-artifact.sh <project-name>
   cd <project-name>
   ```
   *(Creates a Vite + React + TS + Tailwind + shadcn project with Parcel bundler)*

2. Develop your artifact by editing the generated code inside `/src`.

3. Bundle all code into a single HTML file using `scripts/bundle-artifact.sh`
   ```bash
   bash scripts/bundle-artifact.sh
   ```
   *(Creates `bundle.html` - a self-contained artifact with all JavaScript, CSS, and dependencies inlined using html-inline)*

4. **Display artifact to user**: Share the bundled `bundle.html` file in conversation.

### Testing/Visualizing the Artifact (Optional)

To test/visualize the artifact, use available tools (including other Skills or built-in tools like Playwright or Puppeteer). In general, avoid testing the artifact upfront as it adds latency between the request and when the finished artifact can be seen. Test later, after presenting the artifact, if requested or if issues arise.
