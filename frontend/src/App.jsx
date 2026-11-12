import { lazy, Suspense, useEffect, useState } from 'react';
import './App.css';
import Inicio from './pages/Inicio';
import PortalCiudadano from './pages/PortalCiudadano';
import LoginMunicipal from './pages/LoginMunicipal';
import ConsultaTramite from './pages/ConsultaTramite';
import GuiaUsuario from './pages/GuiaUsuario';

// El SIGEM (con los gráficos) se descarga solo cuando entra el personal municipal
const Sigem = lazy(() => import('./pages/Sigem'));

const VISTAS = ['inicio', 'ciudadano', 'consulta', 'login', 'sigem', 'guia'];
const vistaDesdeUrl = () => {
  const vista = window.location.hash.replace('#/', '');
  return VISTAS.includes(vista) ? vista : 'inicio';
};
// La sesión vale mientras no venza el token de Supabase Auth (expira en segundos Unix)
const leerSesion = () => {
  const sesion = JSON.parse(sessionStorage.getItem('sigem_sesion') || 'null');
  return sesion?.expira && sesion.expira * 1000 > Date.now() ? sesion : null;
};

export default function App() {
  const [vista, setVista] = useState(vistaDesdeUrl);
  const [sesion, setSesion] = useState(leerSesion);

  // La vista vive en la URL (#/ciudadano, #/sigem…) para que funcione el botón "Atrás"
  useEffect(() => {
    // Los enlaces (#/ciudadano, #/consulta…) cambian el hash: se muestra la vista y se sube al inicio
    const alCambiar = () => {
      setVista(vistaDesdeUrl());
      window.scrollTo(0, 0);
    };
    window.addEventListener('hashchange', alCambiar);
    return () => window.removeEventListener('hashchange', alCambiar);
  }, []);

  const irA = (destino) => {
    window.location.hash = `/${destino}`;
  };

  const ingresar = (usuario) => {
    sessionStorage.setItem('sigem_sesion', JSON.stringify(usuario));
    setSesion(usuario);
    irA('sigem');
  };

  const salir = () => {
    sessionStorage.removeItem('sigem_sesion');
    setSesion(null);
    irA('inicio');
  };

  if (vista === 'ciudadano') return <PortalCiudadano />;
  if (vista === 'consulta') return <ConsultaTramite />;
  if (vista === 'guia') return <GuiaUsuario />;
  if (vista === 'sigem' && sesion) {
    return (
      <Suspense fallback={<div className="cargando-bloque"><span className="girando" /> Cargando SIGEM…</div>}>
        <Sigem sesion={sesion} onSalir={salir} />
      </Suspense>
    );
  }
  if (vista === 'login' || vista === 'sigem') return <LoginMunicipal onIngresar={ingresar} />;
  return <Inicio />;
}
