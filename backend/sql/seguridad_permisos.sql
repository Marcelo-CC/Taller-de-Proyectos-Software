-- OWASP A01 (R7): el rol público (anon) ya no puede cambiar el estado de los reclamos.
-- El SIGEM siempre actualiza con el token del operador (rol authenticated), así que no se ve afectado.
--
-- ⚠️ CONDICIÓN: ejecutar SOLO si SUPABASE_KEY en Render es la clave service_role o secret.
--    Si el backend usara la clave pública (anon), perdería permisos. Verifíquelo en
--    Supabase → Project Settings → API Keys y compárelo con la variable de Render.

-- 1. Situación actual: qué roles pueden actualizar columnas de reclamos
SELECT grantee, column_name, privilege_type
FROM information_schema.column_privileges
WHERE table_name = 'reclamos' AND privilege_type = 'UPDATE'
ORDER BY grantee, column_name;

-- 2. Cambio
REVOKE UPDATE ON reclamos FROM anon;

-- 3. Verificación: ya no debe aparecer "anon" en la lista
SELECT grantee, column_name, privilege_type
FROM information_schema.column_privileges
WHERE table_name = 'reclamos' AND privilege_type = 'UPDATE'
ORDER BY grantee, column_name;

-- ROLLBACK (si algo dejara de funcionar):
-- GRANT UPDATE (estado) ON reclamos TO anon;
