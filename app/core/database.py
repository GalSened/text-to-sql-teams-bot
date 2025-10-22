"""
Database connection and query execution module for SQL Server.
"""
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
import time

from app.config import settings
from loguru import logger


class DatabaseManager:
    """Manages SQL Server database connections and operations."""

    def __init__(self):
        """Initialize database manager with connection pool."""
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self._init_engine()

    def _init_engine(self):
        """Initialize SQLAlchemy engine with connection pooling."""
        try:
            connection_string = settings.get_connection_string()
            logger.info(f"Initializing database connection to: {settings.db_server}/{settings.db_name}")

            self.engine = create_engine(
                connection_string,
                pool_pre_ping=True,  # Verify connections before using
                pool_size=5,
                max_overflow=10,
                echo=settings.debug,
            )

            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            # Test connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1 AS test"))
                logger.info("Database connection successful")

        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise

    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions.

        Usage:
            with db_manager.get_session() as session:
                result = session.execute(text("SELECT * FROM users"))
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {e}")
            raise
        finally:
            session.close()

    def execute_query(
        self,
        sql: str,
        params: Optional[Dict[str, Any]] = None,
        fetch_results: bool = True,
    ) -> Tuple[List[Dict[str, Any]], int, float]:
        """
        Execute SQL query and return results.

        Args:
            sql: SQL query string
            params: Optional parameters for parameterized queries
            fetch_results: Whether to fetch and return results

        Returns:
            Tuple of (results, rows_affected, execution_time_ms)
        """
        start_time = time.time()
        results = []
        rows_affected = 0

        try:
            with self.get_session() as session:
                # Execute query
                result = session.execute(text(sql), params or {})

                # Get rows affected
                rows_affected = result.rowcount

                # Fetch results if needed
                if fetch_results and result.returns_rows:
                    rows = result.fetchall()
                    # Convert rows to dictionaries
                    if rows:
                        columns = result.keys()
                        results = [dict(zip(columns, row)) for row in rows]

                        # Limit results
                        if len(results) > settings.max_rows_return:
                            logger.warning(
                                f"Query returned {len(results)} rows, "
                                f"limiting to {settings.max_rows_return}"
                            )
                            results = results[:settings.max_rows_return]

                session.commit()

        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise

        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        return results, rows_affected, execution_time

    def execute_with_transaction(
        self,
        sql: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Dict[str, Any]], int, float]:
        """
        Execute query within an explicit transaction.
        Useful for write operations that may need to be rolled back.

        Args:
            sql: SQL query string
            params: Optional parameters

        Returns:
            Tuple of (results, rows_affected, execution_time_ms)
        """
        start_time = time.time()
        results = []
        rows_affected = 0

        with self.get_session() as session:
            try:
                # Begin explicit transaction
                session.execute(text("BEGIN TRANSACTION"))

                # Execute query
                result = session.execute(text(sql), params or {})
                rows_affected = result.rowcount

                # Fetch results if available
                if result.returns_rows:
                    rows = result.fetchall()
                    if rows:
                        columns = result.keys()
                        results = [dict(zip(columns, row)) for row in rows]

                # Commit transaction
                session.execute(text("COMMIT TRANSACTION"))
                session.commit()

            except Exception as e:
                # Rollback on error
                try:
                    session.execute(text("ROLLBACK TRANSACTION"))
                except:
                    pass
                logger.error(f"Transaction error: {e}")
                raise

        execution_time = (time.time() - start_time) * 1000
        return results, rows_affected, execution_time

    def get_affected_rows_preview(
        self,
        sql: str,
        limit: int = 10
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Preview rows that would be affected by UPDATE/DELETE query.

        Args:
            sql: The UPDATE or DELETE query
            limit: Maximum number of sample rows to return

        Returns:
            Tuple of (total_affected_count, sample_rows)
        """
        try:
            # Convert UPDATE/DELETE to SELECT to preview
            select_sql = self._convert_to_select_preview(sql)

            with self.get_session() as session:
                # Get count
                count_sql = f"SELECT COUNT(*) as cnt FROM ({select_sql}) as preview"
                count_result = session.execute(text(count_sql))
                total_count = count_result.fetchone()[0]

                # Get sample data
                sample_sql = f"SELECT TOP {limit} * FROM ({select_sql}) as preview"
                sample_result = session.execute(text(sample_sql))
                rows = sample_result.fetchall()

                sample_data = []
                if rows:
                    columns = sample_result.keys()
                    sample_data = [dict(zip(columns, row)) for row in rows]

                return total_count, sample_data

        except Exception as e:
            logger.error(f"Preview error: {e}")
            raise

    def _convert_to_select_preview(self, sql: str) -> str:
        """
        Convert UPDATE/DELETE query to SELECT for preview.

        Args:
            sql: UPDATE or DELETE query

        Returns:
            SELECT query that shows affected rows
        """
        sql_upper = sql.upper().strip()

        if sql_upper.startswith("DELETE"):
            # DELETE FROM table WHERE condition
            # -> SELECT * FROM table WHERE condition
            select_sql = sql.replace("DELETE", "SELECT *", 1)

        elif sql_upper.startswith("UPDATE"):
            # UPDATE table SET ... WHERE condition
            # -> SELECT * FROM table WHERE condition
            parts = sql.split("SET", 1)
            if len(parts) == 2:
                table_part = parts[0].replace("UPDATE", "SELECT * FROM", 1)
                where_part = ""
                if "WHERE" in parts[1].upper():
                    where_part = "WHERE" + parts[1].upper().split("WHERE", 1)[1]
                select_sql = f"{table_part} {where_part}"
            else:
                raise ValueError("Invalid UPDATE query format")
        else:
            raise ValueError("Only UPDATE and DELETE queries can be previewed")

        return select_sql

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get database schema information using SQLAlchemy introspection.

        Returns:
            Dictionary containing tables, columns, and relationships
        """
        try:
            inspector = inspect(self.engine)

            schema_info = {
                "tables": [],
                "views": [],
            }

            # Get all tables
            table_names = inspector.get_table_names()

            for table_name in table_names:
                columns = inspector.get_columns(table_name)
                pk_constraint = inspector.get_pk_constraint(table_name)
                foreign_keys = inspector.get_foreign_keys(table_name)

                table_info = {
                    "name": table_name,
                    "columns": [
                        {
                            "name": col["name"],
                            "type": str(col["type"]),
                            "nullable": col["nullable"],
                            "default": col.get("default"),
                            "primary_key": col["name"] in (pk_constraint.get("constrained_columns", []))
                        }
                        for col in columns
                    ],
                    "primary_keys": pk_constraint.get("constrained_columns", []),
                    "foreign_keys": [
                        {
                            "columns": fk["constrained_columns"],
                            "referred_table": fk["referred_table"],
                            "referred_columns": fk["referred_columns"],
                        }
                        for fk in foreign_keys
                    ],
                }

                schema_info["tables"].append(table_info)

            # Get views
            view_names = inspector.get_view_names()
            schema_info["views"] = view_names

            logger.info(f"Retrieved schema info: {len(table_names)} tables, {len(view_names)} views")
            return schema_info

        except Exception as e:
            logger.error(f"Schema introspection error: {e}")
            raise

    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()
