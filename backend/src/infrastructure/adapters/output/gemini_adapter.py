import os
import json
import google.generativeai as genai


class GeminiAdapter:
    def __init__(self):
        # 1. Obtener la API Key desde las variables de entorno de Render
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("⚠️ GEMINI_API_KEY no está configurada en el entorno.")
        
        genai.configure(api_key=api_key)
        # Usamos el modelo 1.5 Flash por su alta velocidad y costo $0.00 USD
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def procesar_reclamo_con_ia(self, texto_original: str):
        """
        Delega a la IA de Gemini:
        1. La anonimización de nombres, DNI, direcciones o teléfonos.
        2. La clasificación automática en una categoría oficial municipal.
        """
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
            response = self.model.generate_content(prompt)
            
            # Limpiar posibles delimitadores de formato markdown que devuelva el modelo
            json_text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(json_text)

            texto_anonimizado = data.get("texto_anonimizado", texto_original)
            categoria = data.get("categoria", "Vías Públicas")

            # Validar que la categoría sea una de las 4 permitidas
            categorias_validas = ["Vías Públicas", "Limpieza Pública", "Parques y Jardines", "Alumbrado"]
            if categoria not in categorias_validas:
                # Fallback por coincidencia parcial si Gemini varía el texto
                for cat in categorias_validas:
                    if cat.lower() in categoria.lower():
                        categoria = cat
                        break
                else:
                    categoria = "Vías Públicas"

            return texto_anonimizado, categoria

        except Exception as e:
            print(f"⚠️ Error al procesar reclamo con Gemini API: {e}")
            # Retorno de emergencia si la API presenta interrupciones
            return texto_original, "Vías Públicas"