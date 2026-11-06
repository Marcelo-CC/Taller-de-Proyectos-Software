import { useState } from 'react';
import { Encabezado, PiePagina, Escudo } from '../components/Layout';
import { iniciarSesion } from '../services/api';

export default function LoginMunicipal({ onIngresar }) {
  const [email, setEmail] = useState('');
  const [clave, setClave] = useState('');
  const [error, setError] = useState('');
  const [ingresando, setIngresando] = useState(false);

  const ingresar = async (e) => {
    e.preventDefault();
    setIngresando(true);
    setError('');
    try {
      // Las credenciales se validan contra Supabase Auth
      const sesion = await iniciarSesion(email.trim().toLowerCase(), clave);
      const usuario = sesion.email.split('@')[0];
      onIngresar({
        ...sesion,
        nombre: usuario.charAt(0).toUpperCase() + usuario.slice(1),
        rol: 'Personal Municipal',
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setIngresando(false);
    }
  };

  return (
    <div className="pagina">
      <Encabezado subtitulo="Sistema de Gestión Interna (SIGEM)">
        <a className="boton boton-claro" href="#/inicio">← Volver al inicio</a>
      </Encabezado>

      <main className="contenedor login">
        <form className="tarjeta tarjeta-login" onSubmit={ingresar}>
          <div className="login-cabecera">
            <Escudo tamano={56} />
            <h1>Acceso Personal Municipal</h1>
            <p>Ingrese con sus credenciales institucionales.</p>
          </div>

          <label className="campo">
            <span className="campo-etiqueta">Correo institucional</span>
            <input type="email" value={email} onChange={(e) => { setEmail(e.target.value); setError(''); }}
              placeholder="usuario@municipalidad.com" autoComplete="username" autoFocus required />
          </label>
          <label className="campo">
            <span className="campo-etiqueta">Contraseña</span>
            <input type="password" value={clave} onChange={(e) => { setClave(e.target.value); setError(''); }}
              autoComplete="current-password" required />
          </label>

          {error && <div className="alerta-error" role="alert">{error}</div>}

          <button type="submit" className="boton boton-primario boton-grande" disabled={ingresando}>
            {ingresando ? 'Verificando…' : 'Ingresar al SIGEM'}
          </button>
        </form>
      </main>

      <PiePagina />
    </div>
  );
}
