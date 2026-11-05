const API_URL = import.meta.env.VITE_API_URL || 'https://taller-de-proyectos-software.onrender.com';

async function solicitar(ruta, opciones = {}) {
  const response = await fetch(`${API_URL}${ruta}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opciones,
  });
  const datos = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(datos.detail || `Error ${response.status} en el servidor`);
  }
  return datos;
}

// Módulo A: Portal Ciudadano
export const registrarReclamo = (reclamo) =>
  solicitar('/api/reclamos', { method: 'POST', body: JSON.stringify(reclamo) });

// Módulo B: SIGEM
// La lista se lee directo de Supabase (solo lectura, no depende de que Render esté despierto).
// Si Supabase no está configurado o falla, se usa el backend como respaldo.
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL?.replace(/\/$/, '');
const SUPABASE_KEY = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

async function listarDesdeSupabase() {
  const filas = [];
  const lote = 1000; // Supabase devuelve como máximo 1000 filas por consulta
  for (let desde = 0; ; desde += lote) {
    const response = await fetch(`${SUPABASE_URL}/rest/v1/reclamos?select=*&order=id.desc`, {
      headers: { apikey: SUPABASE_KEY, Range: `${desde}-${desde + lote - 1}` },
    });
    if (!response.ok) throw new Error(`Supabase respondió ${response.status}`);
    const datos = await response.json();
    filas.push(...datos);
    if (datos.length < lote) return filas;
  }
}

// Login del personal municipal con Supabase Auth (usuarios creados en Authentication → Users)
export async function iniciarSesion(email, password) {
  if (!SUPABASE_URL || !SUPABASE_KEY) throw new Error('Falta configurar Supabase en el frontend.');
  const response = await fetch(`${SUPABASE_URL}/auth/v1/token?grant_type=password`, {
    method: 'POST',
    headers: { apikey: SUPABASE_KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  const datos = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(datos.error_code === 'invalid_credentials'
      ? 'Correo o contraseña incorrectos.'
      : datos.msg || 'No se pudo iniciar sesión. Intente nuevamente.');
  }
  return { email: datos.user.email, token: datos.access_token, expira: datos.expires_at };
}

export async function listarReclamos() {
  if (SUPABASE_URL && SUPABASE_KEY) {
    try {
      return await listarDesdeSupabase();
    } catch (err) {
      console.warn('No se pudo leer de Supabase, se usa el backend:', err.message);
    }
  }
  return solicitar('/api/reclamos').then((r) => r.data);
}

// El cambio de estado va directo a Supabase con el token de la sesión del operador (HU-04)
const ESTADOS_VALIDOS = ['PENDIENTE', 'EN_PROCESO', 'RESUELTO'];

export async function cambiarEstado(id, estado, token) {
  if (!ESTADOS_VALIDOS.includes(estado)) throw new Error('Estado inválido.');
  if (!token) throw new Error('Su sesión expiró. Vuelva a iniciar sesión.');
  const response = await fetch(`${SUPABASE_URL}/rest/v1/reclamos?id=eq.${encodeURIComponent(id)}`, {
    method: 'PATCH',
    headers: {
      apikey: SUPABASE_KEY,
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      Prefer: 'return=representation',
    },
    body: JSON.stringify({ estado }),
  });
  const datos = await response.json().catch(() => null);
  if (response.status === 401) throw new Error('Su sesión expiró. Vuelva a iniciar sesión.');
  if (!response.ok) throw new Error(datos?.message || `Supabase respondió ${response.status}`);
  // Sin filas devueltas: el reclamo no existe o las políticas de Supabase no permiten editarlo
  if (!datos?.length) throw new Error('No se encontró el reclamo o no tiene permiso para editarlo.');
  return datos[0];
}

export const MLFLOW_URL = 'https://dagshub.com/Marcelo-CC/Taller-de-Proyectos-Software.mlflow/#/experiments/0';
