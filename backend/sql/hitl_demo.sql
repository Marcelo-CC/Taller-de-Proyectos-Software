-- =====================================================================
-- Confianza simulada para los reclamos de PRUEBA (solo demo)
-- Ejecutar después de hitl_auditoria.sql. Solo toca reclamos sin confianza (confianza IS NULL).
--
-- Reparte la confianza entre 45 % y 99 %. Los que quedan por debajo del 70 % y siguen
-- PENDIENTES pasan a "Pendiente de auditoría HITL"; los que ya están en proceso o resueltos
-- se consideran auditados antes.
-- =====================================================================

UPDATE reclamos r
SET confianza = s.valor,
    requiere_auditoria = (s.valor < 0.70 AND r.estado = 'PENDIENTE')
FROM (
  SELECT id, round((0.45 + random() * 0.54)::numeric, 4)::double precision AS valor
  FROM reclamos
  WHERE confianza IS NULL
) AS s
WHERE r.id = s.id;

-- Comprobación
SELECT requiere_auditoria, estado, count(*) FROM reclamos GROUP BY 1, 2 ORDER BY 1, 2;
