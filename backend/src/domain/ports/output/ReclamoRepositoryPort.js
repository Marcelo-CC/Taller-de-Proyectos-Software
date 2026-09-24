export class ReclamoRepositoryPort {
  async guardar(reclamo) {
    throw new Error('Método guardar() debe ser implementado por un adaptador de salida');
  }
  async obtenerTodos() {
    throw new Error('Método obtenerTodos() debe ser implementado por un adaptador de salida');
  }
}