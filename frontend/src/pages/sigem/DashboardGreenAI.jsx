import { useMemo, useState } from 'react';
import {
  ResponsiveContainer, BarChart, Bar, Cell, LabelList, XAxis, YAxis, CartesianGrid, Tooltip,
  LineChart, Line,
} from 'recharts';
import { CATEGORIAS, formatoFecha, formatoTicket } from '../../constantes';
import { MLFLOW_URL } from '../../services/api';
import { exportarCsv, exportarPdf } from '../../services/exportar';

const TINTA = { primaria: '#0b0b0b', secundaria: '#52514e', rejilla: '#e1e0d9' };
const SERIE = '#2a78d6';
const ULTIMAS_INFERENCIAS = 60;

const numero = (v, d = 2) => v.toLocaleString('es-PE', { minimumFractionDigits: d, maximumFractionDigits: d });

function TarjetaKpi({ titulo, valor, unidad, detalle }) {
  return (
    <div className="kpi">
      <span className="kpi-titulo">{titulo}</span>
      <span className="kpi-valor">{valor}{unidad && <small> {unidad}</small>}</span>
      {detalle && <span className="kpi-detalle">{detalle}</span>}
    </div>
  );
}

function TooltipCaja({ active, payload, formato }) {
  if (!active || !payload?.length) return null;
  return <div className="tooltip-grafico">{formato(payload[0].payload)}</div>;
}

export default function DashboardGreenAI({ reclamos }) {
  const [verTabla, setVerTabla] = useState({ categorias: false, huella: false });

  const { totalKwh, totalGco2, porCategoria, huella } = useMemo(() => {
    const totalKwh = reclamos.reduce((s, r) => s + (Number(r.consumo_kwh) || 0), 0);
    const totalGco2 = reclamos.reduce((s, r) => s + (Number(r.emisiones_gco2) || 0), 0);
    const porCategoria = CATEGORIAS.map((c) => ({
      ...c,
      total: reclamos.filter((r) => r.categoria === c.nombre).length,
    }));
    const huella = [...reclamos]
      .sort((a, b) => a.id - b.id)
      .slice(-ULTIMAS_INFERENCIAS)
      .map((r) => ({
        id: r.id,
        ticket: formatoTicket(r.id),
        fecha: r.created_at,
        gco2: Number(r.emisiones_gco2) || 0,
      }));
    return { totalKwh, totalGco2, porCategoria, huella };
  }, [reclamos]);

  const promedio = reclamos.length ? totalGco2 / reclamos.length : 0;
  const ultima = huella[huella.length - 1];

  return (
    <section className="dashboard">
      <div className="exportar-reporte">
        <div>
          <strong>Reporte de sostenibilidad</strong>
          <span>Descargue los {reclamos.length.toLocaleString('es-PE')} reclamos con su consumo de energía y emisiones.</span>
        </div>
        <div className="exportar-botones">
          <button className="boton boton-claro" onClick={() => exportarCsv(reclamos)} disabled={!reclamos.length}>
            ⬇ Descargar CSV (Excel)
          </button>
          <button className="boton boton-primario" onClick={() => exportarPdf(reclamos)} disabled={!reclamos.length}>
            🖨 Reporte PDF
          </button>
        </div>
      </div>

      <div className="kpis">
        <TarjetaKpi titulo="Reclamos procesados por la IA" valor={reclamos.length.toLocaleString('es-PE')} />
        <TarjetaKpi titulo="Consumo energético acumulado" valor={numero(totalKwh, 4)} unidad="kWh"
          detalle={`${numero(totalKwh * 1000, 1)} Wh en total`} />
        <TarjetaKpi titulo="Emisiones totales de carbono" valor={numero(totalGco2, 3)} unidad="gCO₂e"
          detalle={`Promedio: ${numero(promedio, 4)} gCO₂e por reclamo`} />
      </div>

      <div className="graficos">
        <article className="tarjeta grafico">
          <header>
            <h3>Distribución de reclamos por categoría</h3>
            <button className="enlace" onClick={() => setVerTabla({ ...verTabla, categorias: !verTabla.categorias })}>
              {verTabla.categorias ? 'Ver gráfico' : 'Ver tabla'}
            </button>
          </header>
          {verTabla.categorias ? (
            <table className="tabla tabla-compacta">
              <thead><tr><th>Categoría</th><th>Reclamos</th><th>%</th></tr></thead>
              <tbody>
                {porCategoria.map((c) => (
                  <tr key={c.nombre}>
                    <td>{c.nombre}</td><td>{c.total}</td>
                    <td>{reclamos.length ? numero((c.total / reclamos.length) * 100, 1) : 0}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={porCategoria} layout="vertical" margin={{ top: 8, right: 48, bottom: 8, left: 8 }}>
                <CartesianGrid horizontal={false} stroke={TINTA.rejilla} />
                <XAxis type="number" allowDecimals={false} tick={{ fill: TINTA.secundaria, fontSize: 12 }}
                  axisLine={{ stroke: TINTA.rejilla }} tickLine={false} />
                <YAxis type="category" dataKey="nombre" width={130} tick={{ fill: TINTA.primaria, fontSize: 13 }}
                  axisLine={false} tickLine={false} />
                <Tooltip cursor={{ fill: 'rgba(11,58,107,0.06)' }}
                  content={<TooltipCaja formato={(d) => (
                    <><strong>{d.nombre}</strong><span>{d.total} reclamos</span></>
                  )} />} />
                <Bar dataKey="total" barSize={24} radius={[0, 4, 4, 0]} isAnimationActive={false}>
                  {porCategoria.map((c) => <Cell key={c.nombre} fill={c.color} />)}
                  <LabelList dataKey="total" position="right" fill={TINTA.primaria} fontSize={13} />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </article>

        <article className="tarjeta grafico">
          <header>
            <div>
              <h3>Huella ambiental por inferencia (gCO₂e)</h3>
              <p className="nota">
                Últimas {huella.length} inferencias con Gemini · Métricas registradas también en{' '}
                <a href={MLFLOW_URL} target="_blank" rel="noreferrer">MLflow (DagsHub)</a>
              </p>
            </div>
            <button className="enlace" onClick={() => setVerTabla({ ...verTabla, huella: !verTabla.huella })}>
              {verTabla.huella ? 'Ver gráfico' : 'Ver tabla'}
            </button>
          </header>
          {verTabla.huella ? (
            <div className="tabla-envoltura tabla-scroll">
              <table className="tabla tabla-compacta">
                <thead><tr><th>Ticket</th><th>Fecha</th><th>gCO₂e</th></tr></thead>
                <tbody>
                  {[...huella].reverse().map((d) => (
                    <tr key={d.id}><td>{d.ticket}</td><td>{formatoFecha(d.fecha)}</td><td>{numero(d.gco2, 5)}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={huella} margin={{ top: 16, right: 72, bottom: 8, left: 0 }}>
                <CartesianGrid vertical={false} stroke={TINTA.rejilla} />
                <XAxis dataKey="ticket" tick={{ fill: TINTA.secundaria, fontSize: 11 }} interval="preserveStartEnd"
                  minTickGap={48} axisLine={{ stroke: TINTA.rejilla }} tickLine={false} />
                <YAxis tickFormatter={(v) => numero(v, 3)} tick={{ fill: TINTA.secundaria, fontSize: 11 }}
                  width={56} axisLine={false} tickLine={false} />
                <Tooltip cursor={{ stroke: TINTA.secundaria, strokeWidth: 1 }}
                  content={<TooltipCaja formato={(d) => (
                    <><strong>Ticket {d.ticket}</strong><span>{formatoFecha(d.fecha)}</span>
                      <span>{numero(d.gco2, 5)} gCO₂e</span></>
                  )} />} />
                <Line type="linear" dataKey="gco2" stroke={SERIE} strokeWidth={2} dot={false}
                  activeDot={{ r: 5, stroke: '#fff', strokeWidth: 2 }} isAnimationActive={false}>
                  {ultima && (
                    <LabelList dataKey="gco2" content={({ x, y, index }) => index === huella.length - 1 && (
                      <text x={x + 8} y={y + 4} fill={TINTA.primaria} fontSize={12}>{numero(ultima.gco2, 4)}</text>
                    )} />
                  )}
                </Line>
              </LineChart>
            </ResponsiveContainer>
          )}
        </article>
      </div>
    </section>
  );
}
