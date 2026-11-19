# Logs del frontend

> Fase 4 · Prompt 6 – Análisis de Logs. Fuentes: `npm run build` y `npm audit` en GitHub Actions, despliegue en Vercel y navegación de la aplicación en producción (`https://taller-de-proyectos-software.vercel.app`).

## 1. Build

```text
> vite build
✓ módulos transformados
dist/index.html
dist/assets/index-*.css
dist/assets/index-*.js
✓ built
```

El build termina sin errores en el CI y en Vercel. `npm audit --omit=dev --audit-level=high` no reporta vulnerabilidades altas ni críticas.

## 2. Ejecución en el navegador

| Vista (`#/…`) | Resultado observado |
|---|---|
| `inicio` | Carga correcta; accesos al Portal Ciudadano, Consulta, Guía y SIGEM |
| `ciudadano` | Formulario en pasos; al enviar muestra ticket, código secreto, categoría y botón "Imprimir constancia". Si Render está dormido, la primera solicitud tarda ~60 s |
| `consulta` | Ticket + código válido → estado del trámite; código incorrecto → mensaje genérico (no revela si el ticket existe) |
| `login` | Credenciales incorrectas → mensaje en español; correctas → SIGEM |
| `sigem` | Tabla paginada de 25 en 25, filtros, auditoría HITL, cambio de estado y Dashboard con exportación CSV/PDF |
| `guia` | Guía de uso de cada módulo |

## 3. Matriz de hallazgos

| ID | Hallazgo | Categoría | Severidad | Recomendación |
|---|---|---|---|---|
| FE-01 | Sin indicador de "servidor despertando": en el arranque en frío solo se ve el botón en espera | Red / experiencia | **Medio** | Mostrar un aviso tras 5 s de espera |
| FE-02 | La lectura del SIGEM va directo a Supabase y, si falla, cae al backend: dos rutas con permisos distintos para la misma operación | Configuración / arquitectura | **Medio** | Unificar en una sola ruta (preferentemente la API) |
| FE-03 | Recursos sin uso en el bundle o en `public/` (`hero.png`, `react.svg`, `vite.svg`, `icons.svg`, `favicon.svg`) | Mantenibilidad | **Bajo** | Eliminarlos |
| FE-04 | `axios` declarado y no usado | Dependencias | **Bajo** | Quitarlo de `package.json` |
| FE-05 | El token de sesión vive en memoria: al recargar la página el operador debe volver a ingresar | Autenticación | **Bajo** (decisión de seguridad aceptable) | Documentarlo en la guía |
