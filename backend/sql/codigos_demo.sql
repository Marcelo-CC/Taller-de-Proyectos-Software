-- =====================================================================
-- Códigos secretos para los reclamos SIMULADOS (solo para pruebas y demo)
-- Ejecutar en Supabase → SQL Editor, después de modulo_c_consulta.sql
--
-- Da un código al azar a cada reclamo que aún no tiene uno, guarda solo su hash
-- y muestra la lista ticket → código UNA sola vez (descárguela con "Export → CSV").
-- No lo use con reclamos reales: el código de un vecino solo debe verlo ese vecino.
-- =====================================================================

WITH nuevos AS (
  SELECT r.id,
         string_agg(substr('23456789ABCDEFGHJKMNPQRSTVWXYZ', floor(random() * 30)::int + 1, 1), '') AS codigo
  FROM reclamos r
  CROSS JOIN generate_series(1, 8)
  WHERE r.codigo_hash IS NULL
  GROUP BY r.id
),
actualizados AS (
  UPDATE reclamos r
  SET codigo_hash = encode(sha256(convert_to(n.codigo, 'UTF8')), 'hex')  -- mismo hash que el backend
  FROM nuevos n
  WHERE r.id = n.id
  RETURNING r.id, n.codigo
)
SELECT id AS ticket,
       substr(codigo, 1, 4) || '-' || substr(codigo, 5, 4) AS codigo_secreto
FROM actualizados
ORDER BY id;
