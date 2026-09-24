from codecarbon import EmissionsTracker
import time

# 1. Iniciar el rastreador de emisiones y energía de CodeCarbon
tracker = EmissionsTracker(project_name="Reclamos_Huancayo_GreenAI")
tracker.start()

print("==================================================")
print("  MUNICIPALIDAD PROVINCIAL DE HUANCAYO")
print("  Modulo de Categorizacion Automatizada de Reclamos")
print("==================================================\n")

# Simulacion de procesamiento de reclamo con modelo local (SLM / Ollama)
reclamo = "Bache peligroso y grieta profunda en la Av. Real cerca a la Plaza Constitucion"
print(f"[PROCESANDO RECLAMO]: '{reclamo}'")

time.sleep(2)  # Simula el tiempo de inferencia de la IA

categoria_detectada = "Vías Públicas / Infraestructura"
precision_estimada = "94.5%"

print(f"\n[RESULTADO IA]: Categoría asignada -> {categoria_detectada}")
print(f"[METRICA IA]: Precisión -> {precision_estimada}")
print("\nFinalizando inferencia y registrando impacto ambiental...\n")

# 2. Detener el rastreador y generar reporte de telemetría
emissions: float = tracker.stop()

print("==================================================")
print("  TELEMETRIA GREEN AI (CODECARBON) - RESUMEN")
print("==================================================")
print(f"Emisiones de CO2e estimadas : {emissions:.8f} kg")
print("Consumo energético          : Medido en Wh / kWh")
print("Cumplimiento Criterio ICACIT: AG-C08 (Sostenibilidad)")
print("==================================================")