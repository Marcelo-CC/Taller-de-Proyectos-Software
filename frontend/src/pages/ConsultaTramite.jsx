import { useState } from 'react';
import { Encabezado, PiePagina, InsigniaCategoria, InsigniaEstado, TextoAnonimizado } from '../components/Layout';
import { consultarReclamo } from '../services/api';
import { ESTADOS, formatoFecha, formatoTicket } from '../constantes';

const DESCRIPCION_ESTADO = {
  PENDIENTE: 'Su reclamo fue recibido y está en cola para ser atendido por el área correspondiente.',
  EN_PROCESO: 'El área responsable ya está trabajando en la atención de su reclamo.',
  RESUELTO: 'El área responsable dio por atendido su reclamo. ¡Gracias por ayudar a mejorar Huancayo!',
};

// Acepta "1201", "01201" o "N° 01201"
const leerTicket = (texto) => Number(texto.replace(/\D/g, '')) || 0;
// Deja solo letras y números en mayúsculas, con el guion de formato XXXX-XXXX
const formatearCodigo = (texto) => {
  const limpio = texto.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 8);
  return limpio.length > 4 ? `${limpio.slice(0, 4)}-${limpio.slice(4)}` : limpio;
};

function LineaDeTiempo({ estado }) {
  const orden = Object.keys(ESTADOS);
  const actual = Math.max(orden.indexOf(estado), 0);
  return (
    <ol className="linea-tiempo" aria-label="Avance del trámite">
      {orden.map((valor, i) => (
        <li key={valor} className={i < actual ? 'hecho' : i === actual ? 'activo' : ''}
          aria-current={i === actual ? 'step' : undefined}>
          <span aria-hidden="true">{i < actual ? '✓' : i + 1}</span> {ESTADOS[valor].etiqueta}
        </li>
      ))}
    </ol>
  );
}

export default function ConsultaTramite() {
  const [ticket, setTicket] = useState('');
  const [codigo, setCodigo] = useState('');
  const [consultando, setConsultando] = useState(false);
  const [error, setError] = useState('');
  const [reclamo, setReclamo] = useState(null);

  const consultar = async (e) => {
    e.preventDefault();
    const numero = leerTicket(ticket);
    if (!numero) return setError('Ingrese el número de ticket que recibió al registrar su reclamo.');
    if (codigo.replace('-', '').length !== 8) return setError('El código secreto tiene 8 caracteres (ej. K7QF-3MZP).');

    setConsultando(true);
    setError('');
    try {
      const encontrado = await consultarReclamo(numero, codigo);
      // Mismo mensaje si falla el ticket o el código: no se revela cuál de los dos está mal
      if (!encontrado) setError('No encontramos un trámite con ese número de ticket y código secreto. Verifique los datos.');
      setReclamo(encontrado);
    } catch (err) {
      setError(err.message);
    } finally {
      setConsultando(false);
    }
  };

  const nuevaConsulta = () => {
    setReclamo(null);
    setTicket('');
    setCodigo('');
  };

  return (
    <div className="pagina">
      <Encabezado subtitulo="Consulta de Trámite">
        <a className="boton boton-claro" href="#/inicio">← Volver al inicio</a>
      </Encabezado>

      <main className="contenedor contenedor-angosto">
        {!reclamo ? (
          <form className="tarjeta" onSubmit={consultar} noValidate>
            <div className="consulta-cabecera">
              <h1>Consulte el estado de su reclamo</h1>
              <p>
                Ingrese el número de ticket y el código secreto que recibió al registrar su reclamo.
                Solo quien tiene ambos datos puede ver el trámite.
              </p>
            </div>

            <div className="rejilla-2">
              <label className="campo">
                <span className="campo-etiqueta">Número de ticket</span>
                <input value={ticket} onChange={(e) => setTicket(e.target.value)} maxLength={12}
                  placeholder="Ej. 01201" inputMode="numeric" autoComplete="off" />
              </label>
              <label className="campo">
                <span className="campo-etiqueta">Código secreto</span>
                <input className="entrada-codigo" value={codigo} onChange={(e) => setCodigo(formatearCodigo(e.target.value))}
                  placeholder="XXXX-XXXX" autoComplete="off" spellCheck={false} maxLength={9} />
              </label>
            </div>

            {error && <div className="alerta-error" role="alert">⚠️ {error}</div>}

            <button type="submit" className="boton boton-primario boton-grande" disabled={consultando}>
              {consultando ? (<><span className="girando" aria-hidden="true" /> Consultando…</>) : 'Consultar estado'}
            </button>
            <p className="nota-centrada">
              ¿Aún no tiene un ticket?{' '}
              <a className="enlace" href="#/ciudadano">Registre un reclamo</a>
            </p>
          </form>
        ) : (
          <section className="tarjeta" aria-live="polite">
            <div className="ticket-datos">
              <div>
                <span className="dato-etiqueta">Número de ticket</span>
                <span className="ticket-numero">{formatoTicket(reclamo.id)}</span>
              </div>
              <div>
                <span className="dato-etiqueta">Registrado el</span>
                <span>{formatoFecha(reclamo.created_at)}</span>
              </div>
              <div>
                <span className="dato-etiqueta">Categoría</span>
                <InsigniaCategoria categoria={reclamo.categoria} />
              </div>
              <div>
                <span className="dato-etiqueta">Estado actual</span>
                <InsigniaEstado estado={reclamo.estado} />
              </div>
            </div>

            <LineaDeTiempo estado={reclamo.estado} />
            <p className="estado-explicacion">{DESCRIPCION_ESTADO[reclamo.estado] || DESCRIPCION_ESTADO.PENDIENTE}</p>

            <div className="cuadro-anonimizado">
              <h3>🔒 Su reclamo</h3>
              <p><strong>{reclamo.titulo}</strong></p>
              <p className="texto-anonimizado"><TextoAnonimizado texto={reclamo.descripcion} /></p>
            </div>

            <div className="acciones-ticket">
              <button className="boton boton-claro" onClick={nuevaConsulta}>Consultar otro ticket</button>
              <a className="boton boton-primario" href="#/inicio">Volver al inicio</a>
            </div>
          </section>
        )}
      </main>

      <PiePagina />
    </div>
  );
}
