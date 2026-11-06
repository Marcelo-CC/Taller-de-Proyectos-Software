import re
import mlflow
from codecarbon import EmissionsTracker

from src.domain.entities.reclamo import Reclamo
from src.domain.valueObjects import codigo_consulta
from src.domain.services import evaluacion_confianza
from src.domain.ports.input.registrar_reclamo_port import RegistrarReclamoPort
from src.domain.ports.output.reclamo_repository_port import ReclamoRepositoryPort
from src.infrastructure.adapters.output.gemini_adapter import GeminiAdapter


class RegistrarReclamoUseCase(RegistrarReclamoPort):
    def __init__(self, repository: ReclamoRepositoryPort, gemini_adapter: GeminiAdapter = None):
        self.repository = repository
        self.gemini_adapter = gemini_adapter or GeminiAdapter()

    @staticmethod
    def _enmascarar(texto: str, datos_personales) -> str:
        # Si el vecino repite su nombre, DNI, domicilio o contacto dentro del texto, también se tapa
        texto = texto or ""
        for valor, marcador in datos_personales:
            if valor and len(valor.strip()) >= 3:
                texto = re.sub(re.escape(valor.strip()), marcador, texto, flags=re.IGNORECASE)
        return texto

    def ejecutar(self, titulo: str, descripcion: str, categoria: str = None, dni: str = "",
                 nombre: str = "", direccion: str = "", contacto: str = "", ubicacion: str = ""):

        # 1. LOS DATOS PERSONALES SE ENMASCARAN AQUÍ: nunca se envían a Gemini
        datos_personales = [
            (dni, "[DNI_PROTEGIDO]"),
            (nombre, "[CIUDADANO_ANÓNIMO]"),
            (direccion, "[DATOS_PROTEGIDOS]"),
            (contacto, "[DATOS_PROTEGIDOS]"),
        ]
        titulo_limpio = self._enmascarar(titulo, datos_personales)
        descripcion_limpia = self._enmascarar(descripcion, datos_personales)

        # 2. TELEMETRÍA GREEN AI: se mide el consumo de la inferencia con Gemini
        tracker = EmissionsTracker(
            project_name="Reclamos_Huancayo_GreenAI",
            save_to_file=False
        )
        tracker.start()

        # 3. LA IA (GEMINI) CORRIGE, ANONIMIZA EL TEXTO LIBRE Y CLASIFICA (una sola llamada)
        titulo_protegido, ubicacion_corregida, detalle, categoria_ia, senales = self.gemini_adapter.procesar_reclamo_con_ia(
            titulo_limpio, descripcion_limpia, ubicacion
        )

        # 4. CÁLCULO DE MÉTRICAS AMBIENTALES
        emisiones_kg = tracker.stop() or 0.0
        consumo_kwh = tracker.final_emissions_data.energy_consumed if tracker.final_emissions_data else 0.0
        emisiones_gco2 = emisiones_kg * 1000

        # Si el cliente no mandó categoría, usamos la que detectó la IA
        categoria_final = categoria if (categoria and categoria != "Vías Públicas") else categoria_ia

        # HITL: confianza de la clasificación y regla de enrutamiento (umbral 70 %)
        confianza = evaluacion_confianza.evaluar(
            probabilidades=senales["probabilidades"],
            categoria=categoria_final,
            problematicas=senales["problematicas"],
            texto=descripcion_limpia,
            clasificado_por_ia=senales["clasificado_por_ia"],
        )
        # True → queda retenido como "Pendiente de auditoría HITL"; False → enrutamiento directo
        requiere_auditoria = evaluacion_confianza.requiere_auditoria(confianza)

        # 5. TEXTO FINAL CON FORMATO FIJO
        partes = []
        if dni or nombre or direccion:
            partes.append("Soy [CIUDADANO_ANÓNIMO] con DNI [DNI_PROTEGIDO], domiciliado en [DATOS_PROTEGIDOS].")
        if ubicacion_corregida:
            partes.append(f"Ubicación del problema: {ubicacion_corregida.rstrip('.')}.")
        partes.append(f"Detalle del problema: {detalle}")
        descripcion_protegida = " ".join(partes)

        nuevo_reclamo = Reclamo(
            titulo=titulo_protegido,
            descripcion=descripcion_protegida,
            categoria=categoria_final,
            confianza=confianza,
            requiere_auditoria=requiere_auditoria
        )

        # Resumen en consola; si algo falla al imprimir, no interrumpe el registro
        try:
            print("\n==================================================")
            print("   TELEMETRIA GREEN AI (CODECARBON) - RESUMEN")
            print("==================================================")
            print(f"Texto Anonimizado           : {str(descripcion_protegida)[:60]}...")
            print(f"Emisiones de CO2e estimadas : {emisiones_kg:.8f} kg ({emisiones_gco2:.6f} gCO2e)")
            print(f"Consumo energético          : {consumo_kwh:.8f} kWh")
            print(f"Confianza de la IA (HITL)   : {confianza:.0%} -> "
                  f"{'Pendiente de auditoría HITL' if requiere_auditoria else 'Enrutamiento directo'}")
            print("Cumplimiento Criterio ICACIT: AG-C08 (Sostenibilidad)")
            print("==================================================\n", flush=True)
        except Exception as e:
            print(f"⚠️ No se pudo imprimir el resumen de telemetría: {e}")

        # 6. REGISTRO MLOPS EN MLFLOW (si DagsHub falla, el reclamo se guarda igual)
        try:
            with mlflow.start_run():
                mlflow.log_param("titulo_reclamo", titulo_protegido[:250])
                mlflow.log_param("categoria_ia", categoria_final)
                mlflow.log_metric("emisiones_gco2", emisiones_gco2)
                mlflow.log_metric("consumo_kwh", consumo_kwh)
                mlflow.log_metric("confianza_ia", confianza)
                mlflow.log_param("requiere_auditoria", requiere_auditoria)
        except Exception as e:
            print(f"⚠️ No se pudo registrar en MLflow: {e}", flush=True)

        # 7. CÓDIGO SECRETO DE CONSULTA (Módulo C): se guarda solo su hash y se muestra una sola vez
        codigo = codigo_consulta.generar()

        # 8. GUARDAR EN SUPABASE
        respuesta_db = self.repository.guardar(
            reclamo=nuevo_reclamo,
            emisiones_gco2=emisiones_gco2,
            consumo_kwh=consumo_kwh,
            codigo_hash=codigo_consulta.hashear(codigo)
        )

        return {
            "db_data": respuesta_db,
            "ticket": respuesta_db[0]["id"] if respuesta_db else None,
            "codigo_consulta": codigo,
            "titulo_anonimizado": titulo_protegido,
            "descripcion_anonimizada": descripcion_protegida,
            "emisiones_gco2": emisiones_gco2,
            "consumo_kwh": consumo_kwh,
            "categoria_detectada": categoria_final,
            "confianza": confianza,
            "requiere_auditoria": requiere_auditoria,
            "anonimizado_por_ia": True
        }
