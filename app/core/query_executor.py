"""
Query executor with confirmation workflow and transaction support.
"""
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.core.database import db_manager
from app.services.sql_generator import IntelligentSQLGenerator
from app.core.query_classifier import query_classifier
from app.models.query_models import (
    QueryType,
    RiskLevel,
    QueryResponse,
    QueryPreview,
    ExecutionResult,
    QueryHistory,
)
from app.config import settings
from loguru import logger


class QueryExecutor:
    """Handles query execution with safety checks and confirmation workflow."""

    def __init__(self):
        """Initialize query executor."""
        self.pending_queries: Dict[str, Dict[str, Any]] = {}
        self.query_history: List[QueryHistory] = []
        self.schema_cache: Optional[Dict[str, Any]] = None
        self.sql_generator = IntelligentSQLGenerator()

    def get_schema(self) -> Dict[str, Any]:
        """Get database schema (cached)."""
        if self.schema_cache is None:
            logger.info("Loading database schema...")
            self.schema_cache = db_manager.get_schema_info()
        return self.schema_cache

    def refresh_schema(self) -> Dict[str, Any]:
        """Refresh schema cache."""
        logger.info("Refreshing database schema...")
        self.schema_cache = db_manager.get_schema_info()
        return self.schema_cache

    def process_question(
        self,
        question: str,
        execute_immediately: bool = False
    ) -> QueryResponse:
        """
        Process natural language question and generate SQL.

        Args:
            question: Natural language question
            execute_immediately: Whether to execute READ queries immediately

        Returns:
            QueryResponse with SQL and metadata
        """
        try:
            # Get schema
            schema = self.get_schema()

            # Detect language (simple Hebrew detection)
            language = 'he' if any(ord(char) >= 0x0590 and ord(char) <= 0x05FF for char in question) else 'en'
            logger.info(f"Detected language: {language}")

            # Generate SQL using pattern-based generator
            ai_result = self.sql_generator.generate_sql(question, language=language, schema_info=schema)

            # Check if generation was successful
            if not ai_result.get("success", False):
                error_msg = ai_result.get("error", "Could not generate SQL")
                raise ValueError(error_msg)

            # Extract components
            sql = ai_result.get("sql", "")

            # Pattern-based generator doesn't provide these, so we'll classify them ourselves
            query_type_str = "READ"  # Default, will be classified below
            risk_level_str = "low"   # Default, will be classified below
            explanation = f"Generated using {ai_result.get('method', 'pattern')} method (confidence: {ai_result.get('confidence', 0):.0%})"
            estimated_impact = f"Pattern type: {ai_result.get('pattern_type', 'unknown')}"

            # Validate and classify
            query_type = QueryType(query_type_str)
            risk_level = RiskLevel(risk_level_str)

            # Double-check classification with our classifier
            classified_type, classified_risk = query_classifier.classify_query(sql)

            # Use higher risk level
            if classified_risk.value in ["high", "critical"]:
                risk_level = classified_risk
                query_type = classified_type

            # Validate query
            is_valid, warnings = query_classifier.validate_query(sql, query_type)

            if not is_valid:
                raise ValueError(f"Invalid query: {', '.join(warnings)}")

            # Generate query ID
            query_id = str(uuid.uuid4())

            # Determine if confirmation needed
            requires_confirmation = self._requires_confirmation(query_type, risk_level)

            # Store as pending query
            self.pending_queries[query_id] = {
                "question": question,
                "sql": sql,
                "query_type": query_type,
                "risk_level": risk_level,
                "explanation": explanation,
                "estimated_impact": estimated_impact,
                "warnings": warnings,
                "timestamp": datetime.now(),
            }

            # Execute immediately if allowed
            executed = False
            results = None
            row_count = None

            if execute_immediately and query_type == QueryType.READ:
                logger.info(f"Executing READ query immediately: {query_id}")
                exec_result = self._execute_query(query_id)
                if exec_result.success:
                    executed = True
                    results = exec_result.results
                    row_count = exec_result.rows_affected

            # Add to history
            self._add_to_history(query_id, executed=executed)

            return QueryResponse(
                query_id=query_id,
                sql=sql,
                query_type=query_type,
                risk_level=risk_level,
                explanation=explanation,
                estimated_impact=estimated_impact,
                requires_confirmation=requires_confirmation,
                executed=executed,
                results=results,
                row_count=row_count,
            )

        except Exception as e:
            logger.error(f"Question processing error: {e}")
            raise

    def preview_query(self, query_id: str) -> QueryPreview:
        """
        Preview affected rows for write operations.

        Args:
            query_id: Query ID

        Returns:
            QueryPreview with affected row count and samples
        """
        if query_id not in self.pending_queries:
            raise ValueError(f"Query not found: {query_id}")

        query_info = self.pending_queries[query_id]
        sql = query_info["sql"]
        query_type = query_info["query_type"]

        # Only preview write operations
        if query_type not in [QueryType.WRITE_SAFE, QueryType.WRITE_RISKY]:
            raise ValueError("Preview only available for write operations")

        try:
            # Get affected rows preview
            count, sample_data = db_manager.get_affected_rows_preview(sql, limit=10)

            warnings = query_info.get("warnings", [])
            if count > 100:
                warnings.append(f"Large operation: {count} rows will be affected")

            return QueryPreview(
                query_id=query_id,
                affected_rows=count,
                sample_data=sample_data,
                warnings=warnings,
            )

        except Exception as e:
            logger.error(f"Preview error: {e}")
            raise

    def execute_query(
        self,
        query_id: str,
        confirmed: bool = False
    ) -> ExecutionResult:
        """
        Execute a pending query.

        Args:
            query_id: Query ID
            confirmed: User confirmation flag

        Returns:
            ExecutionResult with execution status and results
        """
        if query_id not in self.pending_queries:
            raise ValueError(f"Query not found: {query_id}")

        query_info = self.pending_queries[query_id]
        query_type = query_info["query_type"]
        risk_level = query_info["risk_level"]

        # Check if confirmation required
        if self._requires_confirmation(query_type, risk_level) and not confirmed:
            raise ValueError("Confirmation required for this operation")

        # Check if admin operations are enabled
        if query_type == QueryType.ADMIN and not settings.enable_admin_operations:
            raise ValueError("Admin operations are disabled in configuration")

        # Execute
        result = self._execute_query(query_id)

        # Update history
        self._update_history(query_id, result)

        return result

    def _execute_query(self, query_id: str) -> ExecutionResult:
        """
        Internal method to execute query.

        Args:
            query_id: Query ID

        Returns:
            ExecutionResult
        """
        query_info = self.pending_queries[query_id]
        sql = query_info["sql"]
        query_type = query_info["query_type"]

        try:
            # Execute based on type
            if query_type == QueryType.READ:
                # Simple execution for reads
                results, rows_affected, exec_time = db_manager.execute_query(sql)
                success = True
                message = f"Query executed successfully. {len(results)} rows returned."
                can_rollback = False

            else:
                # Use transaction for writes
                results, rows_affected, exec_time = db_manager.execute_with_transaction(sql)
                success = True
                message = f"Query executed successfully. {rows_affected} rows affected."
                can_rollback = False  # Already committed

            return ExecutionResult(
                query_id=query_id,
                success=success,
                message=message,
                rows_affected=rows_affected,
                results=results,
                execution_time_ms=exec_time,
                can_rollback=can_rollback,
            )

        except Exception as e:
            logger.error(f"Execution error: {e}")
            return ExecutionResult(
                query_id=query_id,
                success=False,
                message=f"Execution failed: {str(e)}",
                execution_time_ms=0,
                can_rollback=False,
            )

    def _requires_confirmation(
        self,
        query_type: QueryType,
        risk_level: RiskLevel
    ) -> bool:
        """
        Determine if query requires user confirmation.

        Args:
            query_type: Query type
            risk_level: Risk level

        Returns:
            True if confirmation required
        """
        if not settings.require_confirmation_for_writes:
            return False

        # Always require confirmation for risky/admin operations
        if query_type in [QueryType.WRITE_RISKY, QueryType.ADMIN]:
            return True

        # Require confirmation for high/critical risk
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return True

        # Require confirmation for write operations
        if query_type == QueryType.WRITE_SAFE:
            return True

        return False

    def _add_to_history(self, query_id: str, executed: bool = False):
        """Add query to history."""
        query_info = self.pending_queries[query_id]

        history_entry = QueryHistory(
            query_id=query_id,
            timestamp=query_info["timestamp"],
            question=query_info["question"],
            sql=query_info["sql"],
            query_type=query_info["query_type"],
            risk_level=query_info["risk_level"],
            executed=executed,
        )

        self.query_history.append(history_entry)

    def _update_history(self, query_id: str, result: ExecutionResult):
        """Update history entry with execution result."""
        for entry in self.query_history:
            if entry.query_id == query_id:
                entry.executed = True
                entry.success = result.success
                entry.rows_affected = result.rows_affected
                entry.execution_time_ms = result.execution_time_ms
                break

    def get_history(self, limit: int = 50) -> List[QueryHistory]:
        """Get query history."""
        return self.query_history[-limit:]


# Global executor instance
query_executor = QueryExecutor()
