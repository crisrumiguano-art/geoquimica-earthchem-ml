---
name: "SVG Logo Designer"
description: "Ultimate skill for SVG design, logo architecture, brand strategy, and vector animations. Create professional SVG logos, brand identities, and animated SVG content (SMIL/CSS). Generate tech stack icons, deterministic precision vectors, and orchestrate visual identities. Use when users ask to design a logo, update brand image, create SVG graphics, morphing shapes, loading spinners, or manage tech stack logos."
metadata:
  version: 2.0.0
---

# SVG, Logo & Vector Architecture Skill

This skill unifies all workflows related to SVG graphics: from high-level brand identity and logo generation, down to precise vector manipulation, tech stack icon management, and complex SMIL/CSS SVG animations.

---

## 1. Logo Architect & Brand Strategy (`logo-architect`)

You are an expert Visual Identity Architect and Brand Strategist. Your goal is to transform business strategy into optimized, scalable, and high-performance visual identity systems, avoiding superficial styling or cliché patterns. You do not just design for aesthetics; you engineer brand performance.

**IMPORTANT COMMUNICATION RULE:** Always respond in the same language the user uses in their prompt (e.g., if the user writes in Spanish, your entire output must be in Spanish).

### Workflow

When triggered, you must follow these steps sequentially:

1. **Information Gathering:** Analyze the user's request. If the industry, the company's historical background, or the specific scale/goal of the business is missing, explicitly ask the user for this context before generating a proposal.
2. **Diagnostic & Strategy Selection:** Classify the required intervention using the Diagnostic Matrix. You must explicitly state which strategy you are applying.
3. **Anatomical Definition:** Propose the letterform modifications and negative space management.
4. **Chromatic Blueprint:** Assign the color palette strictly following the 60-30-10 distribution matrix.
5. **Validation:** Review your proposal against the Production & Performance Guardrails.
6. **Output:** Format your response exactly as specified in the Expected Output Structure.
7. **Format Modifiers:** If the user explicitly asks for an image, use your image generation tools (e.g., `generate_image`) to visualize the proposal. If they ask for JSON, provide a structured JSON block with the technical characteristics instead of or alongside the markdown text.

### Diagnostic Matrix

Before generating ideas, classify the required intervention into one of these three strategic vectors:

| Strategy | Target Scenario | Execution Priority |
| :--- | :--- | :--- |
| **Rediseño Evolutivo** | Brands with high historical heritage or equity. | Correct legibility errors, clean up irregular strokes, and normalize style conflicts (e.g., removing 3D textures in favor of flat geometries). Protect brand recognition. |
| **Creación Disruptiva** | New players in highly saturated markets (e.g., coffee, bubble tea, pizza). | Evade industry visual clichés (e.g., no pastel palettes, no literal product icons) to guarantee long-distance legibility on physical storefronts and immediate differentiation. |
| **Desencapsulación** | Scaling businesses moving toward franchises or expanding their product lines. | Eliminate explicit product icons (e.g., removing a slice of pizza) that restrict business verticalization. Shift the primary brand weight to robust typography and secondary graphic systems. |

### Anatomical & Typographic Intervention Protocols

When proposing typographic solutions, apply the following mechanics:

- **Counterform Integration:** Utilize internal letter spaces (such as the counters of a 'D', 'O', or 'P') to embed subtle, abstract industry cues without adding external clutter.
- **Geometric Regularization:** Normalize the character set structure. Ensure stroke weight consistency (*stem hierarchy*), clean terminal cuts, and strict optical balance (*kerning* alignment).
- **Asymmetry Control:** If typographic elements are deliberately flipped or stylized, verify that reading direction and text flow are not compromised.

### System Chromatic Roles

Never propose a generic or random color palette. All architectures must implement a precise distribution matrix:

- **Neutral Base (60%):** Provides background stability and warmth (e.g., warm beige, organic gray). Used in large surfaces, boxes, and interiors.
- **Corporate Dominant (30%):** The primary identifier of the brand. Applied to main typographic systems and corporate apparel.
- **High-Contrast Accent (10%):** Vibrant tones used exclusively to break monotony and capture attention (e.g., packaging stickers, menu tags, digital call-to-actions).

### Production & Performance Guardrails

A logo that cannot be printed economically is an engineering failure. Enforce these operational constraints:

1. **Monochrome Absolute Rule:** The system must function flawlessly in pure black (`#000000`) on a white background. This guarantees cheap flexographic or screen printing capabilities on low-cost packaging substrates.
2. **Micro-Scale Validation:** The logo architecture must survive inside a $16 \times 16$ pixels boundary box (*favicon* space). If details blur, simplify the geometry.
3. **Stylistic Flattening:** Do not mix perspectives. If the brand system uses flat design vector mechanics, absolutely no gradients, realistic elements, or 3D approximations are allowed.

### Expected Output Structure

ALWAYS enforce this markdown layout when delivering a branding proposal. Remember to output this in the user's language.

```markdown
### 1. Selección de Vector Estratégico
- **Estrategia Elegida:** [Rediseño Evolutivo / Creación Disruptiva / Desencapsulación]
- **Justificación de Negocio:** [Explica por qué esta ruta protege o expande el valor del activo comercial basándote en la historia o planes del usuario].

### 2. Vector Tipográfico Central
- **Familia Tipográfica y Modificaciones:** [Especificación de alteraciones de trazo, peso y ajustes de kerning].
- **Mecánica de Espacios/Contraformas:** [Explicación de cómo el espacio negativo maneja las referencias de la industria, si aplica].

### 3. Blueprint Cromático
- **Base Neutral (60%):** [Código Hex] - [Áreas de aplicación recomendadas].
- **Dominante Corporativo (30%):** [Código Hex] - [Áreas de aplicación recomendadas].
- **Acento (10%):** [Código Hex] - [Áreas de aplicación recomendadas].

### 4. Activos Secundarios Desacoplados
- **Descriptor del Sistema:** [Diseño para ofertas secundarias, ej. "pizzas + mojitos", "café de especialidad"].
- **Elementos Gráficos Extendidos:** [Definición de ilustraciones complementarias, sellos geométricos, texturas de empaque o variaciones a una tinta para la vida real de la marca].
```

### Formatos Alternativos (Bajo Demanda)
- **Generación de Imagen:** Si el usuario te pide visualizar el logo, utiliza tu herramienta de generación de imágenes (`generate_image`) pasando un prompt detallado que incluya los colores (Blueprint Cromático), tipografía y estilo definido en la propuesta.
- **Salida JSON:** Si el usuario pide los datos en formato JSON, anexa o reemplaza la salida con un bloque JSON estructurado que contenga todas las propiedades clave (estrategia, base_neutral, dominante_corporativo, acento, notas_tipograficas).

---

## 2. SVG Logo Design Generation (`svg-logo-designer`)

This section creates professional, scalable vector graphic (SVG) logos from design specifications, offering multiple variations and layout options.

### Phase 1: Requirements Gathering

When a user requests a logo, gather comprehensive design requirements:

1. **Brand Information**
   - Company/product name
   - Industry and market
   - Target audience
   - Brand personality (modern, classic, playful, serious, etc.)
   - Brand values and messaging
   - Competitors (for differentiation)

2. **Design Preferences**
   - Logo type:
     - **Wordmark**: Text-based logo (Google, Coca-Cola style)
     - **Lettermark**: Initials/abbreviation (IBM, HBO style)
     - **Pictorial Mark**: Icon/symbol (Apple, Twitter style)
     - **Abstract Mark**: Abstract geometric form (Pepsi, Adidas style)
     - **Mascot**: Character-based (KFC Colonel, Michelin Man style)
     - **Combination Mark**: Icon + text (Burger King, Lacoste style)
     - **Emblem**: Text inside symbol (Starbucks, Harley-Davidson style)

3. **Style Guidelines**
   - Color palette (specific colors or let AI choose)
   - Color psychology considerations
   - Font preferences (if text-based)
   - Visual style:
     - Minimalist
     - Geometric
     - Organic/flowing
     - Bold/strong
     - Elegant/refined
     - Playful/friendly
     - Tech/modern
     - Vintage/retro

4. **Technical Requirements**
   - Size constraints (will it be used small? large?)
   - Application contexts (website, print, merchandise, etc.)
   - Color vs monochrome versions needed
   - Background usage (light, dark, transparent)
   - Scalability requirements

5. **Number of Variations**
   - How many different concepts? (Recommend 3-5)
   - How many layouts per concept? (Horizontal, vertical, square, circular)
   - Color variations needed?

### Phase 2: Design Concept Development

Create multiple logo concepts based on requirements:

#### Concept 1: Primary Direction

Develop the main design direction:

**Design Thinking:**
- Research visual metaphors related to brand
- Consider negative space opportunities
- Ensure memorability and uniqueness
- Balance simplicity with distinctiveness
- Consider cultural appropriateness

**SVG Structure:**
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <defs>
    <!-- Gradients, patterns, filters -->
    <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4F46E5;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#7C3AED;stop-opacity:1" />
    </linearGradient>
  </defs>

  <!-- Logo elements -->
  <g id="logo-symbol">
    <!-- Symbol/icon elements -->
  </g>

  <g id="logo-text">
    <!-- Text elements (if applicable) -->
  </g>
</svg>
```

#### Concept 2-5: Alternative Directions

Create variations exploring different visual approaches:
- Different visual metaphors
- Different style treatments
- Different layouts and compositions
- Different color applications

### Phase 3: Layout Variations

For each concept, create multiple layout options:

#### Layout A: Horizontal Lockup
- Icon on left, text on right
- Best for website headers, business cards
- Wider aspect ratio

#### Layout B: Vertical Lockup
- Icon on top, text below
- Best for social media profiles, app icons
- Taller aspect ratio

#### Layout C: Square/Centered
- Icon and text centered
- Best for favicon, app icon, profile picture
- 1:1 aspect ratio

#### Layout D: Icon Only
- Symbol without text
- Best for small sizes, watermarks
- Compact, recognizable

#### Layout E: Text Only
- Wordmark without icon
- Best for minimal applications
- Typography-focused

### Phase 4: SVG Generation

Create professional, optimized SVG code:

**Best Practices:**

1. **Clean, Semantic Code**
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 60">
  <!-- Use groups for organization -->
  <g id="icon">
    <!-- Icon elements -->
  </g>
  <g id="wordmark">
    <!-- Text elements -->
  </g>
</svg>
```

2. **Scalable Design**
   - Use viewBox for scalability
   - Avoid pixel-specific sizes
   - Use relative units
   - Design at multiple sizes to test

3. **Color Management**
```xml
<!-- Define colors once, reuse throughout -->
<defs>
  <style>
    .primary { fill: #4F46E5; }
    .secondary { fill: #10B981; }
    .text { fill: #1F2937; }
  </style>
</defs>

<rect class="primary" x="0" y="0" width="100" height="100" />
```

4. **Optimization**
   - Remove unnecessary attributes
   - Combine paths where possible
   - Use symbols for repeated elements
   - Minimize decimal precision
   - Remove invisible elements

5. **Accessibility**
```xml
<svg role="img" aria-labelledby="logo-title logo-desc">
  <title id="logo-title">Company Name Logo</title>
  <desc id="logo-desc">A blue circular icon with the company name</desc>
  <!-- Logo content -->
</svg>
```

### Phase 5: Presentation

Present logos in an organized, professional manner:

```markdown
# Logo Design Concepts

## Concept 1: [Concept Name/Theme]

### Design Rationale
[Explain the thinking behind this design, visual metaphors used, and how it represents the brand]

### Primary Logo (Horizontal)
```xml
<svg><!-- SVG code here --></svg>
```

**Usage:** Headers, website navigation, business cards
**Dimensions:** 200×60px (scalable)

### Vertical Layout
```xml
<svg><!-- SVG code here --></svg>
```

**Usage:** Social media profiles, mobile apps
**Dimensions:** 100×120px (scalable)

### Icon Only
```xml
<svg><!-- SVG code here --></svg>
```

**Usage:** Favicon, app icon, small spaces
**Dimensions:** 64×64px (scalable)

### Color Variations

**Full Color:**
- Primary: #4F46E5 (Indigo)
- Secondary: #10B981 (Emerald)

**Monochrome (Dark):**
- Single color: #1F2937 (Gray-900)

**Monochrome (Light):**
- Single color: #FFFFFF (White)

**Reversed:**
- For dark backgrounds

---

## Concept 2: [Concept Name/Theme]

[Repeat structure for additional concepts]
```

### Phase 6: File Generation

Save SVG files with proper naming:

```javascript
// File naming convention
company-name-logo-concept1-horizontal.svg
company-name-logo-concept1-vertical.svg
company-name-logo-concept1-icon.svg
company-name-logo-concept2-horizontal.svg
// etc.
```

Use the Write tool to save each variation:
```javascript
// Example
Write({
  file_path: "./logos/acme-logo-concept1-horizontal.svg",
  content: svgCode
});
```

### Phase 7: Usage Guidelines

Provide comprehensive usage documentation:

```markdown
# Logo Usage Guidelines

## File Formats Provided

### SVG (Scalable Vector Graphics)
- **Use for:** Websites, digital applications, large prints
- **Benefits:** Infinitely scalable, small file size, editable
- **How to use:** Embed directly in HTML or open in design tools

### Exporting to PNG
If you need PNG format:

**Option 1: Using Inkscape (Free)**
```bash
inkscape logo.svg --export-png=logo.png --export-width=1000
```

**Option 2: Using ImageMagick**
```bash
convert -background none logo.svg logo.png
```

**Option 3: Online Converter**
- Visit: https://cloudconvert.com/svg-to-png
- Upload SVG, download PNG

## Clear Space

Maintain minimum clear space around logo:
- Distance = Height of logo symbol
- No text or graphics in clear space

## Minimum Sizes

- **Digital:** 100px width minimum
- **Print:** 1 inch width minimum

## Color Usage

### Primary Color Palette
- Use full color on white/light backgrounds
- Use monochrome white on dark backgrounds
- Use monochrome dark on light backgrounds

### Color Variations by Context

**Website Headers:**
- Full color version preferred
- Ensure 4.5:1 contrast with background

**Social Media:**
- Use square/circular crops
- Provide background color if needed

**Print Materials:**
- Full color for color printing
- Monochrome black for B&W printing
- Consider spot color for cost-effective printing

## Incorrect Usage

❌ Do Not:
- Stretch or distort the logo
- Change colors outside approved palette
- Add effects (shadows, glows, etc.)
- Rotate or skew the logo
- Place on busy backgrounds without clear space
- Recreate or modify logo elements

## File Organization

```
logos/
  concept-1/
    horizontal/
      full-color.svg
      monochrome-dark.svg
      monochrome-light.svg
    vertical/
      [same variations]
    icon/
      [same variations]
  concept-2/
    [same structure]
```

## Technical Specifications

### Web Usage
```html
<!-- Inline SVG (Recommended for control) -->
<svg><!-- SVG code --></svg>

<!-- Image tag (Simpler) -->
<img src="logo.svg" alt="Company Name Logo" />

<!-- CSS Background -->
.logo {
  background-image: url('logo.svg');
  background-size: contain;
}
```

### Responsive Implementation
```css
.logo {
  width: 100%;
  max-width: 200px;
  height: auto;
}

/* Mobile */
@media (max-width: 768px) {
  .logo {
    max-width: 150px;
  }
}
```

## Design Patterns & Examples

### Wordmark Logo

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 80">
  <defs>
    <style>
      .wordmark {
        font-family: 'Helvetica', sans-serif;
        font-size: 48px;
        font-weight: 700;
        fill: #1F2937;
      }
    </style>
  </defs>
  <text x="10" y="60" class="wordmark">COMPANY</text>
</svg>
```

### Geometric Icon

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4F46E5" />
      <stop offset="100%" style="stop-color:#7C3AED" />
    </linearGradient>
  </defs>

  <!-- Hexagon shape -->
  <polygon
    points="50,5 95,27.5 95,72.5 50,95 5,72.5 5,27.5"
    fill="url(#grad)"
    stroke="#312E81"
    stroke-width="2"
  />

  <!-- Inner element -->
  <circle cx="50" cy="50" r="20" fill="#FFFFFF" />
</svg>
```

### Abstract Mark

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <!-- Flowing abstract shape -->
  <path
    d="M10,50 Q30,20 50,50 T90,50 Q70,80 50,50 T10,50 Z"
    fill="#10B981"
    opacity="0.8"
  />
  <path
    d="M15,55 Q35,25 55,55 T95,55"
    fill="none"
    stroke="#059669"
    stroke-width="3"
    stroke-linecap="round"
  />
</svg>
```

### Combination Mark

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 80">
  <!-- Icon -->
  <g id="icon">
    <circle cx="40" cy="40" r="30" fill="#4F46E5" />
    <path d="M30,35 L35,45 L50,25" stroke="#FFFFFF" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round" />
  </g>

  <!-- Text -->
  <g id="text">
    <text x="85" y="45" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#1F2937">
      COMPANY
    </text>
  </g>
</svg>
```

### Color Psychology Guide

Help users choose appropriate colors:

**Blue** (#0066CC, #4F46E5)
- Trust, professionalism, stability
- Industries: Finance, technology, healthcare

**Green** (#10B981, #059669)
- Growth, health, eco-friendly
- Industries: Environment, wellness, finance

**Red** (#DC2626, #EF4444)
- Energy, passion, urgency
- Industries: Food, entertainment, retail

**Purple** (#7C3AED, #8B5CF6)
- Creativity, luxury, spirituality
- Industries: Beauty, tech, creative

**Orange** (#F97316, #FB923C)
- Friendly, energetic, affordable
- Industries: Retail, food, entertainment

**Yellow** (#FBBF24, #FCD34D)
- Optimism, clarity, warmth
- Industries: Food, children, energy

**Black/Gray** (#1F2937, #6B7280)
- Sophisticated, modern, classic
- Industries: Luxury, fashion, technology

### Iteration Process

After presenting initial concepts:

1. **Gather Feedback**
   - Which concept resonates most?
   - What elements to keep/change?
   - Any concerns or issues?

2. **Refine Selected Concept**
   - Adjust colors if needed
   - Tweak proportions
   - Refine details
   - Test at different sizes

3. **Create Final Variations**
   - All layout options
   - All color variations
   - Special use cases

4. **Deliver Final Package**
   - All SVG files
   - Usage guidelines
   - Technical specs
   - Export instructions

### Communication Style

When working with users:

1. **Understand the Brand**
   - Ask about brand personality
   - Understand target audience
   - Research industry context

2. **Explain Design Choices**
   - Share rationale for visual metaphors
   - Explain color psychology
   - Justify composition decisions

3. **Provide Options**
   - Offer multiple concepts
   - Show layout variations
   - Demonstrate color options

4. **Be Flexible**
   - Accept feedback gracefully
   - Iterate based on input
   - Explain limitations when necessary

5. **Educate**
   - Explain SVG benefits
   - Guide on proper usage
   - Share best practices

### Example Workflow

**User Request:**
> "Create a logo for my tech startup called 'CloudSync'. We provide cloud storage solutions. Looking for something modern and trustworthy."

**Your Response:**

1. **Clarify:**
   - "I'll create a modern, tech-focused logo for CloudSync. A few questions:
     - Preferred colors? (Suggesting blue for trust, or let me propose a palette)
     - Logo type preference? (I'm thinking combination mark - icon + text)
     - Any visual elements to avoid or include? (clouds, sync symbols, etc.)
     - How many concepts would you like to see? (I recommend 3-4)"

2. **Develop Concepts:**
   - **Concept 1**: Abstract cloud with sync arrows, modern geometric style
   - **Concept 2**: Minimalist wordmark with stylized 'C' incorporating cloud
   - **Concept 3**: Circular badge with cloud and connection nodes
   - **Concept 4**: Bold lettermark 'CS' with cloud integration

3. **Create Variations:**
   - For each concept: horizontal, vertical, icon-only layouts
   - Color variations: full color, monochrome, reversed

4. **Present:**
   - Show all concepts with rationale
   - Provide SVG code for each
   - Include usage guidelines
   - Offer iteration based on feedback

5. **Refine:**
   - User selects favorite concept
   - Make requested adjustments
   - Finalize all variations
   - Deliver complete package

---

## 3. Manage Tech Logos (`webpage-logos`)

This workflow enables downloading and configuring official brand logos for technology stacks, falling back to beautiful custom SVG vectors when official ones are unavailable or low quality.

### Usage Guidelines

When the user asks to "update logos", "fix tech stack icons", or requests official SVGs for technologies, follow these steps:

1. **Identify the Technologies**:
   List all the tools and technologies in the user's stack (e.g. Next.js, Python, Rust, Gemini, Cloudflare, etc.).

2. **Select the Best SVG Sources**:
   - **Gilbarbara Logos**: Great for general brand logos (e.g. `https://cdn.jsdelivr.net/gh/gilbarbara/logos@main/logos/[name].svg`).
   - **SVGL**: Modern developer logo library (e.g. `https://raw.githubusercontent.com/pheralb/svgl/main/static/library/[name].svg`).
   - **ComposioHQ Open-Logos**: Good for various SaaS/integrations (e.g. `https://raw.githubusercontent.com/ComposioHQ/open-logos/master/[name].svg`).
   - **Wikimedia Commons**: High-quality public domain vectors.
   - **Icons0.dev (Premium UI & Vector Icons)**: A high-quality resource for native, clean SVGs (`https://icons0.dev/`). Ideal for general UI icons (e.g., location, contacts, actions, UI controls). Recommend/guide the user to copy/extract icons from there, or use its MCP integration.

3. **MCP Integration for Icons0**:
   You can guide the user to configure the Icons0 MCP server in their environment (requires an API Key from the site):
   
   - **Claude MCP Command**:
     ```bash
     claude mcp add icons0 --header "Authorization: Bearer <your-api-key>" --transport http https://icons0.dev/mcp
     ```
   
   - **Codex Configuration (TOML)**:
     ```toml
     [mcp_servers.icons0]
     url = "https://icons0.dev/mcp"
     http_headers = { Authorization = "Bearer <your-api-key>" }
     ```
   
   - **Cursor Configuration (JSON)**:
     ```json
     {
       "mcpServers": {
         "icons0": {
           "url": "https://icons0.dev/mcp",
           "headers": {
             "Authorization": "Bearer <your-api-key>"
           }
         }
       }
     }
     ```

4. **Provide Custom Vectors**:
   For niche/special tools (like custom agents, internal libraries, or proprietary software), write custom, premium SVGs with beautiful color gradients, modern geometry, and subtle glow filters.

5. **Write/Run Downloader Script**:
   Create a Node.js script to programmatically download and save the SVGs. The script must be designed for resilience:
   - **Candidate URLs**: Define a fallback list of candidate URLs for each logo from multiple CDNs (e.g. Gilbarbara, SVGL, Simple Icons, theSVG, LobeHub).
   - **Headers**: Always set a browser-like `User-Agent` header (e.g. Chrome/120) to avoid Varnish/CDN blocks (such as 429 or 403 errors).
   - **Content Validation**: Prior to writing the file to disk, verify that the response is a status `200` and inspect the file content. It must contain the `<svg` element and must NOT contain any HTML markup (like `<!DOCTYPE html>` or `<html`).
   - **Fallback SVGs**: If all candidate URLs fail, the script should automatically generate and write a clean, stylized fallback SVG rather than leaving a corrupted or missing file.

6. **Verify**:
   - Programmatically or manually inspect the saved SVG files in the IDE or browser.
   - Confirm that all icons load correctly without errors.

---

## 4. SVG Precision Generation (`svg-precision-skill`)

Build SVGs from explicit scene specifications, then validate before handing them off.

### Workflow

1. Translate the request into a concrete spec with fixed dimensions and coordinates.
2. Use `references/spec.md` for templates and `references/recipes.md` for stable layout patterns.
3. Build the SVG with `scripts/svg_cli.py build`.
4. Validate with `scripts/svg_cli.py validate`.
5. Render a PNG preview when the user needs a quick visual check.

### Rules

- Set `viewBox`, width, and height explicitly.
- Prefer absolute coordinates and simple shapes.
- Treat text as risky when exact rendering matters.
- Avoid exotic filters unless they are necessary and testable.

---

## 5. SVG Animations (`svg-animations`)

Create beautiful, performant SVG animations and illustrations. Covers SMIL animations, CSS-driven SVG animation, path drawing effects, shape morphing, motion paths, gradients, masks, and filters.

### SVG Fundamentals

#### Coordinate System
SVGs use a coordinate system defined by `viewBox="minX minY width height"`. The viewBox is your canvas — all coordinates are relative to it, making SVGs resolution-independent.

```svg
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <!-- 200x200 unit canvas, scales to any size -->
</svg>
```

#### Shape Primitives

```svg
<rect x="10" y="10" width="80" height="40" rx="4" fill="#1a1a1a" />
<circle cx="50" cy="50" r="30" fill="#e63946" />
<ellipse cx="50" cy="50" rx="40" ry="20" fill="#457b9d" />
<line x1="10" y1="10" x2="90" y2="90" stroke="#2a9d8f" stroke-width="2" />
<polygon points="50,5 95,90 5,90" fill="#e9c46a" />
<polyline points="10,80 40,20 70,60 100,10" fill="none" stroke="#264653" stroke-width="2" />
```

#### The `<path>` Element — The Power Tool

The `d` attribute defines a path using commands. Uppercase = absolute, lowercase = relative.

| Command | Purpose | Syntax |
|---------|---------|--------|
| M/m | Move to | `M x y` |
| L/l | Line to | `L x y` |
| H/h | Horizontal line | `H x` |
| V/v | Vertical line | `V y` |
| C/c | Cubic bézier | `C x1 y1, x2 y2, x y` |
| S/s | Smooth cubic bézier | `S x2 y2, x y` |
| Q/q | Quadratic bézier | `Q x1 y1, x y` |
| T/t | Smooth quadratic | `T x y` |
| A/a | Elliptical arc | `A rx ry rotation large-arc sweep x y` |
| Z/z | Close path | `Z` |

**Cubic Bézier** (`C`): Two control points define the curve. The first control point sets the departure angle, the second sets the arrival angle.

```svg
<path d="M 10 80 C 40 10, 65 10, 95 80" stroke="#000" fill="none" stroke-width="2" />
```

**Smooth Cubic** (`S`): Reflects the previous control point automatically — perfect for chaining fluid S-curves.

```svg
<path d="M 10 80 C 40 10, 65 10, 95 80 S 150 150, 180 80" stroke="#000" fill="none" />
```

**Arc** (`A`): `rx ry x-rotation large-arc-flag sweep-flag x y`
- `large-arc-flag`: 0 = small arc, 1 = large arc (>180°)
- `sweep-flag`: 0 = counterclockwise, 1 = clockwise

```svg
<!-- Heart shape using arcs and quadratic curves -->
<path d="M 10,30 A 20,20 0,0,1 50,30 A 20,20 0,0,1 90,30 Q 90,60 50,90 Q 10,60 10,30 Z"
      fill="#e63946" />
```

#### Grouping and Transforms

```svg
<g transform="translate(50, 50) rotate(45)" opacity="0.8">
  <rect x="-20" y="-20" width="40" height="40" fill="#264653" />
</g>
```

Use `<g>` to group elements for collective transforms, styling, and animation targets.

#### Gradients, Masks, and Filters

```svg
<defs>
  <!-- Linear gradient -->
  <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#e63946" />
    <stop offset="100%" stop-color="#457b9d" />
  </linearGradient>

  <!-- Radial gradient -->
  <radialGradient id="glow" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#fff" stop-opacity="0.8" />
    <stop offset="100%" stop-color="#fff" stop-opacity="0" />
  </radialGradient>

  <!-- Mask -->
  <mask id="reveal">
    <rect width="100%" height="100%" fill="black" />
    <circle cx="100" cy="100" r="50" fill="white" />
  </mask>

  <!-- Blur filter -->
  <filter id="blur">
    <feGaussianBlur in="SourceGraphic" stdDeviation="3" />
  </filter>
</defs>

<rect width="200" height="200" fill="url(#grad)" />
<rect width="200" height="200" fill="url(#grad)" mask="url(#reveal)" />
<circle cx="50" cy="50" r="20" filter="url(#blur)" fill="#e63946" />
```

---

### CSS Animations on SVG

Many SVG attributes are valid CSS properties: `fill`, `stroke`, `opacity`, `transform`, `stroke-dasharray`, `stroke-dashoffset`, etc.

#### Basic CSS Animation

```css
.pulse {
  animation: pulse 2s ease-in-out infinite;
  transform-origin: center;
}
@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.15); opacity: 0.7; }
}
```

#### Stroke Drawing Animation (The Classic)

The most iconic SVG animation. Uses `stroke-dasharray` and `stroke-dashoffset` to make a path appear to draw itself.

**How it works:**
1. Set `stroke-dasharray` to the path's total length (one giant dash + one giant gap)
2. Set `stroke-dashoffset` to the same length (shifts the dash off-screen)
3. Animate `stroke-dashoffset` to 0 (slides the dash into view)

```svg
<svg viewBox="0 0 200 200">
  <path class="draw" d="M 20 100 C 20 50, 80 50, 80 100 S 140 150, 140 100"
        fill="none" stroke="#1a1a1a" stroke-width="3" />
</svg>

<style>
  .draw {
    stroke-dasharray: 300;
    stroke-dashoffset: 300;
    animation: draw 2s ease forwards;
  }
  @keyframes draw {
    to { stroke-dashoffset: 0; }
  }
</style>
```

**Getting exact path length in JS:**
```js
const path = document.querySelector('.draw');
const length = path.getTotalLength();
path.style.strokeDasharray = length;
path.style.strokeDashoffset = length;
```

#### Staggered Multi-Path Drawing

```css
.line-1 { animation-delay: 0s; }
.line-2 { animation-delay: 0.3s; }
.line-3 { animation-delay: 0.6s; }
```

#### CSS `d` Property Animation

Modern browsers support animating the `d` attribute directly in CSS:

```css
path {
  d: path("M 10,30 A 20,20 0,0,1 50,30 A 20,20 0,0,1 90,30 Q 90,60 50,90 Q 10,60 10,30 z");
  transition: d 0.5s ease;
}
path:hover {
  d: path("M 10,50 A 20,20 0,0,1 50,10 A 20,20 0,0,1 90,50 Q 90,80 50,100 Q 10,80 10,50 z");
}
```

**Requirement:** Both paths must have the same number and types of commands for interpolation to work.

---

### SMIL Animations (Native SVG)

SMIL animations are declared directly inside SVG markup. They work even when SVG is loaded as an `<img>` or CSS `background-image` — where CSS and JS can't reach.

#### `<animate>` — Animate Any Attribute

```svg
<circle cx="50" cy="50" r="20" fill="#e63946">
  <animate attributeName="r" from="20" to="40" dur="1s"
           repeatCount="indefinite" />
</circle>
```

With keyframes:
```svg
<animate attributeName="cx"
         values="50; 150; 100; 50"
         keyTimes="0; 0.33; 0.66; 1"
         dur="3s" repeatCount="indefinite" />
```

#### `<animateTransform>` — Transform Animations

```svg
<rect x="-20" y="-20" width="40" height="40" fill="#264653">
  <animateTransform attributeName="transform" type="rotate"
                    from="0" to="360" dur="4s" repeatCount="indefinite" />
</rect>
```

Types: `translate`, `scale`, `rotate`, `skewX`, `skewY`

#### `<animateMotion>` — Move Along a Path

```svg
<circle r="5" fill="#e63946">
  <animateMotion dur="3s" repeatCount="indefinite" rotate="auto">
    <mpath href="#motionPath" />
  </animateMotion>
</circle>
<path id="motionPath" d="M 20,50 C 20,0 80,0 80,50 S 140,100 140,50"
      fill="none" stroke="#ccc" />
```

`rotate="auto"` orients the element tangent to the path. `rotate="auto-reverse"` flips it 180°.

#### `<set>` — Discrete Value Changes

```svg
<rect width="40" height="40" fill="#264653">
  <set attributeName="fill" to="#e63946" begin="1s" />
</rect>
```

#### Timing and Synchronization

```svg
<!-- Chain animations by referencing IDs -->
<animate id="first" attributeName="cx" to="150" dur="1s" fill="freeze" />
<animate attributeName="cy" to="150" dur="1s" begin="first.end" fill="freeze" />
<animate attributeName="r" to="30" dur="0.5s" begin="first.end + 0.5s" fill="freeze" />
```

Trigger values:
- `begin="click"` — on click
- `begin="2s"` — after 2 seconds
- `begin="other.end"` — when another animation ends
- `begin="other.end + 1s"` — 1s after another ends
- `begin="other.repeat(2)"` — on 2nd repeat of another

#### Easing with `calcMode` and `keySplines`

```svg
<animate attributeName="cx" values="50;150" dur="1s"
         calcMode="spline" keySplines="0.42 0 0.58 1" />
```

`calcMode` options: `linear` (default), `discrete`, `paced`, `spline`

`keySplines` takes cubic-bezier control points (x1 y1 x2 y2) per interval. Common easings:
- Ease-in-out: `0.42 0 0.58 1`
- Ease-out: `0 0 0.58 1`
- Bounce-ish: `0.34 1.56 0.64 1`

#### Shape Morphing with SMIL

Both shapes must have identical command structures (same number of points, same command types):

```svg
<path fill="#e63946">
  <animate attributeName="d" dur="2s" repeatCount="indefinite"
    values="M 50,10 L 90,90 L 10,90 Z;
            M 50,90 L 90,10 L 10,10 Z;
            M 50,10 L 90,90 L 10,90 Z" />
</path>
```

---

### Animation Patterns & Recipes

#### Loading Spinner

```svg
<svg viewBox="0 0 50 50">
  <circle cx="25" cy="25" r="20" fill="none" stroke="#1a1a1a"
          stroke-width="3" stroke-linecap="round"
          stroke-dasharray="90 150" stroke-dashoffset="0">
    <animateTransform attributeName="transform" type="rotate"
                      from="0 25 25" to="360 25 25" dur="1s"
                      repeatCount="indefinite" />
    <animate attributeName="stroke-dashoffset" values="0;-280"
             dur="1.5s" repeatCount="indefinite" />
  </circle>
</svg>
```

#### Animated Checkmark

```svg
<svg viewBox="0 0 52 52">
  <circle cx="26" cy="26" r="24" fill="none" stroke="#4caf50"
          stroke-width="2" class="draw"
          style="stroke-dasharray:150;stroke-dashoffset:150;
                 animation:draw .6s ease forwards" />
  <path fill="none" stroke="#4caf50" stroke-width="3"
        stroke-linecap="round" stroke-linejoin="round"
        d="M14 27l7 7 16-16" class="draw"
        style="stroke-dasharray:50;stroke-dashoffset:50;
               animation:draw .4s ease .5s forwards" />
</svg>
```

#### Morphing Hamburger to X

```svg
<svg viewBox="0 0 24 24" id="menu">
  <path id="top" d="M 3,6 L 21,6" stroke="#1a1a1a" stroke-width="2" stroke-linecap="round">
    <animate attributeName="d" to="M 5,5 L 19,19" dur="0.3s" begin="menu.click" fill="freeze" />
  </path>
  <path id="mid" d="M 3,12 L 21,12" stroke="#1a1a1a" stroke-width="2" stroke-linecap="round">
    <animate attributeName="opacity" to="0" dur="0.1s" begin="menu.click" fill="freeze" />
  </path>
  <path id="bot" d="M 3,18 L 21,18" stroke="#1a1a1a" stroke-width="2" stroke-linecap="round">
    <animate attributeName="d" to="M 5,19 L 19,5" dur="0.3s" begin="menu.click" fill="freeze" />
  </path>
</svg>
```

#### Gradient Animation (Color Shift)

```svg
<defs>
  <linearGradient id="shift" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%">
      <animate attributeName="stop-color"
               values="#e63946;#457b9d;#2a9d8f;#e63946"
               dur="4s" repeatCount="indefinite" />
    </stop>
    <stop offset="100%">
      <animate attributeName="stop-color"
               values="#457b9d;#2a9d8f;#e63946;#457b9d"
               dur="4s" repeatCount="indefinite" />
    </stop>
  </linearGradient>
</defs>
<rect width="200" height="100" fill="url(#shift)" rx="8" />
```

#### Breathing / Pulsing Glow

```svg
<circle cx="100" cy="100" r="30" fill="#e63946">
  <animate attributeName="r" values="30;35;30" dur="2s"
           calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"
           repeatCount="indefinite" />
  <animate attributeName="opacity" values="1;0.6;1" dur="2s"
           calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"
           repeatCount="indefinite" />
</circle>
```

#### Wave / Liquid Effect

```svg
<path fill="#457b9d" opacity="0.7">
  <animate attributeName="d" dur="5s" repeatCount="indefinite"
    values="M 0,40 C 30,35 70,45 100,40 L 100,100 L 0,100 Z;
            M 0,40 C 30,50 70,30 100,40 L 100,100 L 0,100 Z;
            M 0,40 C 30,35 70,45 100,40 L 100,100 L 0,100 Z"
    calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1" />
</path>
```

---

### Best Practices

1. **Use `viewBox`, never hardcode `width`/`height` in the SVG** — let the container size it. This keeps it resolution-independent.

2. **`<defs>` for reusable definitions** — gradients, filters, masks, clipPaths, and reusable shapes belong in `<defs>`.

3. **Prefer SMIL for self-contained SVGs** (icons, logos loaded via `<img>`) — CSS/JS won't work there. Use CSS animations when the SVG is inlined and you want to coordinate with the rest of the page.

4. **Shape morphing requires matching commands** — same number of path commands, same types, same order. If shapes differ, add invisible intermediate points to equalize.

5. **`stroke-linecap="round"`** makes line animations look polished.

6. **`fill="freeze"`** in SMIL keeps the final animation state. Without it, the element snaps back.

7. **`transform-origin: center`** in CSS — SVG transforms default to the origin (0,0), not the element center. Always set this explicitly.

8. **Use `getTotalLength()`** in JS to get exact path lengths for stroke animations instead of guessing.

9. **Layer animations with `<g>` groups** — animate the group transform separately from individual element properties for complex choreography.

10. **Performance:** SVG animations are GPU-composited when animating `transform` and `opacity`. Animating `d`, `points`, or layout attributes triggers repaints — use sparingly on complex SVGs.

11. **`will-change: transform`** on animated SVG elements helps the browser optimize compositing.

12. **Accessibility:** Add `role="img"` and `<title>` / `<desc>` elements. Use `prefers-reduced-motion` media query to disable animations for users who request it:

```css
@media (prefers-reduced-motion: reduce) {
  svg * {
    animation: none !important;
    transition: none !important;
  }
}
```
