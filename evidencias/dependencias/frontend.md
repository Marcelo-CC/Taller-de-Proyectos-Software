# Dependencias del frontend

> Fase 2 · Prompt 3 – Dependencias. Archivos analizados: `frontend/package.json` y `frontend/package-lock.json` (232 paquetes resueltos).

## 1. Inventario completo

| Paquete | Declarado | Resuelto (lock) | Tipo | Uso |
|---|---|---|---|---|
| react | ^19.2.8 | 19.3.1 | Producción | Interfaz de usuario |
| react-dom | ^19.2.8 | 19.3.1 | Producción | Renderizado en el navegador |
| recharts | ^3.10.1 | 3.10.1 | Producción | Gráficos del Dashboard Green AI |
| axios | ^1.20.0 | 1.21.0 | Producción | **Declarado, pero no se importa** (el código usa `fetch`) |
| vite | ^8.3.0 | 8.3.5 | Desarrollo | Servidor de desarrollo y build |
| @vitejs/plugin-react | ^6.1.1 | 6.1.2 | Desarrollo | Soporte de JSX en Vite |
| eslint | ^10.10.0 | 10.13.0 | Desarrollo | Análisis estático |
| @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, globals | varias | — | Desarrollo | Reglas de ESLint |
| @types/react, @types/react-dom | ^19 | — | Desarrollo | Tipos para el editor |

## 2. Dependencias de producción

`react`, `react-dom`, `recharts` y `axios` (sin uso).

## 3. Dependencias de desarrollo

`vite`, `@vitejs/plugin-react`, `eslint` y sus complementos, `@types/*`.

## 4. Dependencias críticas

`react` y `react-dom` (toda la interfaz) y `vite` (sin build no hay despliegue en Vercel).

## 5. Dependencias obsoletas

Dependabot agrupó las actualizaciones menores del frontend en un pull request (`menores-frontend`, 19/11/2026). No hay versiones mayores atrasadas: React 19, Vite 8 y ESLint 10 son las líneas actuales.

## 6. Vulnerabilidades potenciales

- El CI ejecuta `npm audit --omit=dev --audit-level=high` y bloquea si hay vulnerabilidades altas o críticas en producción; la última ejecución en `main` pasó.
- `axios` sin uso aumenta la superficie de ataque y la cantidad de alertas sin aportar funcionalidad.

## 7. Dependencias relacionadas con seguridad

No hay librerías de seguridad en el cliente. La autenticación se hace con `fetch` contra Supabase Auth y el token se guarda en memoria de la sesión (`App.jsx`). Las cabeceras de seguridad las aplica Vercel (`vercel.json`).

## 8. Dependencias relacionadas con persistencia

Ninguna librería: el frontend llama directamente a la API REST de Supabase con `fetch` (`services/api.js`).

## 9. Dependencias relacionadas con APIs

`fetch` nativo del navegador hacia la API propia (Render) y hacia Supabase (REST, RPC y Auth). `axios` está declarado pero no se usa.
