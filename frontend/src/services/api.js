import { CATEGORIAS } from '../constantes';

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
// Columnas públicas: el hash del código secreto (codigo_hash) no se puede leer por la API
const COLUMNAS = 'id,created_at,titulo,descripcion,categoria,emisiones_gco2,consumo_kwh,estado,confianza,requiere_auditoria';

async function listarDesdeSupabase() {
  const filas = [];
  const lote = 1000; // Supabase devuelve como máximo 1000 filas por consulta
  for (let desde = 0; ; desde += lote) {
    const response = await fetch(`${SUPABASE_URL}/rest/v1/reclamos?select=${COLUMNAS}&order=id.desc`, {
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

// `token`: sesión del operador del SIGEM. El respaldo por backend exige ese token (OWASP A01).
export async function listarReclamos(token) {
  if (SUPABASE_URL && SUPABASE_KEY) {
    try {
      return await listarDesdeSupabase();
    } catch (err) {
      console.warn('No se pudo leer de Supabase, se usa el backend:', err.message);
    }
  }
  const autorizacion = token ? { Authorization: `Bearer ${token}` } : {};
  return solicitar('/api/reclamos', { headers: { 'Content-Type': 'application/json', ...autorizacion } })
    .then((r) => r.data);
}

// Los cambios del operador van directo a Supabase con el token de su sesión (HU-04 y HITL).
// `filtro` es una condición extra de PostgREST: si la fila no la cumple, no se actualiza nada.
async function actualizarReclamo(id, cambios, token, filtro = '') {
  if (!token) throw new Error('Su sesión expiró. Vuelva a iniciar sesión.');
  const url = `${SUPABASE_URL}/rest/v1/reclamos?id=eq.${encodeURIComponent(id)}${filtro}&select=${COLUMNAS}`;
  const response = await fetch(url, {
    method: 'PATCH',
    headers: {
      apikey: SUPABASE_KEY,
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      Prefer: 'return=representation',
    },
    body: JSON.stringify(cambios),
  });
  const datos = await response.json().catch(() => null);
  if (response.status === 401) throw new Error('Su sesión expiró. Vuelva a iniciar sesión.');
  if (!response.ok) throw new Error(datos?.message || `Supabase respondió ${response.status}`);
  // Sin filas devueltas: el reclamo no existe, no cumple el filtro o las políticas no permiten editarlo
  if (!datos?.length) throw new Error('No se encontró el reclamo o no tiene permiso para editarlo.');
  return datos[0];
}

const ESTADOS_VALIDOS = ['PENDIENTE', 'EN_PROCESO', 'RESUELTO'];

export function cambiarEstado(id, estado, token) {
  if (!ESTADOS_VALIDOS.includes(estado)) return Promise.reject(new Error('Estado inválido.'));
  return actualizarReclamo(id, { estado }, token);
}

// HITL: el operador confirma o corrige la categoría sugerida por la IA y libera el reclamo
// hacia la gerencia (pasa a "En proceso"). Solo actúa si el reclamo sigue pendiente de auditoría.
export function auditarReclamo(id, categoria, token) {
  if (!CATEGORIAS.some((c) => c.nombre === categoria)) return Promise.reject(new Error('Categoría inválida.'));
  return actualizarReclamo(
    id,
    { categoria, requiere_auditoria: false, estado: 'EN_PROCESO' },
    token,
    '&requiere_auditoria=eq.true',
  );
}

export const MLFLOW_URL = 'https://dagshub.com/Marcelo-CC/Taller-de-Proyectos-Software.mlflow/#/experiments/0';

// Módulo C: el vecino consulta su trámite con el número de ticket y el código secreto.
// La verificación ocurre dentro de Supabase (función consultar_reclamo): el hash nunca sale de la base.
export async function consultarReclamo(ticket, codigo) {
  if (!SUPABASE_URL || !SUPABASE_KEY) throw new Error('El servicio de consulta no está disponible.');
  const response = await fetch(`${SUPABASE_URL}/rest/v1/rpc/consultar_reclamo`, {
    method: 'POST',
    headers: { apikey: SUPABASE_KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify({ p_ticket: ticket, p_codigo: codigo }),
  });
  const datos = await response.json().catch(() => null);
  if (!response.ok) throw new Error('No se pudo realizar la consulta. Intente nuevamente.');
  return datos?.[0] || null;  // null: el ticket no existe o el código no coincide
}
