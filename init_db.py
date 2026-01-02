import os
import asyncio
import logging
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine import URL

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "extraction_db")
    db_schema = os.getenv("DB_SCHEMA", "public")

    sa_url = URL.create(
        drivername="postgresql+asyncpg",
        username=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
        database=db_name,
    )

    engine = create_async_engine(sa_url)
    
    table_name = "extraction_tracker"
    
    # SQL to create schema and table
    queries = [
        f"CREATE SCHEMA IF NOT EXISTS {db_schema}",
        f"""
        CREATE TABLE IF NOT EXISTS {db_schema}.{table_name} (
            request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            application_id VARCHAR(255) NOT NULL,
            metadata JSONB NOT NULL,
            status VARCHAR(50) NOT NULL,
            extracted_data JSONB,
            message TEXT,
            errors JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        """,
        # Index on application_id for filtering
        f"CREATE INDEX IF NOT EXISTS idx_application_id ON {db_schema}.{table_name} (application_id)",
        # GIN index on metadata for fast checksum lookup
        f"CREATE INDEX IF NOT EXISTS idx_metadata_checksum ON {db_schema}.{table_name} USING gin (metadata)"
    ]

    try:
        async with engine.begin() as conn:
            # Ensure schema exists first
            await conn.exec_driver_sql(queries[0])
            
            # Check if table exists and alter column if necessary
            check_table_query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = '{db_schema}' AND table_name = '{table_name}' AND column_name = 'message'"
            result = await conn.exec_driver_sql(check_table_query)
            row = result.fetchone()
            if row and row[1] != 'text':
                logger.info(f"Altering column 'message' in {db_schema}.{table_name} to TEXT")
                await conn.exec_driver_sql(f"ALTER TABLE {db_schema}.{table_name} ALTER COLUMN message TYPE TEXT")

            for query in queries[1:]:
                # Correctly await the coroutine
                await conn.exec_driver_sql(query)
        logger.info(f"Database initialized successfully in schema '{db_schema}'")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
