import { useState } from 'react';
import { InsigniaCategoria, InsigniaEstado, TextoAnonimizado } from '../../components/Layout';
import { ESTADOS, formatoFecha, formatoTicket } from '../../constantes';

const POR_PAGINA = 12;

export default function TablaReclamos({ reclamos, onCambiarEstado, actualizando, resaltar = '' }) {
  const [pagina, setPagina] = useState(1);
  const [expandido, setExpandido] = useState(null);

  const totalPaginas = Math.max(1, Math.ceil(reclamos.length / POR_PAGINA));
  // Si un filtro reduce la lista, no quedarse en una página que ya no existe
  if (pagina > totalPaginas) setPagina(totalPaginas);
  const visibles = reclamos.slice((pagina - 1) * POR_PAGINA, pagina * POR_PAGINA);

  if (!reclamos.length) {
    return <div className="tabla-vacia">No se encontraron reclamos con los criterios seleccionados.</div>;
  }

  return (
    <>
      <div className="tabla-envoltura">
        <table className="tabla">
          <thead>
            <tr>
              <th>Ticket</th>
              <th>Fecha</th>
              <th>Título</th>
              <th>Categoría (IA)</th>
              <th>Texto anonimizado</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {visibles.map((r) => (
              <tr key={r.id}>
                <td className="celda-ticket">{formatoTicket(r.id)}</td>
                <td className="celda-fecha">{formatoFecha(r.created_at)}</td>
                <td className="celda-titulo"><TextoAnonimizado texto={r.titulo} resaltar={resaltar} /></td>
                <td><InsigniaCategoria categoria={r.categoria} /></td>
                <td className="celda-texto">
                  <div className={expandido === r.id ? '' : 'texto-recortado'}>
                    <TextoAnonimizado texto={r.descripcion} resaltar={resaltar} />
                  </div>
                  <button className="enlace" onClick={() => setExpandido(expandido === r.id ? null : r.id)}>
                    {expandido === r.id ? 'Ver menos' : 'Ver completo'}
                  </button>
                </td>
                <td className="celda-estado">
                  <InsigniaEstado estado={r.estado} />
                  <select
                    aria-label={`Cambiar estado del ticket ${formatoTicket(r.id)}`}
                    value={r.estado || 'PENDIENTE'}
                    disabled={actualizando === r.id}
                    onChange={(e) => onCambiarEstado(r.id, e.target.value)}
                  >
                    {Object.entries(ESTADOS).map(([valor, e]) => (
                      <option key={valor} value={valor}>{e.etiqueta}</option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <nav className="paginacion" aria-label="Paginación">
        <span>
          {(pagina - 1) * POR_PAGINA + 1}–{Math.min(pagina * POR_PAGINA, reclamos.length)} de {reclamos.length} reclamos
        </span>
        <div>
          <button className="boton boton-claro" disabled={pagina === 1} onClick={() => setPagina(pagina - 1)}>‹ Anterior</button>
          <span className="pagina-actual">Página {pagina} de {totalPaginas}</span>
          <button className="boton boton-claro" disabled={pagina === totalPaginas} onClick={() => setPagina(pagina + 1)}>Siguiente ›</button>
        </div>
      </nav>
    </>
  );
}
