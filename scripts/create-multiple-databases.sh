#!/bin/bash
# Create multiple PostgreSQL databases for microservices architecture

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create separate database for payment service
    CREATE DATABASE smartcompute_payments;
    
    -- Create payment service user with limited privileges
    CREATE USER payment_user WITH ENCRYPTED PASSWORD '$PAYMENT_DB_PASSWORD';
    GRANT CONNECT ON DATABASE smartcompute_payments TO payment_user;
    GRANT USAGE ON SCHEMA public TO payment_user;
    GRANT CREATE ON SCHEMA public TO payment_user;
    
    -- Switch to payment database and set up permissions
    \c smartcompute_payments;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO payment_user;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO payment_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO payment_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO payment_user;
    
    -- Create monitoring database
    \c postgres;
    CREATE DATABASE smartcompute_monitoring;
    
    -- Create monitoring user
    CREATE USER monitoring_user WITH ENCRYPTED PASSWORD '$MONITORING_DB_PASSWORD';
    GRANT CONNECT ON DATABASE smartcompute_monitoring TO monitoring_user;
    
    \c smartcompute_monitoring;
    GRANT USAGE ON SCHEMA public TO monitoring_user;
    GRANT CREATE ON SCHEMA public TO monitoring_user;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO monitoring_user;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO monitoring_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO monitoring_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO monitoring_user;

EOSQL