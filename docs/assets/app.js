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
