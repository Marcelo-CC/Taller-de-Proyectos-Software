-- =====================================================================
-- Módulo HITL (Human-in-the-Loop): confianza de la IA y auditoría humana
-- Ejecutar una sola vez en Supabase → SQL Editor, ANTES de publicar el código nuevo
-- (el código nuevo lee estas columnas; el código anterior no las usa y sigue funcionando).
-- =====================================================================

-- 1. Columnas nuevas
--    confianza:          0.0–1.0, calculada por el backend al clasificar con la IA (NULL en reclamos antiguos)
--    requiere_auditoria: true = "Pendiente de auditoría HITL" (confianza < 70 %), retenido hasta revisión humana
ALTER TABLE reclamos ADD COLUMN IF NOT EXISTS confianza double precision
  CHECK (confianza IS NULL OR confianza BETWEEN 0 AND 1);
ALTER TABLE reclamos ADD COLUMN IF NOT EXISTS requiere_auditoria boolean NOT NULL DEFAULT false;

-- 2. Permisos por columna (la tabla usa permisos por columna desde el Módulo C)
GRANT SELECT (confianza, requiere_auditoria) ON reclamos TO anon, authenticated;
-- Solo el personal con sesión puede auditar: corregir la categoría y liberar el reclamo
GRANT UPDATE (categoria, requiere_auditoria) ON reclamos TO authenticated;

-- 3. Regla de negocio en la base: un reclamo retenido no cambia de estado sin auditoría.
--    Para cambiar su estado hay que liberarlo (requiere_auditoria = false) en la misma operación.
CREATE OR REPLACE FUNCTION proteger_auditoria_hitl()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  IF OLD.requiere_auditoria AND NEW.requiere_auditoria AND NEW.estado IS DISTINCT FROM OLD.estado THEN
    RAISE EXCEPTION 'El reclamo % está pendiente de auditoría HITL: confirme o corrija la categoría antes de cambiar su estado.', OLD.id;
  END IF;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_proteger_auditoria_hitl ON reclamos;
CREATE TRIGGER trg_proteger_auditoria_hitl
  BEFORE UPDATE ON reclamos
  FOR EACH ROW EXECUTE FUNCTION proteger_auditoria_hitl();
