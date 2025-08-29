#!/usr/bin/env python3
"""
SmartCompute PostgreSQL Migration Script
Migrates data from JSON/SQLite to PostgreSQL using Alembic
"""

import json
import sqlite3
import asyncio
import asyncpg
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataMigrator:
    """Handles migration from legacy storage to PostgreSQL"""
    
    def __init__(self):
        self.pg_url = os.getenv('DATABASE_URL', 'postgresql://smartcompute:password@localhost:5432/smartcompute')
        self.legacy_data_dir = Path('./data')
        self.sqlite_db = './smartcompute.db'
    
    async def connect_postgres(self):
        """Connect to PostgreSQL database"""
        try:
            self.pg_conn = await asyncpg.connect(self.pg_url)
            logger.info("Connected to PostgreSQL")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    async def create_tables(self):
        """Create PostgreSQL tables if they don't exist"""
        schema_sql = """
        -- Analysis Results Table
        CREATE TABLE IF NOT EXISTS analysis_results (
            id SERIAL PRIMARY KEY,
            request_id VARCHAR(255) UNIQUE NOT NULL,
            analysis_type VARCHAR(100) NOT NULL,
            status VARCHAR(50) NOT NULL,
            result JSONB NOT NULL,
            processing_time_ms FLOAT NOT NULL,
            confidence FLOAT DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- System Metrics Table
        CREATE TABLE IF NOT EXISTS system_metrics (
            id SERIAL PRIMARY KEY,
            metric_type VARCHAR(100) NOT NULL,
            metric_name VARCHAR(255) NOT NULL,
            value FLOAT NOT NULL,
            unit VARCHAR(50),
            labels JSONB DEFAULT '{}',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Performance Baselines Table
        CREATE TABLE IF NOT EXISTS performance_baselines (
            id SERIAL PRIMARY KEY,
            system_id VARCHAR(255) NOT NULL,
            baseline_type VARCHAR(100) NOT NULL,
            baseline_data JSONB NOT NULL,
            established_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT true
        );
        
        -- User Sessions Table
        CREATE TABLE IF NOT EXISTS user_sessions (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) UNIQUE NOT NULL,
            user_id VARCHAR(255),
            api_key_hash VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT true
        );
        
        -- API Usage Logs Table
        CREATE TABLE IF NOT EXISTS api_usage (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255),
            endpoint VARCHAR(255) NOT NULL,
            method VARCHAR(10) NOT NULL,
            response_code INTEGER NOT NULL,
            processing_time_ms FLOAT,
            request_size_bytes INTEGER,
            response_size_bytes INTEGER,
            ip_address INET,
            user_agent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_analysis_results_request_id ON analysis_results(request_id);
        CREATE INDEX IF NOT EXISTS idx_analysis_results_type ON analysis_results(analysis_type);
        CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at ON analysis_results(created_at);
        
        CREATE INDEX IF NOT EXISTS idx_system_metrics_type ON system_metrics(metric_type);
        CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp);
        
        CREATE INDEX IF NOT EXISTS idx_performance_baselines_system ON performance_baselines(system_id);
        CREATE INDEX IF NOT EXISTS idx_performance_baselines_type ON performance_baselines(baseline_type);
        
        CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
        CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(is_active);
        
        CREATE INDEX IF NOT EXISTS idx_api_usage_endpoint ON api_usage(endpoint);
        CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp ON api_usage(timestamp);
        """
        
        await self.pg_conn.execute(schema_sql)
        logger.info("PostgreSQL tables created/verified")
    
    async def migrate_json_files(self):
        """Migrate data from JSON files"""
        if not self.legacy_data_dir.exists():
            logger.warning(f"Legacy data directory {self.legacy_data_dir} not found")
            return
        
        # Migrate history files
        history_files = list(self.legacy_data_dir.glob('*_history.json'))
        for history_file in history_files:
            try:
                with open(history_file, 'r') as f:
                    history_data = json.load(f)
                
                await self.migrate_history_data(history_data, history_file.stem)
                logger.info(f"Migrated {history_file}")
                
            except Exception as e:
                logger.error(f"Failed to migrate {history_file}: {e}")
        
        # Migrate baseline files
        baseline_files = list(self.legacy_data_dir.glob('*_baseline.json'))
        for baseline_file in baseline_files:
            try:
                with open(baseline_file, 'r') as f:
                    baseline_data = json.load(f)
                
                await self.migrate_baseline_data(baseline_data, baseline_file.stem)
                logger.info(f"Migrated {baseline_file}")
                
            except Exception as e:
                logger.error(f"Failed to migrate {baseline_file}: {e}")
    
    async def migrate_history_data(self, history_data: List[Dict], source: str):
        """Migrate historical analysis data"""
        for i, record in enumerate(history_data):
            try:
                request_id = f"{source}_{i}_{int(datetime.now().timestamp())}"
                
                # Determine analysis type from record structure
                analysis_type = "performance_optimization"
                if "threat_score" in record:
                    analysis_type = "threat_analysis"
                elif "anomaly_score" in record:
                    analysis_type = "anomaly_detection"
                
                await self.pg_conn.execute("""
                    INSERT INTO analysis_results 
                    (request_id, analysis_type, status, result, processing_time_ms, confidence)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (request_id) DO NOTHING
                """, 
                    request_id,
                    analysis_type,
                    "completed",
                    json.dumps(record),
                    record.get('processing_time_ms', 0),
                    record.get('confidence', record.get('threat_score', 0.5))
                )
                
            except Exception as e:
                logger.error(f"Failed to migrate history record {i}: {e}")
    
    async def migrate_baseline_data(self, baseline_data: Dict, source: str):
        """Migrate performance baseline data"""
        try:
            await self.pg_conn.execute("""
                INSERT INTO performance_baselines 
                (system_id, baseline_type, baseline_data, established_at, is_active)
                VALUES ($1, $2, $3, $4, $5)
            """,
                source,
                "performance_baseline",
                json.dumps(baseline_data),
                datetime.now(),
                True
            )
            
        except Exception as e:
            logger.error(f"Failed to migrate baseline data: {e}")
    
    async def migrate_sqlite_data(self):
        """Migrate data from SQLite database if it exists"""
        if not os.path.exists(self.sqlite_db):
            logger.warning(f"SQLite database {self.sqlite_db} not found")
            return
        
        try:
            sqlite_conn = sqlite3.connect(self.sqlite_db)
            sqlite_conn.row_factory = sqlite3.Row  # Enable column access by name
            
            # Get all tables
            cursor = sqlite_conn.execute("""
                SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            logger.info(f"Found SQLite tables: {tables}")
            
            for table in tables:
                await self.migrate_sqlite_table(sqlite_conn, table)
            
            sqlite_conn.close()
            
        except Exception as e:
            logger.error(f"Failed to migrate SQLite data: {e}")
    
    async def migrate_sqlite_table(self, sqlite_conn: sqlite3.Connection, table_name: str):
        """Migrate a specific SQLite table"""
        try:
            cursor = sqlite_conn.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            logger.info(f"Migrating {len(rows)} rows from {table_name}")
            
            # Map to appropriate PostgreSQL table based on structure
            for row in rows:
                row_dict = dict(row)
                
                # Determine target table and migrate accordingly
                if 'threat_score' in row_dict or 'analysis_type' in row_dict:
                    await self.migrate_analysis_row(row_dict)
                elif 'metric_name' in row_dict or 'value' in row_dict:
                    await self.migrate_metrics_row(row_dict)
                else:
                    logger.warning(f"Unknown row structure in {table_name}: {list(row_dict.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to migrate table {table_name}: {e}")
    
    async def migrate_analysis_row(self, row: Dict):
        """Migrate analysis result row"""
        try:
            request_id = row.get('id', f"sqlite_{int(datetime.now().timestamp())}")
            analysis_type = row.get('analysis_type', 'unknown')
            
            await self.pg_conn.execute("""
                INSERT INTO analysis_results 
                (request_id, analysis_type, status, result, processing_time_ms, confidence)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (request_id) DO NOTHING
            """,
                str(request_id),
                analysis_type,
                row.get('status', 'completed'),
                json.dumps(row),
                row.get('processing_time_ms', 0),
                row.get('confidence', 0.5)
            )
            
        except Exception as e:
            logger.error(f"Failed to migrate analysis row: {e}")
    
    async def migrate_metrics_row(self, row: Dict):
        """Migrate metrics row"""
        try:
            await self.pg_conn.execute("""
                INSERT INTO system_metrics 
                (metric_type, metric_name, value, unit, labels, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6)
            """,
                row.get('metric_type', 'system'),
                row.get('metric_name', 'unknown'),
                float(row.get('value', 0)),
                row.get('unit', ''),
                json.dumps(row.get('labels', {})),
                datetime.fromisoformat(row.get('timestamp', datetime.now().isoformat()))
            )
            
        except Exception as e:
            logger.error(f"Failed to migrate metrics row: {e}")
    
    async def verify_migration(self):
        """Verify migration success"""
        tables = ['analysis_results', 'system_metrics', 'performance_baselines']
        
        logger.info("Migration verification:")
        for table in tables:
            count = await self.pg_conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            logger.info(f"  {table}: {count} records")
        
        # Test a sample query
        sample_result = await self.pg_conn.fetchrow("""
            SELECT * FROM analysis_results ORDER BY created_at DESC LIMIT 1
        """)
        
        if sample_result:
            logger.info(f"Sample migrated record: {dict(sample_result)}")
        else:
            logger.warning("No migrated records found")
    
    async def cleanup_legacy_data(self, confirm: bool = False):
        """Clean up legacy data files (with confirmation)"""
        if not confirm:
            logger.warning("Skipping legacy data cleanup (not confirmed)")
            return
        
        # Move legacy files to backup directory
        backup_dir = Path('./data_backup')
        backup_dir.mkdir(exist_ok=True)
        
        if self.legacy_data_dir.exists():
            for file in self.legacy_data_dir.glob('*.json'):
                backup_path = backup_dir / file.name
                file.rename(backup_path)
                logger.info(f"Moved {file} to {backup_path}")
        
        if os.path.exists(self.sqlite_db):
            backup_path = backup_dir / 'smartcompute.db'
            os.rename(self.sqlite_db, backup_path)
            logger.info(f"Moved SQLite database to {backup_path}")
    
    async def close(self):
        """Close database connections"""
        if hasattr(self, 'pg_conn'):
            await self.pg_conn.close()


async def main():
    """Main migration function"""
    logger.info("Starting SmartCompute PostgreSQL migration...")
    
    migrator = DataMigrator()
    
    try:
        # Connect to PostgreSQL
        await migrator.connect_postgres()
        
        # Create/verify schema
        await migrator.create_tables()
        
        # Migrate data
        logger.info("Migrating JSON files...")
        await migrator.migrate_json_files()
        
        logger.info("Migrating SQLite data...")
        await migrator.migrate_sqlite_data()
        
        # Verify migration
        await migrator.verify_migration()
        
        # Optional cleanup (commented out for safety)
        # await migrator.cleanup_legacy_data(confirm=False)
        
        logger.info("Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    
    finally:
        await migrator.close()


if __name__ == "__main__":
    asyncio.run(main())