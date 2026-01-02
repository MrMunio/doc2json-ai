# db_client.py
import os
import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Optional, Tuple, Any

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker


logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    pass

class DatabaseClient:
    """
    Async PostgreSQL database client using SQLAlchemy (asyncpg).
    Env vars: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    Default schema: 'prodnextgen'
    """
    def __init__(
        self,
        *,
        host: Optional[str] = None,
        port: Optional[str] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        schema: str = "prodnextgen",
        pool_size: int = 20,
        max_overflow: int = 30,
        echo: bool = False,
    ) -> None:
        self.connection_params = {
            "host": host or os.getenv("DB_HOST", "db"),
            "port": int(port or os.getenv("DB_PORT", "5432")),
            "database": database or os.getenv("DB_NAME", "extraction_db"),
            "user": user or os.getenv("DB_USER", "postgres"),
            "password": password or os.getenv("DB_PASSWORD", "postgres"),
        }
        self.schema = schema or os.getenv("DB_SCHEMA", "public")

        sa_url = URL.create(
            drivername="postgresql+asyncpg",
            username=self.connection_params["user"],
            password=self.connection_params["password"],
            host=self.connection_params["host"],
            port=self.connection_params["port"],
            database=self.connection_params["database"],
        )

        self.engine = create_async_engine(
            sa_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=echo,
            future=True,
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        logger.info("AsyncDatabaseClient initialized for %s", self.connection_params["database"])

    @asynccontextmanager
    async def _raw_connection(self):
        async with self.engine.begin() as conn:  # This auto-commits on successful exit
            try:
                await conn.exec_driver_sql(f"SET search_path TO {self.schema}, public")
                yield conn
                # No explicit commit needed - engine.begin() commits on clean exit
            except Exception as e:
                logger.exception("Database error: %s", e)
                # Rollback happens automatically on exception
                raise DatabaseError(str(e)) from e


    async def execute_query(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
        async with self._raw_connection() as conn:
            result = await conn.exec_driver_sql(query, params or ())
            rows = result.mappings().all()
            return [dict(r) for r in rows]

    async def execute_non_query(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> int:
        async with self._raw_connection() as conn:
            result = await conn.exec_driver_sql(query, params or ())
            return result.rowcount or 0

    async def test_connection(self) -> bool:
        try:
            await self.execute_query("SELECT 1;")
            logger.info("Async database connection test successful.")
            return True
        except Exception as e:
            logger.warning("Async database connection test failed: %s", e)
            return False


    # Utilities
    def set_schema(self, schema: str) -> None:
        logger.info("Switching schema: %s -> %s", self.schema, schema)
        self.schema = schema

    async def dispose(self) -> None:
        logger.info("Disposing async engine.")
        await self.engine.dispose()
