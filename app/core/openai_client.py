"""
OpenAI integration for natural language to SQL conversion.
"""
from openai import OpenAI
from typing import Dict, Any, Optional
import json

from app.config import settings
from app.models.query_models import QueryType, RiskLevel
from loguru import logger


class OpenAIClient:
    """Handles OpenAI API interactions for SQL generation."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def generate_sql(
        self,
        question: str,
        schema_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate SQL query from natural language question.

        Args:
            question: Natural language question
            schema_info: Database schema information

        Returns:
            Dictionary containing SQL, type, risk level, and explanation
        """
        try:
            # Build the prompt
            prompt = self._build_prompt(question, schema_info)

            # Call OpenAI API
            logger.info(f"Generating SQL for question: {question}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent SQL generation
                response_format={"type": "json_object"}
            )

            # Parse response
            content = response.choices[0].message.content
            result = json.loads(content)

            logger.info(f"Generated SQL: {result.get('sql', 'N/A')}")
            return result

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _get_system_prompt(self) -> str:
        """Get the system prompt for SQL generation."""
        return """You are an expert SQL Server database assistant. Your task is to convert natural language questions into valid T-SQL queries.

IMPORTANT RULES:
1. Generate syntactically correct T-SQL (SQL Server dialect)
2. Use TOP instead of LIMIT for row limiting
3. For write operations (INSERT/UPDATE/DELETE):
   - Always include WHERE clauses for UPDATE/DELETE unless explicitly asked to affect all rows
   - Explain the potential impact clearly
   - Mark risk level appropriately
4. Use proper T-SQL functions and syntax
5. Consider the schema relationships when joining tables
6. Always return valid JSON in the exact format specified

RESPONSE FORMAT:
You must return a JSON object with these exact fields:
{
  "sql": "The T-SQL query here",
  "query_type": "READ|WRITE_SAFE|WRITE_RISKY|ADMIN",
  "risk_level": "low|medium|high|critical",
  "explanation": "Clear explanation of what this query does",
  "estimated_impact": "Description of affected data (for write operations)",
  "warnings": ["Warning 1", "Warning 2"] (optional)
}

QUERY TYPES:
- READ: SELECT, SHOW, DESCRIBE operations
- WRITE_SAFE: INSERT single row, UPDATE with specific WHERE clause
- WRITE_RISKY: DELETE, UPDATE without WHERE or affecting many rows, TRUNCATE
- ADMIN: DROP, CREATE, ALTER operations

RISK LEVELS:
- low: Read operations, safe single-row writes
- medium: Multi-row INSERT, targeted UPDATE/DELETE with WHERE
- high: Bulk operations, UPDATE/DELETE affecting many rows
- critical: Operations without WHERE, TRUNCATE, DROP, ALTER operations
"""

    def _build_prompt(
        self,
        question: str,
        schema_info: Dict[str, Any]
    ) -> str:
        """
        Build the user prompt with schema context.

        Args:
            question: User's natural language question
            schema_info: Database schema information

        Returns:
            Formatted prompt string
        """
        # Format schema information
        schema_text = self._format_schema(schema_info)

        # Build comprehensive prompt
        prompt = f"""DATABASE SCHEMA:
{schema_text}

USER QUESTION:
{question}

Generate a T-SQL query to answer this question. Consider:
1. Which tables and columns are needed
2. Any necessary JOINs based on foreign key relationships
3. Appropriate WHERE conditions
4. Proper SQL Server syntax (use TOP, not LIMIT)
5. For write operations, assess the impact and risk

Return your response as JSON following the specified format."""

        return prompt

    def _format_schema(self, schema_info: Dict[str, Any]) -> str:
        """
        Format schema information for the prompt.

        Args:
            schema_info: Database schema dictionary

        Returns:
            Formatted schema string
        """
        lines = []

        # Format tables
        for table in schema_info.get("tables", []):
            lines.append(f"\nTable: {table['name']}")

            # Columns
            lines.append("  Columns:")
            for col in table.get("columns", []):
                pk_marker = " (PRIMARY KEY)" if col.get("primary_key") else ""
                nullable = "NULL" if col.get("nullable") else "NOT NULL"
                lines.append(f"    - {col['name']}: {col['type']} {nullable}{pk_marker}")

            # Foreign keys
            if table.get("foreign_keys"):
                lines.append("  Foreign Keys:")
                for fk in table["foreign_keys"]:
                    fk_cols = ", ".join(fk["columns"])
                    ref_table = fk["referred_table"]
                    ref_cols = ", ".join(fk["referred_columns"])
                    lines.append(f"    - {fk_cols} -> {ref_table}({ref_cols})")

        # Format views
        if schema_info.get("views"):
            lines.append("\nViews:")
            for view in schema_info["views"]:
                lines.append(f"  - {view}")

        return "\n".join(lines)

    def explain_query(self, sql: str) -> str:
        """
        Generate a human-readable explanation of a SQL query.

        Args:
            sql: SQL query to explain

        Returns:
            Plain English explanation
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a database expert. Explain SQL queries in simple, non-technical language."
                    },
                    {
                        "role": "user",
                        "content": f"Explain this SQL query in simple terms:\n\n{sql}"
                    }
                ],
                temperature=0.3,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Query explanation error: {e}")
            return "Unable to generate explanation"


# Global OpenAI client instance
openai_client = OpenAIClient()
