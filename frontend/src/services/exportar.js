// Exportación de reportes de sostenibilidad del SIGEM (FURPS+ Funcionalidad).
// Todo se genera en el navegador con los reclamos ya cargados: no hay llamadas extra al servidor.
import { CATEGORIAS, ESTADOS, ESTADO_AUDITORIA, estadoVisible, formatoFecha, formatoTicket } from '../constantes';

const etiquetaEstado = (r) => {
  const e = estadoVisible(r);
  return e === 'AUDITORIA' ? ESTADO_AUDITORIA.etiqueta : ESTADOS[e]?.etiqueta || e;
};

// OWASP (inyección de fórmulas en CSV): una celda que empieza con = + - @ se trata como texto en Excel
const celdaCsv = (valor) => {
  let texto = valor == null ? '' : String(valor);
  if (/^[=+\-@\t\r]/.test(texto)) texto = `'${texto}`;
  return /[";\n\r]/.test(texto) ? `"${texto.replace(/"/g, '""')}"` : texto;
};

const fechaArchivo = () => new Date().toISOString().slice(0, 10);

function descargar(contenido, nombre, tipo) {
  const url = URL.createObjectURL(new Blob([contenido], { type: tipo }));
  const enlace = Object.assign(document.createElement('a'), { href: url, download: nombre });
  document.body.appendChild(enlace);
  enlace.click();
  enlace.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// Excel en español separa columnas con «;» y usa coma decimal: así cada dato cae en su columna y los números
// quedan como números (se pueden sumar y graficar).
const SEPARADOR = ';';
const decimal = (valor, decimales) => (Number(valor) || 0).toFixed(decimales).replace('.', ',');

// CSV con una fila por reclamo. No incluye el texto del reclamo: solo datos de gestión y de huella ambiental.
export function exportarCsv(reclamos) {
  const encabezado = ['Ticket', 'Fecha', 'Categoría', 'Estado', 'Confianza IA (%)', 'Energía (kWh)', 'Emisiones (gCO2e)'];
  const filas = [...reclamos]
    .sort((a, b) => a.id - b.id)
    .map((r) => [
      formatoTicket(r.id),
      formatoFecha(r.created_at),
      r.categoria,
      etiquetaEstado(r),
      r.confianza == null ? '' : Math.round(Number(r.confianza) * 100),
      decimal(r.consumo_kwh, 8),
      decimal(r.emisiones_gco2, 6),
    ]);
  const csv = [encabezado, ...filas].map((fila) => fila.map(celdaCsv).join(SEPARADOR)).join('\r\n');
  // BOM: Excel reconoce UTF-8 y muestra bien las tildes
  descargar(`﻿${csv}`, `reporte_sostenibilidad_${fechaArchivo()}.csv`, 'text/csv;charset=utf-8');
}

export function resumenSostenibilidad(reclamos) {
  const suma = (lista, campo) => lista.reduce((s, r) => s + (Number(r[campo]) || 0), 0);
  const total = reclamos.length;
  const totalKwh = suma(reclamos, 'consumo_kwh');
  const totalGco2 = suma(reclamos, 'emisiones_gco2');
  const porCategoria = CATEGORIAS.map((c) => {
    const lista = reclamos.filter((r) => r.categoria === c.nombre);
    return { nombre: c.nombre, total: lista.length, kwh: suma(lista, 'consumo_kwh'), gco2: suma(lista, 'emisiones_gco2') };
  });
  const porEstado = [['AUDITORIA', ESTADO_AUDITORIA], ...Object.entries(ESTADOS)].map(([clave, e]) => ({
    nombre: e.etiqueta,
    total: reclamos.filter((r) => estadoVisible(r) === clave).length,
  }));
  return { total, totalKwh, totalGco2, promedio: total ? totalGco2 / total : 0, porCategoria, porEstado };
}

const escapar = (t) => String(t).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const num = (v, d) => v.toLocaleString('es-PE', { minimumFractionDigits: d, maximumFractionDigits: d });
const pct = (parte, total) => (total ? `${num((parte / total) * 100, 1)} %` : '0 %');

// Reporte para imprimir o guardar como PDF desde el diálogo de impresión del navegador
export function exportarPdf(reclamos) {
  const r = resumenSostenibilidad(reclamos);
  const filasCategoria = r.porCategoria.map((c) => `<tr><td>${escapar(c.nombre)}</td><td>${c.total}</td>
    <td>${pct(c.total, r.total)}</td><td>${num(c.kwh, 5)}</td><td>${num(c.gco2, 4)}</td></tr>`).join('');
  const filasEstado = r.porEstado.map((e) => `<tr><td>${escapar(e.nombre)}</td><td>${e.total}</td>
    <td>${pct(e.total, r.total)}</td></tr>`).join('');

  const html = `<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>Reporte de sostenibilidad Green AI · ${fechaArchivo()}</title>
<style>
  body { font-family: Arial, Helvetica, sans-serif; color: #1a1a1a; margin: 32px; }
  h1 { font-size: 20px; margin: 0 0 4px; color: #0b3a6b; }
  h2 { font-size: 15px; margin: 24px 0 8px; color: #0b3a6b; }
  .sub { color: #555; font-size: 12px; margin: 0 0 20px; }
  .kpis { display: flex; gap: 12px; }
  .kpi { flex: 1; border: 1px solid #d7d7d2; border-radius: 6px; padding: 10px 12px; }
  .kpi b { display: block; font-size: 18px; margin-top: 4px; }
  .kpi span { font-size: 11px; color: #555; }
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  th, td { border: 1px solid #d7d7d2; padding: 6px 8px; text-align: right; }
  th:first-child, td:first-child { text-align: left; }
  th { background: #eef2f7; }
  .nota { font-size: 11px; color: #555; margin-top: 24px; }
  @media print { body { margin: 12mm; } }
</style></head><body>
<h1>Reporte de sostenibilidad · Green AI Municipal</h1>
<p class="sub">Municipalidad Provincial de Huancayo · SIGEM · Generado el ${escapar(formatoFecha(new Date().toISOString()))}</p>
<div class="kpis">
  <div class="kpi"><span>Reclamos procesados por la IA</span><b>${r.total.toLocaleString('es-PE')}</b></div>
  <div class="kpi"><span>Consumo energético acumulado</span><b>${num(r.totalKwh, 4)} kWh</b></div>
  <div class="kpi"><span>Emisiones totales</span><b>${num(r.totalGco2, 3)} gCO₂e</b></div>
  <div class="kpi"><span>Promedio por reclamo</span><b>${num(r.promedio, 4)} gCO₂e</b></div>
</div>
<h2>Reclamos y huella por categoría</h2>
<table><thead><tr><th>Categoría</th><th>Reclamos</th><th>%</th><th>Energía (kWh)</th><th>Emisiones (gCO₂e)</th></tr></thead>
<tbody>${filasCategoria}</tbody></table>
<h2>Reclamos por estado</h2>
<table><thead><tr><th>Estado</th><th>Reclamos</th><th>%</th></tr></thead><tbody>${filasEstado}</tbody></table>
<p class="nota">Energía y emisiones medidas con CodeCarbon en cada inferencia y registradas en MLflow (DagsHub).
Los reclamos retenidos por baja confianza de la IA figuran como «${escapar(ESTADO_AUDITORIA.etiqueta)}».</p>
</body></html>`;

  const ventana = window.open('', '_blank');
  if (!ventana) {
    // Si el navegador bloquea la ventana emergente, se descarga el reporte como HTML para imprimirlo
    descargar(html, `reporte_sostenibilidad_${fechaArchivo()}.html`, 'text/html;charset=utf-8');
    return;
  }
  ventana.document.open();
  ventana.document.write(html);
  ventana.document.close();
  ventana.focus();
  setTimeout(() => ventana.print(), 300);
}
