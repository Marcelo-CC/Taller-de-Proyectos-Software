# 02 · Plan de mejora FURPS+ — Green AI Municipal

| Dato | Valor |
|---|---|
| Entrada | `docs/01_auditoria_furps.md` |
| Rol | Agente 2 — Planificador FURPS+ (Arquitecto de Software Senior) |
| Restricción principal | El sistema ya funciona y está en producción: ninguna mejora puede romper lo existente |
| Rama de trabajo | `mejoras-semana13` (no se toca `main` hasta validar) |

## 1. Principios aplicados

- **Compatibilidad hacia atrás:** no cambian las rutas de la API, los campos de la respuesta ni el esquema de la base de datos.
- **Cambios incrementales:** cada mejora es pequeña, independiente y se puede revertir sola.
- **Riesgo mínimo:** no se reescribe la lógica de negocio; se agregan pruebas, validaciones y protecciones alrededor de ella.
- **Validación obligatoria:** cada mejora tiene una prueba automatizada o una verificación manual definida.
- **Rollback:** todo vive en una rama aparte; revertir es `git revert <commit>` o volver a desplegar `main`.

## 2. Mejoras priorizadas

### M1 · Pruebas automatizadas del dominio y de los casos de uso — Prioridad **Crítica**

| Campo | Detalle |
|---|---|
| Objetivo | Cubrir con `pytest` la anonimización, la confianza HITL, el código secreto, la clasificación local, el registro de reclamos y el cambio de estado |
| Justificación | Brecha S-02: 0 pruebas. La anonimización (Ley 29733) y la regla HITL son críticas y hoy pueden romperse sin aviso |
| Riesgo | Muy bajo: solo se agregan archivos en `backend/tests/`; no se modifica código de producción |
| Dependencias | Ninguna (se usan dobles de prueba para Gemini, Supabase, CodeCarbon y MLflow) |
| Validación | `pytest` en verde; las pruebas deben pasar sin conexión a internet ni credenciales |
| Rollback | Borrar `backend/tests/` y `requirements-dev.txt` |

### M2 · Validación de entradas en el servidor — Prioridad **Alta**

| Campo | Detalle |
|---|---|
| Objetivo | Límites de longitud en `ReclamoDTO` y `EstadoDTO`, iguales o más amplios que los del formulario (título 200, descripción 2000, etc.) |
| Justificación | Brecha R-05: el servidor acepta textos de cualquier tamaño |
| Riesgo | Bajo: los límites son más amplios que los del frontend (120 y 1500), así que ningún uso legítimo cambia |
| Dependencias | M1 (pruebas de los DTO) |
| Validación | Pruebas: un reclamo normal se acepta y uno de 5000 caracteres se rechaza con 422 |
| Rollback | Revertir `dtos.py` a campos sin límite |

### M3 · Manejo de errores estandarizado con registro — Prioridad **Alta**

| Campo | Detalle |
|---|---|
| Objetivo | Responder al cliente un mensaje genérico con un código de incidente, y registrar el detalle técnico con `logging` en el servidor |
| Justificación | Brechas U-05 y R-04 |
| Riesgo | Bajo: el código HTTP (500) y el campo `detail` se mantienen; solo cambia el texto |
| Dependencias | Ninguna |
| Validación | Prueba de la función de error; revisión del log en Render |
| Rollback | Revertir `api_router.py` |

### M4 · Arranque tolerante a fallos de DagsHub — Prioridad **Alta**

| Campo | Detalle |
|---|---|
| Objetivo | Si DagsHub/MLflow no responde o no hay token, la API arranca igual y solo se deja de registrar en MLflow |
| Justificación | Brecha R-03 |
| Riesgo | Bajo: con DagsHub disponible el comportamiento es idéntico |
| Dependencias | Ninguna |
| Validación | Arranque local sin `MLFLOW_TRACKING_PASSWORD`; en Render, revisar que `/` responda |
| Rollback | Revertir `main.py` |

### M5 · Documentación y configuración — Prioridad **Media**

| Campo | Detalle |
|---|---|
| Objetivo | README actualizado (modelo real, cómo ejecutar, cómo probar, variables de entorno) y `backend/.env.example` |
| Justificación | Brechas S-03 y S-04 |
| Riesgo | Nulo (solo documentación) |
| Dependencias | M1 a M4 (para documentar el estado final) |
| Validación | Revisión del README y de que `.env.example` liste todas las variables que lee el código |
| Rollback | Revertir los archivos de documentación |

### M6 · Higiene del repositorio — Prioridad **Media**

| Campo | Detalle |
|---|---|
| Objetivo | Excluir de Git `mlflow.db`, `emissions.csv`, `mlruns/` y cachés de pruebas |
| Justificación | Brecha S-05 |
| Riesgo | Bajo: los archivos se dejan de versionar (`git rm --cached`) pero no se borran del disco; ningún código los lee |
| Dependencias | Ninguna |
| Validación | `git ls-files` ya no los lista; la app sigue funcionando |
| Rollback | `git add -f` de los archivos |

### M7 · Separar los DTO del adaptador FastAPI — Prioridad **Media**

| Campo | Detalle |
|---|---|
| Objetivo | Mover `ReclamoDTO` y `EstadoDTO` a `dtos.py` (solo Pydantic) para poder probarlos sin levantar el servidor |
| Justificación | Riesgo S-07 |
| Riesgo | Muy bajo: los nombres y campos no cambian; `api_router.py` los importa |
| Dependencias | M2 |
| Validación | Las pruebas de M2 importan `dtos.py` directamente |
| Rollback | Volver a definir las clases en `api_router.py` |

### Mejoras planificadas fuera de esta iteración — Prioridad **Baja**

| Mejora | Motivo para posponer |
|---|---|
| Paginación de `GET /api/reclamos` (P-02) | El SIGEM lee directo de Supabase por lotes de 1000; cambiar el contrato del endpoint exige coordinar frontend y backend |
| Exportación de reportes PDF/CSV (F-06) | Es una funcionalidad nueva, no una corrección; queda en el Product Backlog |
| Retirar `axios` y `backend/package.json` (S-06) | Requiere regenerar `package-lock.json` con `npm install`; se hará en un equipo con conexión y se validará con `npm run build` |
| Reutilizar el `EmissionsTracker` (P-03) | Afecta la medición de energía; necesita una comparación de mediciones antes de cambiarlo |

## 3. Roadmap y orden recomendado

| Paso | Mejora | Por qué en este orden |
|---|---|---|
| 1 | M1 Pruebas | Red de seguridad: permite comprobar que lo siguiente no rompe nada |
| 2 | M7 DTO separados | Prepara el terreno para probar M2 |
| 3 | M2 Validación de entradas | Se valida con las pruebas del paso 1 |
| 4 | M3 Manejo de errores | Cambio local en el adaptador de entrada |
| 5 | M4 Arranque tolerante | Cambio local en `main.py` |
| 6 | M6 Higiene del repositorio | No afecta la ejecución |
| 7 | M5 Documentación | Documenta el estado final |

## 4. Riesgos de ejecución

| Riesgo | Mitigación |
|---|---|
| Las pruebas dependen de servicios externos y fallan sin internet | Dobles de prueba para Gemini, Supabase, CodeCarbon y MLflow |
| Los límites de M2 rechazan reclamos legítimos | Límites más amplios que los del formulario y verificados con pruebas |
| Cambiar `main.py` impide el despliegue en Render | Se prueba en la rama; Render sigue desplegando `main` hasta que se apruebe el merge |
| Dejar de versionar `mlflow.db` borra datos | `git rm --cached` conserva el archivo local; los experimentos reales están en DagsHub |

## 5. Estrategia de preservación de funcionalidad

1. Todo el trabajo se hace en la rama `mejoras-semana13`; producción sigue con `main`.
2. Antes de unir la rama, se ejecutan las pruebas (`pytest`) y la verificación manual: registrar un reclamo de prueba, consultarlo con su código y cambiar su estado en el SIGEM.
3. Ningún endpoint cambia de ruta, método ni formato de respuesta exitosa.
4. Si algo falla tras el despliegue, se revierte el commit y Render/Vercel vuelven a desplegar la versión anterior en minutos.
