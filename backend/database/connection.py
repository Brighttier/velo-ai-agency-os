"""
Database Connection Manager for Velo
Handles PostgreSQL connections (local and Cloud SQL)
"""

import os
from typing import Optional, Dict, Any
from contextlib import contextmanager
import asyncpg
from asyncpg import Pool, Connection

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "velo"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# Cloud SQL configuration (when deployed)
CLOUD_SQL_CONNECTION_NAME = os.getenv("CLOUD_SQL_CONNECTION_NAME")  # "velo-479115:us-central1:velo-db"

# Connection pool
_pool: Optional[Pool] = None


async def init_db_pool() -> Pool:
    """
    Initialize database connection pool

    Returns:
        Connection pool
    """
    global _pool

    if _pool is not None:
        return _pool

    # Check if running on Cloud Run with Cloud SQL
    if CLOUD_SQL_CONNECTION_NAME:
        # Use Unix socket for Cloud SQL
        host = f"/cloudsql/{CLOUD_SQL_CONNECTION_NAME}"
        _pool = await asyncpg.create_pool(
            host=host,
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            min_size=2,
            max_size=10,
        )
    else:
        # Use TCP connection for local development
        _pool = await asyncpg.create_pool(
            **DB_CONFIG,
            min_size=2,
            max_size=10,
        )

    print(f"✅ Database pool initialized: {DB_CONFIG['database']}")
    return _pool


async def close_db_pool():
    """Close database connection pool"""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        print("✅ Database pool closed")


def get_pool() -> Pool:
    """
    Get current database pool

    Raises:
        RuntimeError: If pool not initialized
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db_pool() first.")
    return _pool


@contextmanager
def get_connection():
    """
    Get database connection from pool (sync context manager)

    Usage:
        with get_connection() as conn:
            result = await conn.fetch("SELECT * FROM users")
    """
    pool = get_pool()
    try:
        conn = yield pool.acquire()
    finally:
        pass  # Connection is auto-released by pool


class Database:
    """Database operations wrapper"""

    def __init__(self):
        self.pool = None

    async def initialize(self):
        """Initialize database pool"""
        self.pool = await init_db_pool()

    async def close(self):
        """Close database pool"""
        await close_db_pool()

    async def execute(self, query: str, *args) -> str:
        """
        Execute a query (INSERT, UPDATE, DELETE)

        Args:
            query: SQL query
            *args: Query parameters

        Returns:
            Query result status
        """
        pool = get_pool()
        async with pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> list:
        """
        Fetch multiple rows

        Args:
            query: SQL query
            *args: Query parameters

        Returns:
            List of records
        """
        pool = get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> Optional[Dict]:
        """
        Fetch single row

        Args:
            query: SQL query
            *args: Query parameters

        Returns:
            Single record or None
        """
        pool = get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None

    async def fetchval(self, query: str, *args) -> Any:
        """
        Fetch single value

        Args:
            query: SQL query
            *args: Query parameters

        Returns:
            Single value
        """
        pool = get_pool()
        async with pool.acquire() as conn:
            return await conn.fetchval(query, *args)


# Singleton instance
_db: Optional[Database] = None


def get_db() -> Database:
    """Get database instance"""
    global _db
    if _db is None:
        _db = Database()
    return _db
