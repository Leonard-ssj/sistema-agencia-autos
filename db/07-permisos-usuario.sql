
GRANT ALL ON SCHEMA public TO autos_user;
GRANT USAGE ON SCHEMA public TO autos_user;
GRANT CREATE ON SCHEMA public TO autos_user;

-- 2. Dar permisos sobre todas las tablas existentes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO autos_user;

-- 3. Dar permisos sobre todas las secuencias existentes
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO autos_user;

-- 4. Dar permisos sobre tablas y secuencias futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO autos_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO autos_user;

GRANT CREATE ON DATABASE agencia_autos TO autos_user;


-- Verificar permisos
SELECT 
    grantee, 
    privilege_type 
FROM information_schema.role_table_grants 
WHERE grantee = 'autos_user' 
LIMIT 10;


