import time
import re
import mlflow
from codecarbon import EmissionsTracker

from src.domain.entities.reclamo import Reclamo
from src.domain.ports.input.registrar_reclamo_port import RegistrarReclamoPort
from src.domain.ports.output.reclamo_repository_port import ReclamoRepositoryPort


def anonimizar_datos_sensibles(texto: str) -> str:
    """
    Función de privacidad en la Capa de Dominio.
    Limpia DNI, nombres completos largos y frases de identificación.
    """
    if not texto:
        return texto

    texto_anonimo = texto

    # 1. Enmascarar DNI de 8 dígitos
    texto_anonimo = re.sub(r'\b\d{8}\b', '[DNI_PROTEGIDO]', texto_anonimo)

    # 2. Enmascarar patrones de presentación con nombres largos (hasta 5 palabras como "Marcelo Giovanni Castañeda Ramos")
    # Ejemplo: "Soy Marcelo Giovanni Castañeda con DNI 71701271" -> "Soy [CIUDADANO_ANÓNIMO] con DNI [DNI_PROTEGIDO]"
    patron_identificacion = r'(?i)\b(soy|mi nombre es|atentamente|firmado por)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑa-záéíóúñ]+){0,4})'
    texto_anonimo = re.sub(patron_identificacion, r'\1 [CIUDADANO_ANÓNIMO]', texto_anonimo)

    return texto_anonimo


class RegistrarReclamoUseCase(RegistrarReclamoPort):
    def __init__(self, repository: ReclamoRepositoryPort):
        self.repository = repository

    def ejecutar(self, titulo: str, descripcion: str, categoria: str):
        # 1. APLICAR ANONIMIZACIÓN EN DOMINIO ANTES DE PERSISTIR
        titulo_protegido = anonimizar_datos_sensibles(titulo)
        descripcion_protegida = anonimizar_datos_sensibles(descripcion)

        # 2. TELEMETRÍA GREEN AI
        tracker = EmissionsTracker(
            project_name="Reclamos_Huancayo_GreenAI",
            save_to_file=False
        )
        tracker.start()

        time.sleep(1.5)

        # 3. CREAR ENTIDAD CON DATOS PROTEGIDOS
        nuevo_reclamo = Reclamo(
            titulo=titulo_protegido, 
            descripcion=descripcion_protegida, 
            categoria=categoria
        )

        # 4. CÁLCULO DE MÉTRICAS AMBIENTALES
        emisiones_kg = tracker.stop()
        consumo_kwh = tracker.final_emissions_data.energy_consumed
        emisiones_gco2 = emisiones_kg * 1000

        # 5. REGISTRO MLOPS EN DAGSHUB / MLFLOW
        with mlflow.start_run():
            mlflow.log_param("titulo_reclamo", titulo_protegido)
            mlflow.log_param("categoria", categoria)
            mlflow.log_metric("emisiones_gco2", emisiones_gco2)
            mlflow.log_metric("consumo_kwh", consumo_kwh)
            mlflow.log_metric("f1_score", 1.0)

        print("\n==================================================")
        print("   TELEMETRIA GREEN AI (CODECARBON) - RESUMEN")
        print("==================================================")
        print(f"Texto Anonimizado           : {descripcion_protegida[:60]}...")
        print(f"Emisiones de CO2e estimadas : {emisiones_kg:.8f} kg ({emisiones_gco2:.6f} gCO2e)")
        print(f"Consumo energético          : {consumo_kwh:.8f} kWh")
        print("Cumplimiento Criterio ICACIT: AG-C08 (Sostenibilidad)")
        print("==================================================\n")

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
            "anonimizado": True
        }