import os
import re
import json
from google import genai
from google.genai import types

CATEGORIAS_VALIDAS = ["Vías Públicas", "Limpieza Pública", "Parques y Jardines", "Alumbrado"]

# Palabras clave para clasificar cuando Gemini no está disponible
PALABRAS_CLAVE = {
    "Limpieza Pública": ["basura", "desmonte", "residuo", "bolsas", "olor", "plaga", "limpieza", "recojo", "ratas",
                         "desagüe", "desague", "alcantarilla"],
    "Parques y Jardines": ["parque", "jardín", "jardin", "árbol", "arbol", "pasto", "áreas verdes", "areas verdes",
                           "riego"],
    "Alumbrado": ["alumbrado", "poste", "foco", "luz", "luminaria", "oscuro", "apagado"],
}


class GeminiAdapter:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("⚠️ GEMINI_API_KEY no está configurada en el entorno.")

        # Timeout de 20 s (en ms) y sin reintentos: si un modelo falla se pasa al siguiente
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=20_000,
                retry_options=types.HttpRetryOptions(attempts=1)
            )
        )
        # Primero el modelo lite: más rápido y con menor consumo energético (Green AI).
        # Si está saturado (503/504) se intenta con el Flash completo.
        self.modelos = [
            os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest"),
            os.getenv("GEMINI_MODEL_RESPALDO", "gemini-flash-latest"),
        ]

    def procesar_reclamo_con_ia(self, titulo: str, descripcion: str, ubicacion: str = ""):
        """Anonimiza, corrige y clasifica el reclamo en una sola llamada a Gemini.
        Los datos personales del formulario (DNI, nombre, domicilio, contacto) NO llegan aquí.
        Devuelve (titulo, ubicacion, descripcion, categoria, senales).
        `senales` alimenta la evaluación de confianza HITL:
          {"probabilidades": {categoría: p}, "problematicas": int, "clasificado_por_ia": bool}"""
        titulo = titulo or ""
        descripcion = descripcion or ""
        ubicacion = ubicacion or ""
        if not titulo.strip() and not descripcion.strip():
            return titulo, ubicacion, descripcion, "Vías Públicas", self._senales_local("")

        # DNI, teléfonos y correos escritos en el texto se enmascaran antes de salir hacia Google
        titulo = self._anonimizar_local(titulo)
        descripcion = self._anonimizar_local(descripcion)

        prompt = f"""
        Eres un asistente de IA encargado del triaje en la Mesa de Partes de la Municipalidad Provincial de Huancayo.

        Tu tarea es procesar el siguiente reclamo vecinal realizando tres acciones:

        1. ANONIMIZACIÓN: En el título y la descripción, enmascara cualquier dato personal que aparezca:
           - Reemplaza nombres o apellidos de personas por [CIUDADANO_ANÓNIMO].
           - Reemplaza DNI o números de documento por [DNI_PROTEGIDO].
           - Reemplaza teléfonos, correos o referencias exactas de domicilio personal por [DATOS_PROTEGIDOS].
           - Conserva los marcadores que ya vengan entre corchetes.
           - La "ubicacion" es el lugar público del problema (calle, esquina, parque): NO la enmascares.

        2. CORRECCIÓN DE REDACCIÓN: Corrige la ortografía, tildes, puntuación y gramática del título,
           la ubicación y la descripción.
           - Mantén la persona gramatical original (si el vecino escribe en primera persona, se queda así).
           - NO cambies el significado, NO agregues hechos nuevos y NO elimines detalles del problema
             (lugares, calles, fechas, duración, etc.).
           - Los nombres de calles y avenidas se conservan, solo corrige su escritura (ej. "jr wayra" -> "Jr. Wayra").

        3. CLASIFICACIÓN: Asigna el reclamo a EXACTAMENTE UNA de las siguientes 4 categorías oficiales:
           - Vías Públicas
           - Limpieza Pública
           - Parques y Jardines
           - Alumbrado

        4. CONFIANZA DE LA CLASIFICACIÓN (sé calibrado y honesto, no optimista):
           - "probabilidades": probabilidad de que cada una de las 4 categorías sea la correcta (suman 1).
             Si el texto es vago o mezcla problemas de distintas categorías, reparte la probabilidad.
           - "problematicas": cuántos problemas distintos describe el vecino (número entero, mínimo 1).

        Reclamo a procesar:
        {json.dumps({"titulo": titulo, "ubicacion": ubicacion, "descripcion": descripcion}, ensure_ascii=False)}

        RESPONDE ÚNICAMENTE EN FORMATO JSON ESTRICTO (sin bloques markdown tipo ```json):
        {{"titulo": "...", "ubicacion": "...", "descripcion": "...", "categoria": "Nombre de la Categoría",
          "probabilidades": {{"Vías Públicas": 0.0, "Limpieza Pública": 0.0, "Parques y Jardines": 0.0, "Alumbrado": 0.0}},
          "problematicas": 1}}
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

                titulo_ia = data.get("titulo") or titulo
                ubicacion_ia = data.get("ubicacion") or ubicacion
                descripcion_ia = data.get("descripcion") or descripcion
                categoria = self._normalizar_categoria(data.get("categoria")) or "Vías Públicas"
                senales = {
                    "probabilidades": self._leer_probabilidades(data.get("probabilidades")),
                    "problematicas": self._leer_entero(data.get("problematicas")),
                    "clasificado_por_ia": True,
                }

                # Por si la IA dejó algún DNI, teléfono o correo sin enmascarar
                return (self._limpiar(titulo_ia), self._limpiar(ubicacion_ia),
                        self._limpiar(descripcion_ia), categoria, senales)

            except Exception as e:
                print(f"⚠️ Error al procesar reclamo con Gemini API ({modelo}): {e}", flush=True)

        # Ningún modelo respondió: nunca se guardan datos personales sin proteger
        print("⚠️ Gemini no disponible. Se aplica anonimización y clasificación local.", flush=True)
        texto = f"{titulo} {ubicacion} {descripcion}"
        return (self._limpiar(titulo), self._limpiar(ubicacion), self._limpiar(descripcion),
                self._clasificar_local(texto), self._senales_local(texto))

    @staticmethod
    def _normalizar_categoria(nombre) -> str:
        """Devuelve la categoría oficial que corresponde a `nombre`, o None si no coincide con ninguna."""
        nombre = str(nombre or "")
        if nombre in CATEGORIAS_VALIDAS:
            return nombre
        return next((cat for cat in CATEGORIAS_VALIDAS if cat.lower() in nombre.lower()), None)

    @classmethod
    def _leer_probabilidades(cls, crudas) -> dict:
        # Se ignoran claves desconocidas y valores no numéricos: sin señal válida la confianza baja
        probabilidades = {}
        if isinstance(crudas, dict):
            for nombre, valor in crudas.items():
                categoria = cls._normalizar_categoria(nombre)
                try:
                    if categoria:
                        probabilidades[categoria] = max(float(valor), 0.0)
                except (TypeError, ValueError):
                    pass
        return probabilidades

    @staticmethod
    def _leer_entero(valor) -> int:
        try:
            return max(1, int(valor))
        except (TypeError, ValueError):
            return 1

    @staticmethod
    def _senales_local(texto: str) -> dict:
        # Sin Gemini: la "probabilidad" es la proporción de palabras clave de cada categoría
        texto = texto.lower()
        puntajes = {cat: sum(p in texto for p in palabras) for cat, palabras in PALABRAS_CLAVE.items()}
        return {
            "probabilidades": {cat: float(n) for cat, n in puntajes.items() if n > 0},
            "problematicas": max(1, sum(1 for n in puntajes.values() if n > 0)),
            "clasificado_por_ia": False,
        }

    @classmethod
    def _limpiar(cls, texto: str) -> str:
        # Enmascarado local + mayúscula inicial
        texto = cls._anonimizar_local((texto or "").strip())
        return texto[:1].upper() + texto[1:]

    @staticmethod
    def _anonimizar_local(texto: str) -> str:
        nombre = r"[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑáéíóúñ]+)*"
        texto = re.sub(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", "[DATOS_PROTEGIDOS]", texto)
        texto = re.sub(r"(?<!\d)(?:\+?51\s?)?9\d{2}[\s-]?\d{3}[\s-]?\d{3}(?!\d)", "[DATOS_PROTEGIDOS]", texto)
        texto = re.sub(r"(?<!\d)\d{8}(?!\d)", "[DNI_PROTEGIDO]", texto)
        texto = re.sub(rf"(?i:\b(soy|me llamo|mi nombre es)\s+){nombre}", r"\1 [CIUDADANO_ANÓNIMO]", texto)
        texto = re.sub(r"(?i:\b(domiciliad[oa] en|vivo en|mi casa (?:queda |está |esta )?en)\s+)[^.,;\n]+",
                       r"\1 [DATOS_PROTEGIDOS]", texto)
        return texto

    @staticmethod
    def _clasificar_local(texto: str) -> str:
        # Gana la categoría con más palabras clave encontradas
        texto = texto.lower()
        puntajes = {cat: sum(p in texto for p in palabras) for cat, palabras in PALABRAS_CLAVE.items()}
        mejor = max(puntajes, key=puntajes.get)
        return mejor if puntajes[mejor] > 0 else "Vías Públicas"
