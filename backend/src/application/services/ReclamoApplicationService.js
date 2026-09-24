export class ReclamoApplicationService {
  constructor(registrarReclamoUseCase) {
    this.registrarReclamoUseCase = registrarReclamoUseCase;
  }

  async procesarNuevoReclamo(datos) {
    return await this.registrarReclamoUseCase.execute(datos);
  }
}