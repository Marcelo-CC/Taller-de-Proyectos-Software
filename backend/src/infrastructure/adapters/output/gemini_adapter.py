import os
import re
import json
from google import genai
from google.genai import types

CATEGORIAS_VALIDAS = ["Vías Públicas", "Limpieza Pública", "Parques y Jardines", "Alumbrado"]

# Palabras clave para clasificar cuando Gemini no está disponible
PALABRAS_CLAVE = {
    "Limpieza Pública": ["basura", "desmonte", "residuo", "bolsas", "olor", "plaga", "limpieza", "recojo", "ratas"],
    "Parques y Jardines": ["parque", "jardín", "jardin", "árbol", "arbol", "pasto", "plaza", "áreas verdes", "areas verdes"],
    "Alumbrado": ["alumbrado", "poste", "foco", "luz", "luminaria", "oscuro", "apagado"],
}

class GeminiAdapter:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("⚠️ GEMINI_API_KEY no está configurada en el entorno.")

        # Timeout de 30 s (en ms) y un solo reintento para que el reclamo no se quede colgado
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=30_000,
                retry_options=types.HttpRetryOptions(attempts=2)
            )
        )
        # gemini-1.5-flash fue retirado; el alias "latest" apunta siempre al Flash vigente.
        # Si el modelo principal está saturado (503/504) se intenta con el de respaldo.
        self.modelos = [
            os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
            os.getenv("GEMINI_MODEL_RESPALDO", "gemini-flash-lite-latest"),
        ]

    def procesar_reclamo_con_ia(self, texto_original: str):
        if not texto_original or not texto_original.strip():
            return texto_original, "Vías Públicas"

        prompt = f"""
        Eres un asistente de IA encargado del triaje en la Mesa de Partes de la Municipalidad Provincial de Huancayo.

        Tu tarea es procesar el siguiente reclamo vecinal realizando dos acciones:

        1. ANONIMIZACIÓN: Reescribe el texto identificando y enmascarando cualquier dato personal:
           - Reemplaza nombres o apellidos de personas por [CIUDADANO_ANÓNIMO].
           - Reemplaza DNI o números de documento por [DNI_PROTEGIDO].
           - Reemplaza teléfonos, correos o referencias exactas de domicilio personal por [DATOS_PROTEGIDOS].
           - Conserva intacta la explicación del problema vecinal.

        2. CLASIFICACIÓN: Asigna el reclamo a EXACTAMENTE UNA de las siguientes 4 categorías oficiales:
           - Vías Públicas
           - Limpieza Pública
           - Parques y Jardines
           - Alumbrado

        Texto original a procesar:
        "{texto_original}"

        RESPONDE ÚNICAMENTE EN FORMATO JSON ESTRICTO (sin bloques markdown tipo ```json):
        {{"texto_anonimizado": "texto procesado aquí", "categoria": "Nombre de la Categoría"}}
        """

        for modelo in self.modelos:
            try:
                response = self.client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )

                json_text = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(json_text)

                texto_anonimizado = data.get("texto_anonimizado") or texto_original
                categoria = data.get("categoria", "Vías Públicas")

                if categoria not in CATEGORIAS_VALIDAS:
                    for cat in CATEGORIAS_VALIDAS:
                        if cat.lower() in categoria.lower():
                            categoria = cat
                            break
                    else:
                        categoria = "Vías Públicas"

                # Segunda capa: por si la IA dejó algún DNI, teléfono o correo sin enmascarar
                return self._anonimizar_local(texto_anonimizado), categoria

            except Exception as e:
                print(f"⚠️ Error al procesar reclamo con Gemini API ({modelo}): {e}", flush=True)

        # Ningún modelo respondió: nunca se guardan datos personales sin proteger
        print("⚠️ Gemini no disponible. Se aplica anonimización y clasificación local.", flush=True)
        return self._anonimizar_local(texto_original), self._clasificar_local(texto_original)

    @staticmethod
    def _anonimizar_local(texto: str) -> str:
        nombre = r"[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ]+)*"
        texto = re.sub(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", "[DATOS_PROTEGIDOS]", texto)
        texto = re.sub(r"(?<!\d)(?:\+?51\s?)?9\d{2}[\s-]?\d{3}[\s-]?\d{3}(?!\d)", "[DATOS_PROTEGIDOS]", texto)
        texto = re.sub(r"(?<!\d)\d{8}(?!\d)", "[DNI_PROTEGIDO]", texto)
        texto = re.sub(rf"(?i:\b(soy|me llamo|mi nombre es)\s+){nombre}", r"\1 [CIUDADANO_ANÓNIMO]", texto)
        # La dirección llega hasta la coma o el punto, sin cortar en abreviaturas como "Jr." o "Av."
        direccion = r"(?:(?i:\b(?:jr|av|ca|psje|pje|mz|lt|nro|urb)\.)\s*|[^.,;\n])+"
        texto = re.sub(rf"(?i:\b(domiciliad[oa] en|vivo en|mi casa (?:queda |está |esta )?en)\s+){direccion}",
                       r"\1 [DATOS_PROTEGIDOS]", texto)
        return texto

    @staticmethod
    def _clasificar_local(texto: str) -> str:
        # Gana la categoría con más palabras clave encontradas
        texto = texto.lower()
        puntajes = {cat: sum(p in texto for p in palabras) for cat, palabras in PALABRAS_CLAVE.items()}
        mejor = max(puntajes, key=puntajes.get)
        return mejor if puntajes[mejor] > 0 else "Vías Públicas"
