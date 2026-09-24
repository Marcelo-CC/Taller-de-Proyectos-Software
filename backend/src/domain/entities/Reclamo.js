export class Reclamo {
  constructor({ id, titulo, descripcion, categoria, estado = 'Pendiente', creadoEn }) {
    this.id = id;
    this.titulo = titulo;
    this.descripcion = descripcion;
    this.categoria = categoria;
    this.estado = estado;
    this.creadoEn = creadoEn || new Date();
  }
}