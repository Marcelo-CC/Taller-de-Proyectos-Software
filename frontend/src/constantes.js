// Orden fijo de categorías: el color sigue a la categoría en toda la aplicación (validado para daltonismo)
export const CATEGORIAS = [
  { nombre: 'Vías Públicas', color: '#2a78d6' },
  { nombre: 'Limpieza Pública', color: '#eb6834' },
  { nombre: 'Parques y Jardines', color: '#1baf7a' },
  { nombre: 'Alumbrado', color: '#eda100' },
];

export const colorCategoria = (nombre) =>
  CATEGORIAS.find((c) => c.nombre === nombre)?.color || '#8a8984';

// Estados (HU-04): siempre con ícono + texto, nunca solo color
export const ESTADOS = {
  PENDIENTE: { etiqueta: 'Pendiente', icono: '●', clase: 'estado-pendiente' },
  EN_PROCESO: { etiqueta: 'En proceso', icono: '◐', clase: 'estado-proceso' },
  RESUELTO: { etiqueta: 'Resuelto', icono: '✓', clase: 'estado-resuelto' },
};

export const formatoFecha = (iso) =>
  new Date(iso).toLocaleString('es-PE', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
  });

export const formatoTicket = (id) => `N° ${String(id).padStart(5, '0')}`;
