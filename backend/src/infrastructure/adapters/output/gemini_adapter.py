import os
import google.generativeai as genai

class GeminiAdapter:
    def __init__(self):
        # Toma la API Key desde la variable de entorno
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("⚠️ GEMINI_API_KEY no está configurada.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def clasificar_y_resumir(self, descripcion: str) -> str:
        prompt = f"""
        Eres un asistente de triaje de la Municipalidad Provincial de Huancayo.
        Analiza el siguiente reclamo vecinal y genera un resumen/clasificación de máximo 15 palabras.
        
        Reclamo: "{descripcion}"
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error al conectar con Gemini API: {e}")
            return "Resumen no disponible temporalmente."