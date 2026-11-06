import { colorCategoria, ESTADOS, ESTADO_AUDITORIA } from '../constantes';

export function Escudo({ tamano = 44 }) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 48 48" aria-hidden="true">
      <path d="M24 3 41 9v14c0 11-7.4 19-17 22C14.4 42 7 34 7 23V9z" fill="#0b3a6b" />
      <path d="M24 7.5 37 12v11c0 8.7-5.6 15-13 17.6C16.6 38 11 31.7 11 23V12z" fill="#fff" />
      <path d="M14 30 21 20l4 5 3-4 6 9z" fill="#1baf7a" />
      <circle cx="30" cy="16" r="2.6" fill="#eda100" />
      <rect x="11" y="30" width="26" height="3" fill="#c8102e" />
    </svg>
  );
}

export function Encabezado({ subtitulo, children }) {
  return (
    <header className="encabezado">
      <div className="franja-superior">
        <span>Gobierno Local · Región Junín</span>
        <span>Plataforma de Atención Vecinal</span>
      </div>
      <div className="barra-institucional">
        <a className="marca" href="#/inicio" aria-label="Ir al inicio">
          <Escudo />
          <span>
            <strong>Municipalidad Provincial de Huancayo</strong>
            <small>{subtitulo}</small>
          </span>
        </a>
        <div className="acciones-encabezado">{children}</div>
      </div>
    </header>
  );
}

export function PiePagina() {
  return (
    <footer className="pie">
      <div>
        <strong>Municipalidad Provincial de Huancayo</strong>
        <span>Huancayo · Junín · Perú</span>
      </div>
      <div className="pie-legal">
        Datos personales tratados conforme a la Ley N° 29733, Ley de Protección de Datos Personales.
        <span className="sello-verde">🌱 Plataforma Green AI con medición de huella de carbono</span>
      </div>
    </footer>
  );
}

export function InsigniaCategoria({ categoria }) {
  return (
    <span className="insignia-categoria">
      <span className="punto" style={{ background: colorCategoria(categoria) }} aria-hidden="true" />
      {categoria}
    </span>
  );
}

// Resalta [CIUDADANO_ANÓNIMO], [DNI_PROTEGIDO] y [DATOS_PROTEGIDOS] dentro del texto
export function TextoAnonimizado({ texto = '', resaltar = '' }) {
  const partes = texto.split(/(\[(?:CIUDADANO_ANÓNIMO|DNI_PROTEGIDO|DATOS_PROTEGIDOS)\])/g);
  return partes.map((parte, i) =>
    parte.startsWith('[') && parte.endsWith(']')
      ? <mark key={i} className="etiqueta-protegida">{parte}</mark>
      : <Resaltado key={i} texto={parte} termino={resaltar} />
  );
}

function Resaltado({ texto, termino }) {
  if (!termino) return texto;
  const escapado = termino.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return texto.split(new RegExp(`(${escapado})`, 'gi')).map((p, i) =>
    p.toLowerCase() === termino.toLowerCase() ? <mark key={i} className="coincidencia">{p}</mark> : p
  );
}

export function InsigniaEstado({ estado }) {
  const e = estado === 'AUDITORIA' ? ESTADO_AUDITORIA : ESTADOS[estado] || ESTADOS.PENDIENTE;
  return (
    <span className={`insignia-estado ${e.clase}`}>
      <span aria-hidden="true">{e.icono}</span> {e.etiqueta}
    </span>
  );
}
