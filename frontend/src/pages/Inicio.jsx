import { Encabezado, PiePagina } from '../components/Layout';

export default function Inicio() {
  return (
    <div className="pagina">
      <Encabezado subtitulo="Portal de Atención Vecinal">
        <a className="boton boton-claro" href="#/guia">❓ ¿Cómo usar?</a>
      </Encabezado>

      <section className="hero">
        <div className="hero-contenido">
          <span className="etiqueta-hero">Mesa de Partes Digital</span>
          <h1>Portal de Atención Vecinal</h1>
          <p>
            Registre sus reclamos sobre vías públicas, limpieza, parques y alumbrado. Nuestro sistema
            de inteligencia artificial clasifica cada caso y protege sus datos personales de forma automática.
          </p>
        </div>
      </section>

      <main className="contenedor modulos">
        <a className="tarjeta-modulo" href="#/ciudadano">
          <span className="modulo-icono modulo-a" aria-hidden="true">📝</span>
          <span className="modulo-etiqueta">Módulo A · Vecinos</span>
          <h2>Mesa de Partes Virtual y Reclamos Vecinales</h2>
          <p>
            Presente su reclamo sin necesidad de registrarse. Recibirá un número de ticket y la
            categoría asignada al instante.
          </p>
          <span className="modulo-accion">Registrar un reclamo →</span>
        </a>

        <a className="tarjeta-modulo" href="#/consulta">
          <span className="modulo-icono modulo-c" aria-hidden="true">🔎</span>
          <span className="modulo-etiqueta">Módulo C · Seguimiento</span>
          <h2>Consulta del Estado de su Trámite</h2>
          <p>
            Ingrese su número de ticket y su código secreto para ver en qué estado se encuentra
            su reclamo.
          </p>
          <span className="modulo-accion">Consultar mi trámite →</span>
        </a>

        <a className="tarjeta-modulo" href="#/login">
          <span className="modulo-icono modulo-b" aria-hidden="true">🏛️</span>
          <span className="modulo-etiqueta">Módulo B · Personal Municipal</span>
          <h2>Acceso al Sistema de Gestión Interna (SIGEM)</h2>
          <p>
            Gestión de estados de los reclamos, búsqueda avanzada y dashboard de telemetría
            Green AI.
          </p>
          <span className="modulo-accion">Acceso Personal Municipal →</span>
        </a>
      </main>

      <section className="contenedor franja-beneficios">
        <div><strong>🔒 Datos protegidos</strong><span>Su DNI, nombre y domicilio se anonimizan antes de guardarse.</span></div>
        <div><strong>⚡ Clasificación automática</strong><span>La IA asigna la categoría y deriva el reclamo al área correcta.</span></div>
        <div><strong>🌱 Green AI</strong><span>Cada inferencia mide su consumo energético y emisiones de CO₂.</span></div>
      </section>

      <p className="contenedor enlace-guia">
        ¿Primera vez? Lea la <a href="#/guia">guía rápida de usuario</a>: registrar, consultar y atender reclamos en pocos pasos.
      </p>

      <PiePagina />
    </div>
  );
}
