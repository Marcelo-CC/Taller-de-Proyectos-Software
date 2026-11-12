import { useCallback, useEffect, useState } from 'react';
import { Encabezado, PiePagina } from '../components/Layout';
import { listarReclamos, cambiarEstado, auditarReclamo } from '../services/api';
import { ESTADOS, ESTADO_AUDITORIA, estadoVisible, formatoTicket } from '../constantes';
import TablaReclamos from './sigem/TablaReclamos';
import BusquedaFiltrado from './sigem/BusquedaFiltrado';
import DashboardGreenAI from './sigem/DashboardGreenAI';

const SECCIONES = [
  { id: 'gestion', titulo: 'Panel de Control', icono: '📋' },
  { id: 'busqueda', titulo: 'Búsqueda y Filtrado', icono: '🔍' },
  { id: 'dashboard', titulo: 'Dashboard Green AI', icono: '🌱' },
];

export default function Sigem({ sesion, onSalir }) {
  const [seccion, setSeccion] = useState('gestion');
  const [reclamos, setReclamos] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState('');
  const [actualizando, setActualizando] = useState(null);
  const [aviso, setAviso] = useState('');

  // El estado solo se actualiza cuando responde el servidor
  const traer = useCallback(() =>
    listarReclamos(sesion.token)
      .then((datos) => { setReclamos(datos); setError(''); })
      .catch((err) => setError(err.message || 'No se pudo cargar la lista de reclamos.'))
      .finally(() => setCargando(false)), [sesion.token]);

  useEffect(() => { traer(); }, [traer]);

  const cargar = () => {
    setCargando(true);
    setError('');
    traer();
  };

  // Actualización optimista: se aplica `cambios` en pantalla y se revierte si Supabase falla
  const actualizar = async (id, cambios, guardar, mensaje) => {
    const anterior = reclamos.find((r) => r.id === id);
    setActualizando(id);
    setReclamos((lista) => lista.map((r) => (r.id === id ? { ...r, ...cambios } : r)));
    try {
      await guardar();
      setAviso(mensaje);
    } catch (err) {
      setReclamos((lista) => lista.map((r) => (r.id === id ? anterior : r)));
      setAviso(`⚠️ No se pudo actualizar el ticket ${formatoTicket(id)}: ${err.message}`);
    } finally {
      setActualizando(null);
      setTimeout(() => setAviso(''), 4000);
    }
  };

  const onCambiarEstado = (id, estado) => actualizar(
    id, { estado }, () => cambiarEstado(id, estado, sesion.token),
    `Ticket ${formatoTicket(id)} actualizado a "${ESTADOS[estado].etiqueta}".`,
  );

  // HITL: confirma o corrige la categoría y libera el reclamo hacia la gerencia (pasa a "En proceso")
  const onAuditar = (id, categoria) => {
    const corregido = reclamos.find((r) => r.id === id)?.categoria !== categoria;
    return actualizar(
      id, { categoria, requiere_auditoria: false, estado: 'EN_PROCESO' },
      () => auditarReclamo(id, categoria, sesion.token),
      `Ticket ${formatoTicket(id)} auditado: categoría ${corregido ? 'corregida a' : 'confirmada como'} `
        + `"${categoria}" y derivado a su gerencia.`,
    );
  };

  // Cada reclamo cuenta en un solo contador: los retenidos por HITL no suman en "Pendiente"
  const conteo = (estado) => reclamos.filter((r) => estadoVisible(r) === estado).length;
  const contadores = { AUDITORIA: ESTADO_AUDITORIA, ...ESTADOS };

  return (
    <div className="pagina">
      <Encabezado subtitulo="Sistema de Gestión Interna (SIGEM)">
        <div className="usuario-sesion">
          <span className="avatar" aria-hidden="true">{sesion.nombre[0]}</span>
          <span><strong>{sesion.nombre}</strong><small>Rol: {sesion.rol}</small></span>
        </div>
        <a className="boton boton-claro" href="#/guia" target="_blank" rel="noreferrer">❓ Guía</a>
        <button className="boton boton-claro" onClick={onSalir}>Cerrar sesión</button>
      </Encabezado>

      <main className="contenedor contenedor-ancho">
        <div className="sigem-titulo">
          <div>
            <h1>{SECCIONES.find((s) => s.id === seccion).titulo}</h1>
            <p>Reclamos vecinales anonimizados y clasificados por la IA municipal.</p>
          </div>
          <button className="boton boton-claro" onClick={cargar} disabled={cargando}>
            ↻ {cargando ? 'Actualizando…' : 'Actualizar datos'}
          </button>
        </div>

        <nav className="pestanas" role="tablist">
          {SECCIONES.map((s) => (
            <button key={s.id} role="tab" aria-selected={seccion === s.id}
              className={`pestana ${seccion === s.id ? 'activa' : ''}`} onClick={() => setSeccion(s.id)}>
              <span aria-hidden="true">{s.icono}</span> {s.titulo}
            </button>
          ))}
        </nav>

        {aviso && <div className="aviso-flotante" role="status">{aviso}</div>}

        {error ? (
          <div className="alerta-error" role="alert">
            ⚠️ {error} <button className="enlace" onClick={cargar}>Reintentar</button>
          </div>
        ) : cargando && !reclamos.length ? (
          <div className="cargando-bloque"><span className="girando" /> Cargando reclamos…
            <small>Si el servidor estaba inactivo, puede tardar hasta un minuto.</small></div>
        ) : (
          <>
            {seccion === 'gestion' && (
              <>
                <div className="contadores-estado">
                  {Object.entries(contadores).map(([valor, e]) => (
                    <div key={valor} className={`contador ${e.clase}`}>
                      <span className="contador-icono" aria-hidden="true">{e.icono}</span>
                      <span className="contador-valor">{conteo(valor)}</span>
                      <span className="contador-etiqueta">{e.etiqueta}</span>
                    </div>
                  ))}
                </div>
                <TablaReclamos reclamos={reclamos} onCambiarEstado={onCambiarEstado} onAuditar={onAuditar}
                  actualizando={actualizando} />
              </>
            )}
            {seccion === 'busqueda' && (
              <BusquedaFiltrado reclamos={reclamos} onCambiarEstado={onCambiarEstado} onAuditar={onAuditar}
                actualizando={actualizando} />
            )}
            {seccion === 'dashboard' && <DashboardGreenAI reclamos={reclamos} />}
          </>
        )}
      </main>

      <PiePagina />
    </div>
  );
}
