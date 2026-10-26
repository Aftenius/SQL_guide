CREATE ROLE sql_guide_sandbox LOGIN PASSWORD 'sql_guide_sandbox'
    NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
GRANT sql_guide_sandbox TO sql_guide;

CREATE DATABASE sql_guide_sandbox;

REVOKE CONNECT ON DATABASE sql_guide FROM PUBLIC;
GRANT CONNECT ON DATABASE sql_guide TO sql_guide;
REVOKE ALL ON DATABASE sql_guide_sandbox FROM PUBLIC;
GRANT CONNECT ON DATABASE sql_guide_sandbox TO sql_guide;
GRANT CONNECT ON DATABASE sql_guide_sandbox TO sql_guide_sandbox;

\connect sql_guide_sandbox
REVOKE ALL ON SCHEMA public FROM PUBLIC;
