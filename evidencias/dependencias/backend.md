# Dependencias del backend

> Fase 2 · Prompt 3 – Dependencias. Archivos analizados: `backend/requirements.txt`, `backend/requirements-dev.txt`, `backend/package.json`, `backend/package-lock.json`.

## 1. Inventario completo

### Python (`requirements.txt`, producción)

| Paquete | Rango declarado | Función en el sistema | Categoría |
|---|---|---|---|
| fastapi | `>=0.115.0,<1.0` | Framework de la API REST | API |
| uvicorn | `>=0.30.0,<1.0` | Servidor ASGI que ejecuta FastAPI en Render | API |
| pydantic | `>=2.9.0,<3.0` | Validación de entradas (DTO con longitudes máximas) | API · Seguridad |
| python-dotenv | `>=1.0.0,<2.0` | Carga de variables desde `.env` en local | Configuración |
| supabase | `>=2.10.0,<3.0` | Cliente de PostgreSQL y verificación de tokens de Supabase Auth | Persistencia · Seguridad |
| google-genai | `>=1.50.0,<3.0` | SDK de la API de Gemini | IA · API externa |
| codecarbon | `>=3.0.0,<4.0` | Medición de energía (kWh) y emisiones (gCO₂e) | Telemetría |
| mlflow | `>=3.0.0,<4.0` | Registro de parámetros y métricas por inferencia | MLOps |
| dagshub | `>=0.5.0,<1.0` | Autenticación y servidor MLflow remoto | MLOps · API externa |
| requests | `>=2.32.0,<3.0` | Declarada, pero no se importa en el código del proyecto | HTTP (sin uso directo) |

### Python (`requirements-dev.txt`, desarrollo)

| Paquete | Rango | Uso |
|---|---|---|
| (incluye `requirements.txt`) | `-r requirements.txt` | Mismo entorno que producción |
| pytest | `>=8.0,<10.0` | Pruebas automatizadas (`backend/tests/`) |
| pip-audit | sin versión (se instala en el CI) | Auditoría de vulnerabilidades en GitHub Actions |

### Node.js (`backend/package.json`) — **sin uso**

| Paquete | Versión resuelta (lock) | Observación |
|---|---|---|
| express | 5.2.1 | No existe ningún archivo `.js` en `backend/` |
| pg | 8.23.0 | Ídem |
| @supabase/supabase-js | 2.117.1 | Ídem |
| cors | 2.8.6 | Ídem |
| dotenv | 18.0.0 | Ídem |
| nodemon (desarrollo) | — | Ídem |

El `package-lock.json` resuelve 121 paquetes que no se usan; es un resto de una versión anterior del backend.

## 2. Dependencias de producción

`fastapi`, `uvicorn`, `pydantic`, `python-dotenv`, `supabase`, `google-genai`, `codecarbon`, `mlflow`, `dagshub` (y `requests` sin uso directo).

## 3. Dependencias de desarrollo

`pytest` y `pip-audit` (este último solo en el CI).

## 4. Dependencias críticas

| Paquete | Motivo |
|---|---|
| fastapi / uvicorn | Sin ellas la API no arranca |
| supabase | Persistencia, autenticación del SIGEM y verificación de tokens |
| google-genai | Clasificación y anonimización con IA (hay respaldo local si falla la API, pero con confianza ≤ 50 %) |
| pydantic | Primera barrera de validación de entradas |

`mlflow`, `dagshub` y `codecarbon` son importantes para el objetivo Green AI, pero el sistema tolera su falla: `main.py` captura el error de DagsHub y el caso de uso guarda el reclamo aunque MLflow falle.

## 5. Dependencias obsoletas

En su primera revisión (19/11/2026), Dependabot abrió pull requests para subir el mínimo de:

| Paquete | Mínimo actual | Mínimo propuesto |
|---|---|---|
| codecarbon | 3.0.0 | 3.3.2 |
| pydantic | 2.9.0 | 2.14.3 |
| python-dotenv | 1.0.0 | 1.2.4 |
| requests | 2.32.0 | 2.34.2 |
| uvicorn | 0.30.0 | 0.54.0 |

Ninguna está fuera de soporte, pero los mínimos declarados son antiguos.

## 6. Vulnerabilidades potenciales

- **Sin archivo de bloqueo (lock) en Python:** se usan rangos, por lo que cada despliegue puede instalar versiones distintas. El CI ejecuta `pip-audit -r requirements.txt` y bloquea si hay vulnerabilidades conocidas; en la última ejecución sobre `main` no se reportaron.
- **Superficie innecesaria:** el `package.json` de Node incluye `express` y `pg` sin uso; aunque no se ejecutan, Dependabot y los escáneres los seguirán reportando.
- **`requests`** declarada sin uso directo: aumenta la superficie sin aportar funcionalidad propia.

## 7. Dependencias relacionadas con seguridad

`pydantic` (validación), `supabase` (verificación de JWT con `auth.get_user`), `fastapi.security.HTTPBearer` (esquema de autenticación) y `pip-audit` (auditoría). Los controles de límite de solicitudes, CORS y cabeceras son código propio (`infrastructure/security/`), sin librerías adicionales.

## 8. Dependencias relacionadas con persistencia

`supabase` (PostgreSQL vía PostgREST). La paquetería `pg` del `package.json` no se usa.

## 9. Dependencias relacionadas con APIs

- **API propia:** `fastapi`, `uvicorn`, `pydantic`.
- **APIs consumidas:** `google-genai` (Gemini), `supabase` (REST y Auth), `dagshub`/`mlflow` (servidor MLflow).
