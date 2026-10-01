import time
from codecarbon import EmissionsTracker

from src.domain.entities.reclamo import Reclamo
from src.domain.ports.input.registrar_reclamo_port import RegistrarReclamoPort
from src.domain.ports.output.reclamo_repository_port import ReclamoRepositoryPort

class RegistrarReclamoUseCase(RegistrarReclamoPort):
    def __init__(self, repository: ReclamoRepositoryPort):
        self.repository = repository

    def ejecutar(self, titulo: str, descripcion: str, categoria: str):
        tracker = EmissionsTracker(
            project_name="Reclamos_Huancayo_GreenAI",
            save_to_file=False
        )
        tracker.start()

        time.sleep(1.5)
        nuevo_reclamo = Reclamo(titulo=titulo, descripcion=descripcion, categoria=categoria)

        emisiones_kg = tracker.stop()
        consumo_kwh = tracker.final_emissions_data.energy_consumed
        emisiones_gco2 = emisiones_kg * 1000

        print("\n==================================================")
        print("   TELEMETRIA GREEN AI (CODECARBON) - RESUMEN")
        print("==================================================")
        print(f"Emisiones de CO2e estimadas : {emisiones_kg:.8f} kg ({emisiones_gco2:.6f} gCO2e)")
        print(f"Consumo energético          : {consumo_kwh:.8f} kWh")
        print("Cumplimiento Criterio ICACIT: AG-C08 (Sostenibilidad)")
        print("==================================================\n")

        respuesta_db = self.repository.guardar(
            reclamo=nuevo_reclamo,
            emisiones_gco2=emisiones_gco2,
            consumo_kwh=consumo_kwh
        )

        return {
            "db_data": respuesta_db,
            "emisiones_gco2": emisiones_gco2,
            "consumo_kwh": consumo_kwh
        }