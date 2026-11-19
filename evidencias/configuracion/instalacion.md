# Reconstrucción del entorno e instalación

> Fase 3 · Prompt 4 – Reconstrucción del Entorno (rol: Ingeniero DevOps). Reconstruido a partir de `requirements*.txt`, `package.json`, `.env.example`, `calidad-seguridad.yml`, `vercel.json` y los scripts de `backend/sql/`. Comandos para **Linux Ubuntu 22.04 o 24.04**.

## 1. Software requerido

| Software | Uso |
|---|---|
| Git | Clonar el repositorio |
| Python 3 con `venv` y `pip` | Backend FastAPI y pruebas |
| Node.js y npm | Frontend React/Vite |
| Navegador web | Probar el portal y el SIGEM |

## 2. Versiones recomendadas

| Componente | Versión | Fuente |
|---|---|---|
| Python | 3.11 | Versión usada en GitHub Actions |
| Node.js | 22 LTS | Versión usada en GitHub Actions |
| npm | 10 o superior | Incluido con Node 22 |
| FastAPI / Uvicorn / Pydantic | según `requirements.txt` (rangos `<1.0` y `<3.0`) | `backend/requirements.txt` |
| React / Vite | 19.3.1 / 8.3.5 | `frontend/package-lock.json` |

## 3. Servicios externos requeridos

Supabase (base de datos y autenticación), Google Gemini API (clave) y, de forma opcional, DagsHub (MLflow). El detalle está en `servicios.md`.

## 4. Bases de datos requeridas

Un proyecto de Supabase con la tabla `reclamos` y los scripts de `backend/sql/` aplicados (ver `servicios.md`).

## 5. Variables de entorno

Ver `variables_entorno.md`. Mínimo para ejecutar en local: `SUPABASE_URL`, `SUPABASE_KEY` y `GEMINI_API_KEY` en el backend; `VITE_SUPABASE_URL` y `VITE_SUPABASE_PUBLISHABLE_KEY` en el frontend.

## 6. Configuración necesaria

1. **Supabase:** crear el proyecto y la tabla `reclamos`; en *SQL Editor* ejecutar `modulo_c_consulta.sql`, `hitl_auditoria.sql` y `seguridad_permisos.sql`; en *Authentication → Users* crear al menos un operador.
2. **Gemini:** generar la clave en Google AI Studio.
3. **DagsHub (opcional):** crear un token de acceso para MLflow.

## 7. Procedimiento completo de instalación (Ubuntu)

### 7.1 Herramientas del sistema

```bash
sudo apt update
sudo apt install -y git curl python3 python3-venv python3-pip
# Node.js 22 LTS desde NodeSource
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
python3 --version && node --version && npm --version
```

> En Ubuntu 22.04 el Python del sistema es 3.10; el proyecto funciona, pero para igualar el CI se recomienda 3.11 (`sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt install -y python3.11 python3.11-venv`).

### 7.2 Código fuente

```bash
git clone https://github.com/Marcelo-CC/Taller-de-Proyectos-Software.git
cd Taller-de-Proyectos-Software
```

### 7.3 Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
cp .env.example .env
nano .env          # completar SUPABASE_URL, SUPABASE_KEY y GEMINI_API_KEY
pytest             # verificación: deben pasar todas las pruebas
uvicorn main:app --reload --port 8000
```

La API queda en `http://127.0.0.1:8000` y su documentación interactiva en `http://127.0.0.1:8000/docs`.

### 7.4 Frontend (en otra terminal)

```bash
cd Taller-de-Proyectos-Software/frontend
npm ci
cat > .env.local <<'EOF'
VITE_API_URL=http://127.0.0.1:8000
VITE_SUPABASE_URL=https://xxxxxxxx.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=sb_publishable_xxxxxxxx
EOF
npm run dev
```

La aplicación queda en `http://localhost:5173` (este origen ya está permitido en CORS por defecto).

### 7.5 Verificación

```bash
curl http://127.0.0.1:8000/                      # {"message": "API de Reclamos Vecinales activa…"}
curl -i http://127.0.0.1:8000/api/reclamos       # 401: exige sesión de personal municipal
npm run build                                    # dentro de frontend/: genera dist/ sin errores
```

### 7.6 Despliegue (referencia)

| Plataforma | Configuración |
|---|---|
| Render | Servicio web · raíz `backend` · build `pip install -r requirements.txt` · inicio `python -m uvicorn main:app --host 0.0.0.0 --port $PORT` · variables del backend |
| Vercel | Raíz `frontend` · framework Vite · build `npm run build` · salida `dist` · variables `VITE_*` |

## Observaciones

- El repositorio no incluye `Dockerfile` ni `docker-compose.yml`; un contenedor facilitaría reproducir el entorno en un solo comando.
- No hay script para crear la tabla `reclamos` desde cero; hay que crearla a mano antes de aplicar los scripts.
- `backend/package.json` no se usa: **no** ejecutar `npm install` dentro de `backend/`.
