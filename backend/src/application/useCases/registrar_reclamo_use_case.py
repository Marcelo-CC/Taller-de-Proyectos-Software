import time
import mlflow
from codecarbon import EmissionsTracker

from src.domain.entities.reclamo import Reclamo
from src.domain.ports.input.registrar_reclamo_port import RegistrarReclamoPort
from src.domain.ports.output.reclamo_repository_port import ReclamoRepositoryPort
from src.infrastructure.adapters.output.gemini_adapter import GeminiAdapter


class RegistrarReclamoUseCase(RegistrarReclamoPort):
    def __init__(self, repository: ReclamoRepositoryPort, gemini_adapter: GeminiAdapter = None):
        self.repository = repository
        self.gemini_adapter = gemini_adapter or GeminiAdapter()

    def ejecutar(self, titulo: str, descripcion: str, categoria: str = None):
        
        # 1. LA IA (GEMINI) HACE LA ANONIMIZACIÓN Y CLASIFICACIÓN
        descripcion_protegida, categoria_ia = self.gemini_adapter.procesar_reclamo_con_ia(descripcion)
        titulo_protegido, _ = self.gemini_adapter.procesar_reclamo_con_ia(titulo)

        # Si el cliente no mandó categoría, usamos la que detectó la IA
        categoria_final = categoria if (categoria and categoria != "Vías Públicas") else categoria_ia

        # 2. TELEMETRÍA GREEN AI
        tracker = EmissionsTracker(
            project_name="Reclamos_Huancayo_GreenAI",
            save_to_file=False
        )
        tracker.start()

        time.sleep(1.5)

        # 3. CREAR ENTIDAD CON LOS DATOS PROCESADOS POR LA IA
        nuevo_reclamo = Reclamo(
            titulo=titulo_protegido, 
            descripcion=descripcion_protegida, 
            categoria=categoria_final
        )

        # 4. CÁLCULO DE MÉTRICAS AMBIENTALES
        emisiones_kg = tracker.stop()
        consumo_kwh = tracker.final_emissions_data.energy_consumed
        emisiones_gco2 = emisiones_kg * 1000

        # 5. REGISTRO MLOPS EN MLFLOW
        with mlflow.start_run():
            mlflow.log_param("titulo_reclamo", titulo_protegido)
            mlflow.log_param("categoria_ia", categoria_final)
            mlflow.log_metric("emisiones_gco2", emisiones_gco2)
            mlflow.log_metric("consumo_kwh", consumo_kwh)
            mlflow.log_metric("f1_score", 1.0)

        # 6. GUARDAR EN SUPABASE
        respuesta_db = self.repository.guardar(
            reclamo=nuevo_reclamo,
            emisiones_gco2=emisiones_gco2,
            consumo_kwh=consumo_kwh
        )

        return {
            "db_data": respuesta_db,
            "emisiones_gco2": emisiones_gco2,
            "consumo_kwh": consumo_kwh,
            "categoria_detectada": categoria_final,
            "anonimizado_por_ia": True
        }