"""
Query-related data models and enums.
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class QueryType(str, Enum):
    """SQL query operation types."""
    READ = "READ"  # SELECT, SHOW, DESCRIBE
    WRITE_SAFE = "WRITE_SAFE"  # INSERT single row, UPDATE with WHERE
    WRITE_RISKY = "WRITE_RISKY"  # DELETE, UPDATE without WHERE, TRUNCATE
    ADMIN = "ADMIN"  # DROP, CREATE, ALTER


class RiskLevel(str, Enum):
    """Risk level for query execution."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class QueryRequest(BaseModel):
    """Request model for natural language query."""
    question: str = Field(..., description="Natural language question about the database")
    execute_immediately: bool = Field(
        default=False,
        description="If True, execute READ queries immediately without confirmation"
    )


class QueryResponse(BaseModel):
    """Response model containing generated SQL and metadata."""
    query_id: str = Field(..., description="Unique identifier for this query")
    sql: str = Field(..., description="Generated SQL query")
    query_type: QueryType = Field(..., description="Type of SQL operation")
    risk_level: RiskLevel = Field(..., description="Risk level of the operation")
    explanation: str = Field(..., description="Human-readable explanation of what the query does")
    estimated_impact: Optional[str] = Field(None, description="Description of affected data")
    requires_confirmation: bool = Field(..., description="Whether this query needs user confirmation")
    executed: bool = Field(default=False, description="Whether the query has been executed")
    results: Optional[List[Dict[str, Any]]] = Field(None, description="Query results if executed")
    row_count: Optional[int] = Field(None, description="Number of rows returned/affected")


class QueryPreview(BaseModel):
    """Preview of data that will be affected by the query."""
    query_id: str
    affected_rows: int = Field(..., description="Number of rows that will be affected")
    sample_data: List[Dict[str, Any]] = Field(..., description="Sample of affected rows")
    warnings: List[str] = Field(default_factory=list, description="Any warnings about the operation")


class ExecutionRequest(BaseModel):
    """Request to execute a pending query."""
    query_id: str = Field(..., description="ID of the query to execute")
    confirmed: bool = Field(..., description="User confirmation flag")


class ExecutionResult(BaseModel):
    """Result of query execution."""
    query_id: str
    success: bool
    message: str
    rows_affected: Optional[int] = None
    results: Optional[List[Dict[str, Any]]] = None
    execution_time_ms: float
    can_rollback: bool = Field(default=False, description="Whether this operation can be rolled back")


class QueryHistory(BaseModel):
    """Historical query record."""
    query_id: str
    timestamp: datetime
    question: str
    sql: str
    query_type: QueryType
    risk_level: RiskLevel
    executed: bool
    success: Optional[bool] = None
    rows_affected: Optional[int] = None
    execution_time_ms: Optional[float] = None
    user: Optional[str] = None


class DirectSQLRequest(BaseModel):
    """Request model for executing pre-generated SQL directly."""
    sql: str = Field(..., description="Pre-generated SQL query to execute")
    question: Optional[str] = Field(None, description="Original natural language question (for logging)")


class DirectSQLResponse(BaseModel):
    """Response model for direct SQL execution with simple answer."""
    success: bool = Field(..., description="Whether execution was successful")
    answer: str = Field(..., description="Simple text answer to the question")
    sql_executed: str = Field(..., description="SQL query that was executed")
    rows_affected: Optional[int] = Field(None, description="Number of rows affected/returned")
    execution_time_ms: float = Field(..., description="Execution time in milliseconds")
    error: Optional[str] = Field(None, description="Error message if execution failed")


class SchemaInfo(BaseModel):
    """Database schema information."""
    tables: List[Dict[str, Any]] = Field(..., description="List of tables with columns")
    views: Optional[List[str]] = Field(default_factory=list)
    relationships: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
