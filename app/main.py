"""
FastAPI application for Text-to-SQL.
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import sys

from app.config import settings
from app.models.query_models import (
    QueryRequest,
    QueryResponse,
    QueryPreview,
    ExecutionRequest,
    ExecutionResult,
    QueryHistory,
    SchemaInfo,
    DirectSQLRequest,
    DirectSQLResponse,
)
from app.core.query_executor import query_executor
from app.core.database import db_manager
from app.api.teams_endpoint import router as teams_router
from loguru import logger

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
)
logger.add(
    settings.log_file,
    rotation="10 MB",
    retention="7 days",
    level=settings.log_level,
)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered Text-to-SQL application with safety features for SQL Server",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Teams bot router
app.include_router(teams_router)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Test database connection
    try:
        if db_manager.test_connection():
            logger.info("Database connection successful")
            # Load schema cache
            query_executor.get_schema()
            logger.info("Schema cache loaded")
        else:
            logger.error("Database connection failed")
    except Exception as e:
        logger.error(f"Startup error: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down application")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        db_healthy = db_manager.test_connection()
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "database": "connected" if db_healthy else "disconnected",
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)},
        )


@app.get("/schema", response_model=SchemaInfo)
async def get_schema():
    """
    Get database schema information.

    Returns:
        SchemaInfo: Database tables, columns, and relationships
    """
    try:
        schema = query_executor.get_schema()
        return SchemaInfo(**schema)
    except Exception as e:
        logger.error(f"Schema retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve schema: {str(e)}",
        )


@app.post("/schema/refresh", response_model=SchemaInfo)
async def refresh_schema():
    """
    Refresh cached database schema.

    Returns:
        SchemaInfo: Updated database schema
    """
    try:
        schema = query_executor.refresh_schema()
        return SchemaInfo(**schema)
    except Exception as e:
        logger.error(f"Schema refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh schema: {str(e)}",
        )


@app.post("/query/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Convert natural language question to SQL.

    Args:
        request: QueryRequest with natural language question

    Returns:
        QueryResponse with generated SQL and metadata
    """
    try:
        logger.info(f"Processing question: {request.question}")
        response = query_executor.process_question(
            question=request.question,
            execute_immediately=request.execute_immediately,
        )
        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Question processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}",
        )


@app.get("/query/preview/{query_id}", response_model=QueryPreview)
async def preview_query(query_id: str):
    """
    Preview affected rows for write operations.

    Args:
        query_id: Query ID to preview

    Returns:
        QueryPreview with affected row count and samples
    """
    try:
        preview = query_executor.preview_query(query_id)
        return preview

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Preview error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to preview query: {str(e)}",
        )


@app.post("/query/execute", response_model=ExecutionResult)
async def execute_query(request: ExecutionRequest):
    """
    Execute a pending query with confirmation.

    Args:
        request: ExecutionRequest with query_id and confirmation

    Returns:
        ExecutionResult with execution status and results
    """
    try:
        logger.info(f"Executing query: {request.query_id} (confirmed: {request.confirmed})")
        result = query_executor.execute_query(
            query_id=request.query_id,
            confirmed=request.confirmed,
        )
        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Execution error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute query: {str(e)}",
        )


@app.get("/query/history", response_model=List[QueryHistory])
async def get_history(limit: int = 50):
    """
    Get query execution history.

    Args:
        limit: Maximum number of history entries to return

    Returns:
        List of QueryHistory entries
    """
    try:
        history = query_executor.get_history(limit=limit)
        return history
    except Exception as e:
        logger.error(f"History retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}",
        )


@app.post("/query/execute-sql", response_model=DirectSQLResponse)
async def execute_direct_sql(request: DirectSQLRequest):
    """
    Execute pre-generated SQL query directly and return simple answer.

    This endpoint is designed for PowerShell orchestrator that calls Claude CLI
    to generate SQL, then sends it here for safe execution.

    Args:
        request: DirectSQLRequest with SQL query

    Returns:
        DirectSQLResponse with simple text answer
    """
    import time

    try:
        logger.info(f"Executing direct SQL: {request.sql[:100]}...")

        start_time = time.time()

        # Execute query (db_manager handles both SELECT and DML safely)
        results, rows_affected, exec_time_ms = db_manager.execute_query(request.sql)

        # Format simple answer based on results
        if results:
            # For SELECT queries with results
            if len(results) == 1 and len(results[0]) == 1:
                # Single value result - return just the value
                value = list(results[0].values())[0]
                answer = str(value) if value is not None else "0"
            else:
                # Multiple rows/columns - provide count and first few results
                answer = f"Found {len(results)} results"
                if len(results) <= 5:
                    # Show all results if 5 or fewer
                    answer += ":\n" + "\n".join([str(dict(row)) for row in results[:5]])
                else:
                    # Show first 3 if more than 5
                    answer += f" (showing first 3):\n" + "\n".join([str(dict(row)) for row in results[:3]])
        elif rows_affected is not None and rows_affected > 0:
            # For DML operations (INSERT/UPDATE/DELETE)
            answer = f"{rows_affected} rows affected"
        else:
            # No results
            answer = "No results found"

        return DirectSQLResponse(
            success=True,
            answer=answer,
            sql_executed=request.sql,
            rows_affected=rows_affected or len(results) if results else 0,
            execution_time_ms=exec_time_ms,
            error=None,
        )

    except Exception as e:
        logger.error(f"Direct SQL execution error: {e}")
        return DirectSQLResponse(
            success=False,
            answer=f"Error: {str(e)}",
            sql_executed=request.sql,
            rows_affected=0,
            execution_time_ms=0,
            error=str(e),
        )


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )
