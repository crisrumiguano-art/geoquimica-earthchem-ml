---
name: theme-view-transition
description: Transiciona una web entre modo claro y oscuro respetando contrastes entre letras, elementos y fondos. Usa view-transitions y clip-path para animar los cambios de tema de arriba hacia abajo. Úsala cada vez que el usuario quiera implementar un cambio de tema o dark mode con una animación fluida.
---

# Theme View Transition Skill

Esta habilidad te enseña a implementar un cambio de tema (modo oscuro / claro) utilizando la API de View Transitions y `clip-path` para crear una animación fluida de arriba hacia abajo, asegurando siempre que se respeten los contrastes adecuados entre textos, elementos interactivos y fondos.

## ¿Cómo funciona?

En lugar de depender de transiciones de CSS tradicionales en cada elemento (lo que puede causar repintados masivos y rendimiento deficiente) o de voltear el tema bruscamente, usamos `document.startViewTransition()` combinado con una animación de `clipPath`.

### Código de implementación

```javascript
// Ejemplo de función para cambiar el tema
function toggleTheme(event) {
  // 1. Fallback si el navegador no soporta View Transitions
  if (!document.startViewTransition) {
    document.documentElement.classList.toggle('dark');
    return;
  }

  // 2. Iniciar la transición
  const transition = document.startViewTransition(() => {
    // Aquí cambiamos la clase que controla el tema (ej. de Tailwind o CSS puro)
    document.documentElement.classList.toggle('dark');
  });

  // 3. Animar el pseudo-elemento de la nueva vista
  transition.ready.then(() => {
    document.documentElement.animate(
      { clipPath: ["inset(0 0 100% 0)", "inset(0)"] },
      { pseudoElement: "::view-transition-new(root)", duration: 600, easing: "ease-in-out" }
    );
  });
}
```

```css
/* CSS Requerido para la vista nueva */
::view-transition-new(root) {
  animation: none;
  mix-blend-mode: normal;
}

/* Opcional: Asegurar que la vista antigua se quede estática debajo */
::view-transition-old(root) {
  animation: none;
  z-index: -1;
}
```

Aquí el `clipPath` con valores desde `inset(0 0 100% 0)` hasta `inset(0)` asegura que la transición ocurra de arriba hacia abajo revelando el nuevo tema de forma natural y sofisticada.

## Reglas de Contraste y Diseño

Al implementar los estilos para el modo claro y oscuro, **DEBES** seguir estas reglas para garantizar una lectura cómoda y una estética premium:

1. **Textos**: 
   - *Modo Oscuro*: Usa grises muy claros o blanco roto (ej. `#e5e7eb` o `#f3f4f6`) en lugar de blanco puro (`#ffffff`) para evitar el deslumbramiento y la fatiga visual.
   - *Modo Claro*: Usa grises muy oscuros (ej. `#1f2937` o `#111827`) en lugar de negro puro (`#000000`).
2. **Fondos**:
   - *Modo Oscuro*: Evita el negro puro. Usa tonos muy oscuros pero suaves (ej. `#121212`, `#0f172a`). Los elementos elevados (tarjetas, modales, navbars) deben ser ligeramente más claros que el fondo base (ej. `#1e293b`) para denotar profundidad.
   - *Modo Claro*: Usa blanco puro o un gris extremadamente claro (ej. `#f8fafc`) para el fondo base.
3. **Elementos Interactivos y Acentos**:
   - Asegura un ratio de contraste adecuado (WCAG AA). 
   - Los colores de acento pueden necesitar ajustes de saturación/luminosidad entre temas (un color azul primario que funciona bien en fondo blanco podría necesitar ser un poco más claro/pastel para destacar correctamente en fondo oscuro).

## Pasos para el Agente

Cuando te pidan implementar un cambio de modo claro/oscuro:
1. Asegúrate de añadir el CSS de `::view-transition-new(root)`.
2. Implementa la lógica de JS envolviendo el cambio de clase (ej. `.dark`) dentro de `document.startViewTransition()`.
3. Aplica la animación de `clipPath` en el `transition.ready`.
4. Revisa todos los colores y asegúrate de que el contraste cumpla con las directrices anteriores.
