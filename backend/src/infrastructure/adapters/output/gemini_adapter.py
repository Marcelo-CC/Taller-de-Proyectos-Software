import os
import json
from google import genai
from google.genai import types

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
        # gemini-1.5-flash fue retirado; el alias "latest" apunta siempre al Flash vigente
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

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

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            json_text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(json_text)

            texto_anonimizado = data.get("texto_anonimizado", texto_original)
            categoria = data.get("categoria", "Vías Públicas")

            categorias_validas = ["Vías Públicas", "Limpieza Pública", "Parques y Jardines", "Alumbrado"]
            if categoria not in categorias_validas:
                for cat in categorias_validas:
                    if cat.lower() in categoria.lower():
                        categoria = cat
                        break
                else:
                    categoria = "Vías Públicas"

            return texto_anonimizado, categoria

        except Exception as e:
            print(f"⚠️ Error al procesar reclamo con Gemini API: {e}")
            return texto_original, "Vías Públicas"