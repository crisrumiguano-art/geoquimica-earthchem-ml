// Código común a todas las páginas: navegación, aparición al hacer scroll, pestañas,
// lectura de CSV (tablas que exporta R) y estilo de los gráficos Plotly.

const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const fmt = (n, dec = 2) => Number(n).toLocaleString("es", { maximumFractionDigits: dec });
const esc = t => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;");

// Navegación: página actual marcada y fondo sólido al bajar (en la portada empieza transparente)
const nav = document.getElementById("nav");
const pagina = document.body.dataset.pagina;
document.querySelectorAll(".nav ul a[data-p]").forEach(a => { if (a.dataset.p === pagina) a.setAttribute("aria-current", "page"); });
if (pagina !== "inicio") nav.classList.add("fija");
addEventListener("scroll", () => nav.classList.toggle("solid", scrollY > 40), { passive: true });

// Aviso flotante de proyecto académico: se cierra con la X y vuelve a salir al recargar (no se guarda nada)
document.body.insertAdjacentHTML("beforeend", `<div class="aviso" role="note"><span>Proyecto <b>estrictamente académico</b><span class="sec"> ·
  Estadística y Probabilidades, FIGEMPA – UCE</span> · sin fines comerciales</span><button type="button" aria-label="Cerrar aviso">×</button></div>`);
document.querySelector(".aviso button").addEventListener("click", e => e.currentTarget.parentElement.remove());

// Aparición al hacer scroll
const io = new IntersectionObserver(es => es.forEach(e => {
  if (e.isIntersecting) { e.target.classList.add("ver"); io.unobserve(e.target); }
}), { threshold: .1 });
document.querySelectorAll(".rev").forEach(el => io.observe(el));

// Pestañas genéricas: <div class="pestanas"><button data-panel="id">…  + paneles con esos id
function pestanas(grupo, alCambiar) {
  const tabs = [...grupo.querySelectorAll("button")];
  tabs.forEach(b => b.addEventListener("click", () => {
    tabs.forEach(t => { t.setAttribute("aria-selected", t === b); document.getElementById(t.dataset.panel).hidden = t !== b; });
    if (alCambiar) alCambiar(b.dataset.panel);
  }));
}

// CSV de R (write.csv): campos entre comillas, separador coma, NA / Inf / -Inf
async function leerCSV(url) {
  const texto = (await (await fetch(url)).text()).trim();
  const campos = linea => [...linea.matchAll(/("([^"]*)"|[^,]*)(,|$)/g)].map(m => m[2] ?? m[1]).slice(0, -1);
  const [cab, ...filas] = texto.split(/\r?\n/).map(campos);
  return filas.map(f => Object.fromEntries(cab.map((c, i) => [c, f[i]])));
}

// Tabla HTML a partir de filas de leerCSV. columnas: [[clave, título, decimales?], ...]
function tabla(contenedor, filas, columnas) {
  const valor = (v, dec) => {
    if (v === undefined || v === "NA" || v === "Inf" || v === "-Inf" || v === "") return "—";
    return dec === undefined || isNaN(+v) ? esc(v) : fmt(+v, dec);
  };
  contenedor.innerHTML = `<table><thead><tr>${columnas.map(([, t, d]) => `<th${d !== undefined ? ' class="n"' : ""}>${t}</th>`).join("")}</tr></thead>
    <tbody>${filas.map(f => `<tr${f.MC === "NA" ? ' class="abierta"' : ""}>${columnas.map(([k, , d]) =>
      `<td${d !== undefined ? ' class="n"' : ""}>${valor(f[k], d)}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
}

// Estilo común de Plotly
function base(extra = {}) {
  const axis = { gridcolor: css("--grid"), linecolor: css("--axis"), zeroline: false,
                 tickfont: { color: css("--muted") }, title: { font: { color: css("--text-secondary") } } };
  return Object.assign({
    paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)",
    font: { family: '"Instrument Sans", "Segoe UI", sans-serif', color: css("--text-secondary"), size: 12 },
    margin: { l: 56, r: 16, t: 8, b: 44 }, bargap: 0.15, showlegend: false,
    hoverlabel: { bgcolor: css("--surface-2"), bordercolor: css("--axis"), font: { color: css("--text-primary") } },
    xaxis: { ...axis }, yaxis: { ...axis },
  }, extra);
}
const cfg = { displaylogo: false, responsive: true, modeBarButtonsToRemove: ["lasso2d", "select2d"] };
const bar = (x, y, extra = {}) => ({ type: "bar", x, y, marker: { color: css("--series-1"), line: { color: css("--surface-1"), width: 2 } }, ...extra });
const conPlotly = f => window.Plotly ? f() : setTimeout(() => conPlotly(f), 100);

// Botón «Código R» en cada gráfica hecha con R (img/r/*.png). El código sale de data/codigo_r.json, que arma
// scripts/codigo_r.py con el script y las funciones exactas que generaron el PNG. Las gráficas se crean con JS
// después de cargar la página, por eso se vigila el DOM en vez de recorrerlo una sola vez.
// Resaltado de sintaxis de R, con los mismos colores por tipo que RStudio o VS Code (tema oscuro).
// Un solo regex recorre el código: el primer grupo que coincide decide el color del trozo. Las cadenas van antes
// que los comentarios en el orden de lectura, así un "#3987e5" dentro de comillas no se toma como comentario.
const R_TOKENS = new RegExp([
  /("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/,                                   // 1 cadena de texto
  /(#.*)/,                                                                   // 2 comentario
  /\b(function|if|else|for|while|in|repeat|return|next|break)\b/,            // 3 palabra reservada
  /\b(TRUE|FALSE|NULL|NA|Inf|NaN)\b/,                                        // 4 constante
  /(\b\d+(?:\.\d+)?(?:e[+-]?\d+)?L?\b|\.\d+\b)/,                             // 5 número
  /([A-Za-z_.][\w.]*)(?=\s*\()/,                                             // 6 llamada a función
  /(<<-|<-|->|%in%|%%|==|!=|<=|>=|&&|\|\||\$|[+\-*/^~!&|<>=:])/,            // 7 operador
].map(r => r.source).join("|"), "g");
const R_CLASES = [, "s", "c", "k", "b", "n", "f", "o"];
function resaltarR(texto) {
  let html = "", desde = 0;
  for (const m of texto.matchAll(R_TOKENS)) {
    const g = m.findIndex((v, i) => i > 0 && v !== undefined);
    html += esc(texto.slice(desde, m.index)) + `<span class="r-${R_CLASES[g]}">${esc(m[g])}</span>`;
    desde = m.index + m[g].length;  // el grupo 6 no incluye el "(" (lookahead): sigue como texto normal
  }
  return html + esc(texto.slice(desde));
}

let codigosR;
function botonCodigo(fig) {
  const img = fig.querySelector('img[src*="img/r/"]');
  if (!img || fig.dataset.codigo) return;
  const archivo = img.getAttribute("src").split("/").pop();
  const json = img.getAttribute("src").replace(/img\/r\/[^/]+$/, "data/codigo_r.json");
  fig.dataset.codigo = archivo;
  const boton = document.createElement("button");
  boton.type = "button"; boton.className = "ver-codigo"; boton.textContent = "</> Código R";
  boton.setAttribute("aria-expanded", "false");
  fig.append(boton);
  boton.addEventListener("click", async () => {
    let caja = fig.querySelector(".codigo-r");
    if (caja) { caja.remove(); boton.setAttribute("aria-expanded", "false"); return; }
    codigosR ??= fetch(json).then(r => r.json());
    const texto = (await codigosR)[archivo] ?? "# Sin código registrado para " + archivo;
    caja = document.createElement("div");
    caja.className = "codigo-r";
    caja.innerHTML = `<div class="barra"><span>${esc(archivo)} · R</span><button type="button">Copiar</button></div><pre><code>${resaltarR(texto)}</code></pre>`;
    caja.querySelector("button").addEventListener("click", e => navigator.clipboard.writeText(texto)
      .then(() => { e.target.textContent = "Copiado"; setTimeout(() => e.target.textContent = "Copiar", 1500); }));
    fig.append(caja);  // dentro de la figura: en .bloque un hermano nuevo desarmaría la grilla
    boton.setAttribute("aria-expanded", "true");
  });
}
new MutationObserver(() => document.querySelectorAll("figure.grafica").forEach(botonCodigo))
  .observe(document.body, { childList: true, subtree: true });
document.querySelectorAll("figure.grafica").forEach(botonCodigo);
