export class ReclamoRepositoryPort {
  async guardar(reclamo) {
    throw new Error('Método guardar() debe ser implementado por un adaptador');
  }
  async obtenerTodos() {
    throw new Error('Método obtenerTodos() debe ser implementado por un adaptador');
  }
}