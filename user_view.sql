CREATE USER user_view WITH PASSWORD 'tvoj_prosti_password';
GRANT USAGE ON SCHEMA dwh TO user_view;

-- Dajemo SELECT na sve tabele u schemi dwh
GRANT SELECT ON ALL TABLES IN SCHEMA dwh TO user_view;

-- Automatski SELECT na nove tabele u schemi
ALTER DEFAULT PRIVILEGES IN SCHEMA dwh
GRANT SELECT ON TABLES TO user_view;
