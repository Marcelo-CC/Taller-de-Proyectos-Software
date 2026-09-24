import { Reclamo } from '../../domain/entities/Reclamo.js';

export class RegistrarReclamoUseCase {
  constructor(reclamoRepository) {
    this.reclamoRepository = reclamoRepository;
  }

  async execute({ titulo, descripcion, categoria }) {
    if (!titulo || !descripcion) {
      throw new Error('El título y la descripción son obligatorios.');
    }
    const nuevoReclamo = new Reclamo({ titulo, descripcion, categoria });
    return await this.reclamoRepository.guardar(nuevoReclamo);
  }
}