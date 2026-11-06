import { colorCategoria, ESTADOS, ESTADO_AUDITORIA } from '../constantes';

// Escudo de la Municipalidad Provincial de Huancayo (public/escudo-huancayo.png, proporción 138:160).
// `tamano` es la altura en píxeles; el ancho se calcula para no deformarlo.
export function Escudo({ tamano = 44 }) {
  return (
    <img src="/escudo-huancayo.png" alt="" aria-hidden="true"
      height={tamano} width={Math.round((tamano * 138) / 160)} />
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
