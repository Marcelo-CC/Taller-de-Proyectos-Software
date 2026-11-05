import { useMemo, useState } from 'react';
import TablaReclamos from './TablaReclamos';
import { CATEGORIAS, ESTADOS } from '../../constantes';

// Sección 2 (HU-07): filtros por categoría y estado + buscador en tiempo real
export default function BusquedaFiltrado({ reclamos, onCambiarEstado, actualizando }) {
  const [categoria, setCategoria] = useState('');
  const [estado, setEstado] = useState('');
  const [busqueda, setBusqueda] = useState('');

  const termino = busqueda.trim().toLowerCase();
  const filtrados = useMemo(() => reclamos.filter((r) =>
    (!categoria || r.categoria === categoria) &&
    (!estado || (r.estado || 'PENDIENTE') === estado) &&
    (!termino || `${r.titulo} ${r.descripcion}`.toLowerCase().includes(termino))
  ), [reclamos, categoria, estado, termino]);

  const limpiar = () => { setCategoria(''); setEstado(''); setBusqueda(''); };
  const hayFiltros = categoria || estado || busqueda;

  return (
    <section>
      <div className="barra-filtros">
        <label className="buscador">
          <span aria-hidden="true">🔍</span>
          <input
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            placeholder='Buscar en los textos anonimizados: "poste", "basura", "Giráldez", "bache"…'
            aria-label="Buscar por palabra clave"
          />
        </label>

        <div className="grupo-filtro" role="group" aria-label="Filtrar por categoría">
          <span className="grupo-etiqueta">Categoría</span>
          <button className={`chip ${!categoria ? 'activo' : ''}`} onClick={() => setCategoria('')}>Todas</button>
          {CATEGORIAS.map((c) => (
            <button key={c.nombre} className={`chip ${categoria === c.nombre ? 'activo' : ''}`}
              onClick={() => setCategoria(c.nombre)} aria-pressed={categoria === c.nombre}>
              <span className="punto" style={{ background: c.color }} aria-hidden="true" /> {c.nombre}
            </button>
          ))}
        </div>

        <div className="grupo-filtro" role="group" aria-label="Filtrar por estado">
          <span className="grupo-etiqueta">Estado</span>
          <button className={`chip ${!estado ? 'activo' : ''}`} onClick={() => setEstado('')}>Todos</button>
          {Object.entries(ESTADOS).map(([valor, e]) => (
            <button key={valor} className={`chip ${estado === valor ? 'activo' : ''}`}
              onClick={() => setEstado(valor)} aria-pressed={estado === valor}>
              <span aria-hidden="true">{e.icono}</span> {e.etiqueta}
            </button>
          ))}
        </div>
      </div>

      <div className="resumen-filtro">
        <span><strong>{filtrados.length}</strong> de {reclamos.length} reclamos</span>
        {hayFiltros && <button className="enlace" onClick={limpiar}>Limpiar filtros</button>}
      </div>

      <TablaReclamos
        key={`${categoria}|${estado}|${termino}`}
        reclamos={filtrados}
        onCambiarEstado={onCambiarEstado}
        actualizando={actualizando}
        resaltar={busqueda.trim()}
      />
    </section>
  );
}
