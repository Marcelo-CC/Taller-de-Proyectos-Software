# Inventario funcional del sistema

> Fase 4 · Prompt 7 – Descubrimiento Funcional (evidencia guardada en `analisis/`). Fuente: aplicación en ejecución (Vercel + Render) y código de `frontend/src` y `backend/src`.

## 1. Módulos funcionales

| Módulo | Usuario | Vista / componente | Función |
|---|---|---|---|
| Inicio | Público | `pages/Inicio.jsx` | Portada con accesos a los demás módulos |
| A · Portal Ciudadano | Vecino | `pages/PortalCiudadano.jsx` | Registrar un reclamo; la IA corrige, anonimiza y clasifica |
| C · Consulta de trámite | Vecino | `pages/ConsultaTramite.jsx` | Ver el estado con número de ticket + código secreto |
| Acceso municipal | Personal | `pages/LoginMunicipal.jsx` | Inicio de sesión con Supabase Auth |
| B · SIGEM | Personal | `pages/Sigem.jsx`, `sigem/TablaReclamos.jsx`, `sigem/BusquedaFiltrado.jsx` | Bandeja de reclamos, filtros, cambio de estado y auditoría HITL |
| Dashboard Green AI | Personal | `sigem/DashboardGreenAI.jsx` | Energía (kWh), emisiones (gCO₂e), reclamos por categoría; exportación CSV y PDF; enlace a MLflow |
| Guía de usuario | Todos | `pages/GuiaUsuario.jsx` | Ayuda paso a paso de cada módulo |

## 2. Menús

Navegación por hash (`#/inicio`, `#/ciudadano`, `#/consulta`, `#/guia`, `#/login`, `#/sigem`) definida en `App.jsx` y la cabecera de `components/Layout.jsx`. El SIGEM solo se muestra con sesión; sin ella redirige al login. Dentro del SIGEM hay pestañas de bandeja y dashboard, y un botón de cierre de sesión.

## 3. Formularios

| Formulario | Campos | Validaciones |
|---|---|---|
| Registro de reclamo (en pasos) | Nombre, DNI, contacto, dirección · título (≤120), ubicación, descripción (≤1500) | Nombre solo letras; DNI 8 dígitos; campos obligatorios; límites también en el servidor (Pydantic) |
| Consulta de trámite | Número de ticket, código `XXXX-XXXX` | Formato del código; respuesta genérica si no coincide |
| Login municipal | Correo, contraseña | Supabase Auth |
| Búsqueda y filtrado (SIGEM) | Buscador de texto, botones de categoría y de estado | Filtrado en tiempo real en el cliente |
| Auditoría HITL | Selección de la categoría correcta | Solo para reclamos con `requiere_auditoria = true` |

## 4. Procesos de negocio

1. **Registro y clasificación:** el vecino envía el reclamo → se enmascaran sus datos personales → Gemini corrige, anonimiza y clasifica en una de 4 categorías → se calcula la confianza → se guarda con ticket y hash del código.
2. **Enrutamiento HITL:** confianza ≥ 0,70 → derivación directa; < 0,70 → queda "Pendiente de auditoría" hasta que un operador confirme o corrija la categoría, lo que lo pasa a `EN_PROCESO`.
3. **Gestión del trámite:** `PENDIENTE` → `EN_PROCESO` → `RESUELTO`.
4. **Consulta ciudadana:** ticket + código → función `consultar_reclamo` compara el hash y devuelve solo datos públicos.
5. **Medición Green AI:** cada inferencia se mide con CodeCarbon y se registra en MLflow; el dashboard agrega los totales.

## 5. APIs consumidas

Gemini API, Supabase (REST, RPC y Auth) y DagsHub/MLflow (ver `../ejecucion/endpoints_detectados.md`).

## 6. APIs expuestas

`GET /`, `POST /api/reclamos`, `GET /api/reclamos`, `PATCH /api/reclamos/{id}/estado`, `/docs` y `/openapi.json`. La función `consultar_reclamo` de Supabase actúa como API pública adicional.

## 7. Flujos principales

```text
Vecino ─► Portal Ciudadano ─► POST /api/reclamos ─► (enmascarar ─► Gemini ─► confianza ─► Supabase ─► MLflow)
       ◄─ ticket + código secreto ◄─────────────────┘

Vecino ─► Consulta ─► RPC consultar_reclamo(ticket, código) ─► estado del trámite

Operador ─► Login (Supabase Auth) ─► SIGEM ─► listar (Supabase REST / API)
                                         ├─► auditar categoría (PATCH con JWT)
                                         ├─► cambiar estado (PATCH con JWT)
                                         └─► Dashboard ─► CSV / PDF / MLflow
```
