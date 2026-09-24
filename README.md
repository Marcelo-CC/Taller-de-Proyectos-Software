# Sistema de Gestión de Reclamos - Municipalidad Provincial de Huancayo

Proyecto correspondiente a la **Unidad II (S6)** para la Municipalidad Provincial de Huancayo. La solución implementa un prototipo funcional (PMV) con arquitectura desacoplada, persistencia en la nube e integración con Inteligencia Artificial para el procesamiento de reclamos y telemetría de consumo energético.

---

## 🏗️ Arquitectura del Sistema

El proyecto está estructurado bajo una **Arquitectura Hexagonal (Puertos y Adaptadores)** para garantizar la separación de responsabilidades, mantenibilidad y escalabilidad del código.

```text
├── backend/
│   ├── src/
│   │   ├── application/       # Casos de uso y lógica de aplicación
│   │   ├── domain/            # Entidades de negocio y puertos
│   │   └── infrastructure/    # Adaptadores de entrada (Express/Server) y salida (Supabase)
│   └── package.json
├── frontend/                  # Interfaz de usuario construida en React + Vite
└── main.py                    # Integración de IA (Ollama) y telemetría de emisión (CodeCarbon)
