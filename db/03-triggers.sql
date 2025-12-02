

-- Función para convertir registro a JSON (para auditoría)
CREATE OR REPLACE FUNCTION row_to_json_safe(record ANYELEMENT)
RETURNS JSONB AS $$
BEGIN
    RETURN to_jsonb(record);
EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger 1: Validar disponibilidad del vehículo
-- Valida disponibilidad antes de confirmar una venta

CREATE OR REPLACE FUNCTION fn_check_disponibilidad_vehiculo()
RETURNS TRIGGER AS $$
DECLARE
    v_estado VARCHAR(20);
    v_marca VARCHAR(50);
    v_modelo VARCHAR(50);
BEGIN
    -- Obtener el estado actual del vehículo
    SELECT v.estado_disponibilidad, m.nombre, v.modelo
    INTO v_estado, v_marca, v_modelo
    FROM vehiculo v
    INNER JOIN marca m ON v.marca_id = m.id
    WHERE v.id = NEW.vehiculo_id;
    
    -- Validar que el vehículo existe
    IF NOT FOUND THEN
        RAISE EXCEPTION 'El vehículo con ID % no existe', NEW.vehiculo_id;
    END IF;
    
    -- Validar que el vehículo esté disponible
    IF v_estado != 'DISPONIBLE' THEN
        RAISE EXCEPTION 'El vehículo % % (ID: %) no está disponible. Estado actual: %', 
            v_marca, v_modelo, NEW.vehiculo_id, v_estado;
    END IF;
    
    -- Si todo está bien, permitir la inserción
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear el trigger
DROP TRIGGER IF EXISTS trg_check_disponibilidad ON detalle_venta;
CREATE TRIGGER trg_check_disponibilidad
    BEFORE INSERT ON detalle_venta
    FOR EACH ROW
    EXECUTE FUNCTION fn_check_disponibilidad_vehiculo();

COMMENT ON FUNCTION fn_check_disponibilidad_vehiculo() IS 
'Valida que el vehículo esté DISPONIBLE antes de agregarlo a una venta';

-- Trigger 2: Actualizar estado del vehículo
-- Requisito: Actualización automática del estado del vehículo (Disponible, Vendido, Reservado)
-- Se ejecuta AFTER INSERT en detalle_venta

CREATE OR REPLACE FUNCTION fn_update_estado_vehiculo()
RETURNS TRIGGER AS $$
BEGIN
    -- Actualizar el estado del vehículo a VENDIDO
    UPDATE vehiculo
    SET estado_disponibilidad = 'VENDIDO',
        fecha_modificacion = CURRENT_TIMESTAMP
    WHERE id = NEW.vehiculo_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear el trigger
DROP TRIGGER IF EXISTS trg_update_estado_vehiculo ON detalle_venta;
CREATE TRIGGER trg_update_estado_vehiculo
    AFTER INSERT ON detalle_venta
    FOR EACH ROW
    EXECUTE FUNCTION fn_update_estado_vehiculo();

COMMENT ON FUNCTION fn_update_estado_vehiculo() IS 
'Actualiza automáticamente el estado del vehículo a VENDIDO después de agregarlo a una venta';

-- Trigger 3: Auditoría de ventas
-- Requisito: Registro de auditoría automática al modificar, cancelar o eliminar una venta
-- Se ejecuta AFTER INSERT, UPDATE, DELETE en venta

CREATE OR REPLACE FUNCTION fn_audit_ventas()
RETURNS TRIGGER AS $$
DECLARE
    v_accion VARCHAR(10);
    v_old_data JSONB;
    v_new_data JSONB;
    v_venta_id BIGINT;
BEGIN
    -- Determinar la acción
    IF TG_OP = 'INSERT' THEN
        v_accion := 'INSERT';
        v_old_data := NULL;
        v_new_data := to_jsonb(NEW);
        v_venta_id := NEW.id;
    ELSIF TG_OP = 'UPDATE' THEN
        v_accion := 'UPDATE';
        v_old_data := to_jsonb(OLD);
        v_new_data := to_jsonb(NEW);
        v_venta_id := NEW.id;
    ELSIF TG_OP = 'DELETE' THEN
        v_accion := 'DELETE';
        v_old_data := to_jsonb(OLD);
        v_new_data := NULL;
        v_venta_id := OLD.id;
    END IF;
    
    -- Insertar registro de auditoría
    INSERT INTO aud_ventas (
        venta_id,
        accion,
        usuario_bd,
        fecha_evento,
        old_data,
        new_data
    ) VALUES (
        v_venta_id,
        v_accion,
        CURRENT_USER,
        CURRENT_TIMESTAMP,
        v_old_data,
        v_new_data
    );
    
    -- Retornar el registro apropiado
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Crear el trigger
DROP TRIGGER IF EXISTS trg_audit_ventas ON venta;
CREATE TRIGGER trg_audit_ventas
    AFTER INSERT OR UPDATE OR DELETE ON venta
    FOR EACH ROW
    EXECUTE FUNCTION fn_audit_ventas();

COMMENT ON FUNCTION fn_audit_ventas() IS 
'Registra automáticamente todos los cambios (INSERT/UPDATE/DELETE) en la tabla venta';

-- Trigger 4: Auditoría de vehículos
-- Requisito: Registro de auditoría automática en tabla separada (NO UNA SOLA TABLA)
-- Se ejecuta AFTER INSERT, UPDATE, DELETE en vehiculo

CREATE OR REPLACE FUNCTION fn_audit_vehiculos()
RETURNS TRIGGER AS $$
DECLARE
    v_accion VARCHAR(10);
    v_old_data JSONB;
    v_new_data JSONB;
    v_vehiculo_id BIGINT;
BEGIN
    -- Determinar la acción
    IF TG_OP = 'INSERT' THEN
        v_accion := 'INSERT';
        v_old_data := NULL;
        v_new_data := to_jsonb(NEW);
        v_vehiculo_id := NEW.id;
    ELSIF TG_OP = 'UPDATE' THEN
        v_accion := 'UPDATE';
        v_old_data := to_jsonb(OLD);
        v_new_data := to_jsonb(NEW);
        v_vehiculo_id := NEW.id;
    ELSIF TG_OP = 'DELETE' THEN
        v_accion := 'DELETE';
        v_old_data := to_jsonb(OLD);
        v_new_data := NULL;
        v_vehiculo_id := OLD.id;
    END IF;
    
    -- Insertar registro de auditoría
    INSERT INTO aud_vehiculos (
        vehiculo_id,
        accion,
        usuario_bd,
        fecha_evento,
        old_data,
        new_data
    ) VALUES (
        v_vehiculo_id,
        v_accion,
        CURRENT_USER,
        CURRENT_TIMESTAMP,
        v_old_data,
        v_new_data
    );
    
    -- Retornar el registro apropiado
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Crear el trigger
DROP TRIGGER IF EXISTS trg_audit_vehiculos ON vehiculo;
CREATE TRIGGER trg_audit_vehiculos
    AFTER INSERT OR UPDATE OR DELETE ON vehiculo
    FOR EACH ROW
    EXECUTE FUNCTION fn_audit_vehiculos();

COMMENT ON FUNCTION fn_audit_vehiculos() IS 
'Registra automáticamente todos los cambios (INSERT/UPDATE/DELETE) en la tabla vehiculo';

