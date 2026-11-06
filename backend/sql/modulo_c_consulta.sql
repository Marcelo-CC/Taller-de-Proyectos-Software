-- =====================================================================
-- Módulo C: Consulta de trámite con número de ticket + código secreto
-- Ejecutar una sola vez en Supabase → SQL Editor
-- =====================================================================

-- 1. Columna con el hash SHA-256 del código secreto (el código en texto plano nunca se guarda)
ALTER TABLE reclamos ADD COLUMN IF NOT EXISTS codigo_hash text;

-- 2. Nadie puede leer ni modificar el hash por la API pública.
--    Se quitan los permisos sobre toda la tabla y se devuelven solo sobre las columnas públicas.
REVOKE SELECT, UPDATE ON reclamos FROM anon, authenticated;
GRANT SELECT (id, created_at, titulo, descripcion, categoria, emisiones_gco2, consumo_kwh, estado)
  ON reclamos TO anon, authenticated;
GRANT UPDATE (estado) ON reclamos TO anon, authenticated;  -- las políticas RLS siguen decidiendo quién edita

-- 3. Consulta del vecino: devuelve el reclamo solo si el ticket y el código coinciden.
--    SECURITY DEFINER: compara el hash dentro de la base sin exponerlo nunca.
CREATE OR REPLACE FUNCTION consultar_reclamo(p_ticket bigint, p_codigo text)
RETURNS TABLE (id bigint, created_at timestamptz, titulo text, descripcion text, categoria text, estado text)
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT r.id::bigint, r.created_at::timestamptz, r.titulo::text, r.descripcion::text,
         r.categoria::text, r.estado::text
  FROM reclamos r
  WHERE r.id = p_ticket
    AND r.codigo_hash IS NOT NULL
    AND r.codigo_hash = encode(
          sha256(convert_to(upper(regexp_replace(coalesce(p_codigo, ''), '[^A-Za-z0-9]', '', 'g')), 'UTF8')),
          'hex');
$$;

REVOKE ALL ON FUNCTION consultar_reclamo(bigint, text) FROM public;
GRANT EXECUTE ON FUNCTION consultar_reclamo(bigint, text) TO anon, authenticated;
