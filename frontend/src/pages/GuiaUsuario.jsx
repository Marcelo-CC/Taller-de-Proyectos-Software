import { Encabezado, PiePagina } from '../components/Layout';

// Guía rápida de usuario (FURPS+ Usabilidad): cómo usar el portal y el SIGEM en pocos pasos.
// La versión para imprimir está en docs/GUIA_RAPIDA_USUARIO.md.

const PASOS_VECINO = [
  {
    titulo: 'Entre a «Registrar un reclamo»',
    texto: 'Desde la página de inicio elija el Módulo A. No necesita crear una cuenta.',
  },
  {
    titulo: 'Complete sus datos y describa el problema',
    texto: 'Escriba su nombre, DNI, un teléfono o correo y su domicilio. Luego indique un título, la ubicación '
      + 'exacta del problema (calle, cuadra y una referencia) y qué ocurre, desde cuándo y cómo afecta a los vecinos.',
  },
  {
    titulo: 'Envíe el reclamo',
    texto: 'La inteligencia artificial corrige la redacción, protege sus datos personales y asigna la categoría '
      + '(Vías Públicas, Limpieza Pública, Parques y Jardines o Alumbrado). Tarda unos segundos.',
  },
  {
    titulo: 'Guarde su número de ticket y su código secreto',
    texto: 'Aparecen en la pantalla de confirmación. El código se muestra una sola vez: cópielo, anótelo o use '
      + '«Imprimir constancia». Sin el código nadie puede ver su reclamo, ni siquiera usted.',
    alerta: true,
  },
  {
    titulo: 'Consulte el avance cuando quiera',
    texto: 'En «Consultar mi trámite» (Módulo C) escriba el número de ticket y el código. Verá el estado: '
      + 'Pendiente, En proceso o Resuelto.',
  },
];

const PASOS_PERSONAL = [
  {
    titulo: 'Ingrese al SIGEM',
    texto: 'En la página de inicio elija «Acceso Personal Municipal» (Módulo B) e ingrese el correo y la '
      + 'contraseña que le asignó el administrador. La sesión se cierra sola al vencer.',
  },
  {
    titulo: 'Revise el Panel de Control',
    texto: 'Los contadores muestran cuántos reclamos hay en cada estado. La tabla lista 25 reclamos por página, '
      + 'del más reciente al más antiguo. Use «Ver completo» para leer todo el texto y «Actualizar datos» para '
      + 'traer los reclamos nuevos.',
  },
  {
    titulo: 'Atienda los reclamos «Pendiente de auditoría HITL»',
    texto: 'Son reclamos en los que la IA tuvo una confianza menor al 70 %. Lea el texto, elija la categoría '
      + 'correcta en la lista y presione «Confirmar y derivar» (o «Corregir y derivar» si la cambió). El reclamo '
      + 'pasa a «En proceso» en su gerencia.',
    alerta: true,
  },
  {
    titulo: 'Actualice el estado de cada reclamo',
    texto: 'En la columna Estado elija «En proceso» cuando el área empiece a atenderlo y «Resuelto» al terminar. '
      + 'El vecino ve el cambio al consultar su trámite.',
  },
  {
    titulo: 'Busque y filtre',
    texto: 'En «Búsqueda y Filtrado» escriba una palabra del reclamo (por ejemplo «poste» o «basura») y filtre por '
      + 'categoría o estado. La búsqueda se aplica mientras escribe.',
  },
  {
    titulo: 'Consulte y descargue el Dashboard Green AI',
    texto: 'Muestra la energía y las emisiones de CO₂ de la IA y los reclamos por categoría. Con «Descargar CSV» '
      + 'obtiene el detalle para Excel y con «Reporte PDF» un resumen listo para imprimir o guardar como PDF.',
  },
];

const ESTADOS_GUIA = [
  ['● Pendiente', 'El reclamo fue recibido y espera ser atendido.'],
  ['◐ En proceso', 'El área responsable ya está trabajando en él.'],
  ['✓ Resuelto', 'El área dio por atendido el reclamo.'],
  ['⚠ Pendiente de auditoría HITL', 'Solo lo ve el personal: un especialista confirma la categoría antes de derivarlo.'],
];

function Pasos({ pasos }) {
  return (
    <ol className="guia-pasos">
      {pasos.map((p, i) => (
        <li key={p.titulo} className={p.alerta ? 'guia-paso guia-alerta' : 'guia-paso'}>
          <span className="guia-numero" aria-hidden="true">{i + 1}</span>
          <div>
            <strong>{p.titulo}</strong>
            <p>{p.texto}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}

export default function GuiaUsuario() {
  return (
    <div className="pagina">
      <Encabezado subtitulo="Guía rápida de usuario">
        <a className="boton boton-claro" href="#/inicio">← Volver al inicio</a>
      </Encabezado>

      <main className="contenedor contenedor-angosto guia">
        <h1>¿Cómo usar el Portal de Atención Vecinal?</h1>
        <p className="guia-intro">
          Esta guía explica en pocos pasos cómo presentar y seguir un reclamo, y cómo lo atiende el personal
          municipal en el Sistema de Gestión Interna (SIGEM).
        </p>

        <nav className="guia-indice" aria-label="Contenido de la guía">
          <a href="#guia-vecino" onClick={(e) => { e.preventDefault(); document.getElementById('guia-vecino')?.scrollIntoView(); }}>
            📝 Para vecinos
          </a>
          <a href="#guia-personal" onClick={(e) => { e.preventDefault(); document.getElementById('guia-personal')?.scrollIntoView(); }}>
            🏛️ Para personal municipal
          </a>
        </nav>

        <section id="guia-vecino" className="tarjeta guia-seccion">
          <h2>📝 Para vecinos: presentar y seguir un reclamo</h2>
          <Pasos pasos={PASOS_VECINO} />
          <div className="guia-botones">
            <a className="boton boton-primario" href="#/ciudadano">Registrar un reclamo</a>
            <a className="boton boton-claro" href="#/consulta">Consultar mi trámite</a>
          </div>
        </section>

        <section className="tarjeta guia-seccion">
          <h2>¿Qué significa cada estado?</h2>
          <dl className="guia-estados">
            {ESTADOS_GUIA.map(([estado, significado]) => (
              <div key={estado}><dt>{estado}</dt><dd>{significado}</dd></div>
            ))}
          </dl>
        </section>

        <section id="guia-personal" className="tarjeta guia-seccion">
          <h2>🏛️ Para personal municipal: atender reclamos en el SIGEM</h2>
          <Pasos pasos={PASOS_PERSONAL} />
          <div className="guia-botones">
            <a className="boton boton-primario" href="#/login">Ingresar al SIGEM</a>
          </div>
        </section>

        <section className="tarjeta guia-seccion">
          <h2>🔒 Sus datos están protegidos</h2>
          <p>
            Su nombre, DNI, contacto y domicilio se reemplazan por etiquetas como [DNI_PROTEGIDO] antes de guardarse
            y no se envían al servicio de inteligencia artificial (Ley N° 29733). La ubicación del problema sí es
            pública, porque es el lugar donde se debe atender.
          </p>
        </section>
      </main>

      <PiePagina />
    </div>
  );
}
