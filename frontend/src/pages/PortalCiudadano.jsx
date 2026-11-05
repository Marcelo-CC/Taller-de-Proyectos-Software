import { useState } from 'react';
import { Encabezado, PiePagina, InsigniaCategoria, TextoAnonimizado } from '../components/Layout';
import { registrarReclamo } from '../services/api';
import { formatoTicket } from '../constantes';

const FORMULARIO_VACIO = {
  nombre: '', dni: '', contacto: '', direccion: '',
  titulo: '', ubicacion: '', descripcion: '',
};

const SOLO_LETRAS = /[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]/g;
const ES_CELULAR = /^9\d{8}$/;
const ES_CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validar(f) {
  const errores = {};
  if (f.nombre.trim().split(/\s+/).length < 2) errores.nombre = 'Ingrese nombres y apellidos completos.';
  if (!/^\d{8}$/.test(f.dni)) errores.dni = 'El DNI debe tener exactamente 8 dígitos numéricos.';
  const contacto = f.contacto.trim().replace(/\s/g, '');
  if (!ES_CELULAR.test(contacto) && !ES_CORREO.test(f.contacto.trim())) {
    errores.contacto = 'Ingrese un celular de 9 dígitos (ej. 987654321) o un correo válido.';
  }
  if (f.direccion.trim().length < 5) errores.direccion = 'Ingrese la dirección de su domicilio.';
  if (f.titulo.trim().length < 5) errores.titulo = 'El título debe tener al menos 5 caracteres.';
  if (f.ubicacion.trim().length < 5) errores.ubicacion = 'Indique calle, cuadra o una referencia del lugar.';
  if (f.descripcion.trim().length < 15) errores.descripcion = 'Describa el problema con un poco más de detalle.';
  return errores;
}

function Campo({ etiqueta, error, ayuda, children }) {
  return (
    <label className={`campo ${error ? 'con-error' : ''}`}>
      <span className="campo-etiqueta">{etiqueta}</span>
      {children}
      {error ? <span className="campo-error">{error}</span> : ayuda && <span className="campo-ayuda">{ayuda}</span>}
    </label>
  );
}

export default function PortalCiudadano({ irA }) {
  const [form, setForm] = useState(FORMULARIO_VACIO);
  const [errores, setErrores] = useState({});
  const [enviando, setEnviando] = useState(false);
  const [errorServidor, setErrorServidor] = useState('');
  const [ticket, setTicket] = useState(null);

  const cambiar = (campo, filtro) => (e) => {
    const valor = filtro ? filtro(e.target.value) : e.target.value;
    setForm({ ...form, [campo]: valor });
    if (errores[campo]) setErrores({ ...errores, [campo]: undefined });
  };

  const enviar = async (e) => {
    e.preventDefault();
    const encontrados = validar(form);
    setErrores(encontrados);
    if (Object.keys(encontrados).length) return;

    setEnviando(true);
    setErrorServidor('');
    try {
      // Campos separados: el backend enmascara los datos personales sin enviarlos a Gemini
      const respuesta = await registrarReclamo({
        titulo: form.titulo.trim(),
        ubicacion: form.ubicacion.trim(),
        descripcion: form.descripcion.trim(),
        nombre: form.nombre.trim(),
        dni: form.dni,
        direccion: form.direccion.trim(),
        contacto: form.contacto.trim(),
      });
      setTicket(respuesta);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setErrorServidor(err.message || 'No se pudo conectar con el servidor.');
    } finally {
      setEnviando(false);
    }
  };

  const nuevoReclamo = () => {
    setForm(FORMULARIO_VACIO);
    setTicket(null);
  };

  return (
    <div className="pagina">
      <Encabezado onInicio={() => irA('inicio')} subtitulo="Mesa de Partes Virtual">
        <button className="boton boton-claro" onClick={() => irA('inicio')}>← Volver al inicio</button>
      </Encabezado>

      <main className="contenedor contenedor-angosto">
        <ol className="pasos" aria-label="Progreso del trámite">
          <li className={!ticket ? 'activo' : 'hecho'}><span>1</span> Registro de incidencia</li>
          <li className={ticket ? 'activo' : ''}><span>2</span> Confirmación y ticket</li>
        </ol>

        {!ticket ? (
          <form className="tarjeta" onSubmit={enviar} noValidate>
            <div className="aviso-privacidad" role="note">
              <strong>🔒 Sus datos personales están protegidos.</strong> Su nombre, DNI, contacto y domicilio
              se anonimizan automáticamente y no se envían al servicio de inteligencia artificial ni se
              guardan de forma visible.
            </div>

            <fieldset>
              <legend>Datos del solicitante</legend>
              <div className="rejilla-2">
                <Campo etiqueta="Nombres y apellidos completos" error={errores.nombre}>
                  <input value={form.nombre} onChange={cambiar('nombre', (v) => v.replace(SOLO_LETRAS, ''))}
                    placeholder="Ej. Rosa Elena Huamán Quispe" autoComplete="name" />
                </Campo>
                <Campo etiqueta="DNI" error={errores.dni}>
                  <input value={form.dni} onChange={cambiar('dni', (v) => v.replace(/\D/g, '').slice(0, 8))}
                    placeholder="8 dígitos" inputMode="numeric" maxLength={8} />
                </Campo>
                <Campo etiqueta="Teléfono o correo electrónico" error={errores.contacto}>
                  <input value={form.contacto} onChange={cambiar('contacto')}
                    placeholder="Ej. 987654321 o vecino@correo.com" autoComplete="email" />
                </Campo>
                <Campo etiqueta="Dirección del domicilio" error={errores.direccion}>
                  <input value={form.direccion} onChange={cambiar('direccion')}
                    placeholder="Ej. Jr. Ancash 845, El Tambo" autoComplete="street-address" />
                </Campo>
              </div>
            </fieldset>

            <fieldset>
              <legend>Detalle del reclamo</legend>
              <Campo etiqueta="Título del reclamo" error={errores.titulo}>
                <input value={form.titulo} onChange={cambiar('titulo')} maxLength={120}
                  placeholder="Ej. Poste sin luz en la cuadra" />
              </Campo>
              <Campo etiqueta="Ubicación exacta del problema" error={errores.ubicacion}
                ayuda="Calle, cuadra y una referencia. Este dato es público y no se anonimiza.">
                <input value={form.ubicacion} onChange={cambiar('ubicacion')}
                  placeholder="Ej. Jr. Cusco cuadra 5, esquina con Calle Real" />
              </Campo>
              <Campo etiqueta="Descripción detallada del incidente" error={errores.descripcion}
                ayuda={`${form.descripcion.length}/1500 caracteres`}>
                <textarea value={form.descripcion} onChange={cambiar('descripcion')} rows={5} maxLength={1500}
                  placeholder="Describa qué ocurre, desde cuándo y cómo afecta a los vecinos." />
              </Campo>
            </fieldset>

            {errorServidor && <div className="alerta-error" role="alert">⚠️ {errorServidor}</div>}

            <button type="submit" className="boton boton-primario boton-grande" disabled={enviando}>
              {enviando ? (<><span className="girando" aria-hidden="true" /> Procesando con la IA Municipal…</>)
                : 'Enviar Reclamo a la IA Municipal'}
            </button>
            {enviando && (
              <p className="nota-centrada">
                Esto puede tardar unos segundos. Si el servidor estaba inactivo, la primera solicitud puede
                demorar hasta un minuto.
              </p>
            )}
          </form>
        ) : (
          <section className="tarjeta ticket" aria-live="polite">
            <div className="ticket-cabecera">
              <span className="ticket-check" aria-hidden="true">✓</span>
              <div>
                <h2>¡Reclamo registrado con éxito!</h2>
                <p>Conserve su número de ticket para hacer seguimiento.</p>
              </div>
            </div>

            <div className="ticket-datos">
              <div>
                <span className="dato-etiqueta">Número de ticket</span>
                <span className="ticket-numero">{ticket.ticket ? formatoTicket(ticket.ticket) : '—'}</span>
              </div>
              <div>
                <span className="dato-etiqueta">Categoría asignada por la IA</span>
                <InsigniaCategoria categoria={ticket.categoria_asignada} />
              </div>
              <div>
                <span className="dato-etiqueta">Estado</span>
                <span className="insignia-estado estado-pendiente">● Pendiente</span>
              </div>
            </div>

            <div className="cuadro-anonimizado">
              <h3>🔒 Así se guardó su reclamo</h3>
              <p className="nota">
                Sus datos personales fueron reemplazados por etiquetas protegidas, en cumplimiento de la
                Ley N° 29733 de Protección de Datos Personales.
              </p>
              <p><strong>{ticket.titulo_anonimizado}</strong></p>
              <p className="texto-anonimizado"><TextoAnonimizado texto={ticket.descripcion_anonimizada} /></p>
            </div>

            <div className="sello-green">
              <span aria-hidden="true">🌱</span>
              <p>
                <strong>Sello Green AI:</strong> tu reclamo fue categorizado con un impacto ambiental de{' '}
                <strong>{ticket.telemetria_green_ai.emisiones_gco2.toFixed(4)} gCO₂e</strong>{' '}
                ({(ticket.telemetria_green_ai.consumo_kwh * 1000).toFixed(4)} Wh de energía).
              </p>
            </div>

            <div className="acciones-ticket">
              <button className="boton boton-claro" onClick={() => window.print()}>🖨️ Imprimir constancia</button>
              <button className="boton boton-primario" onClick={nuevoReclamo}>Registrar otro reclamo</button>
            </div>
          </section>
        )}
      </main>

      <PiePagina />
    </div>
  );
}
