import { ReclamoRepositoryPort } from '../../../domain/ports/ReclamoRepositoryPort.js';

export class SupabaseReclamoRepository extends ReclamoRepositoryPort {
  constructor(supabaseClient) {
    super();
    this.supabase = supabaseClient;
  }

  async guardar(reclamo) {
    const { data, error } = await this.supabase
      .from('reclamos')
      .insert([{
        titulo: reclamo.titulo,
        descripcion: reclamo.descripcion,
        categoria: reclamo.categoria,
        estado: reclamo.estado
      }])
      .select();

    if (error) throw new Error(error.message);
    return data[0];
  }
}