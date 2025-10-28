"""
Claude CLI Direct Client - Calls local Claude Code CLI directly
No API keys needed - uses the Claude Code CLI already running on your computer.
"""
from typing import Dict, Any
import subprocess
import json
from loguru import logger
from app.models.query_models import QueryType, RiskLevel


class ClaudeCLIClient:
    """Calls Claude Code CLI directly for SQL generation."""

    def __init__(self):
        """Initialize Claude CLI client."""
        # Try to find claude command - check common locations
        self.claude_cmd = None

        # Try standard 'claude' command first
        try:
            check = subprocess.run(
                ['claude', '--version'],
                capture_output=True,
                timeout=5
            )
            if check.returncode == 0:
                self.claude_cmd = 'claude'
                logger.info("✓ Claude CLI found in PATH")
        except (FileNotFoundError, Exception):
            pass

        # If not found, try common Windows npm location
        if not self.claude_cmd:
            npm_claude = r"C:\Users\gals\AppData\Roaming\npm\claude.cmd"
            try:
                check = subprocess.run(
                    [npm_claude, '--version'],
                    capture_output=True,
                    timeout=5
                )
                if check.returncode == 0:
                    self.claude_cmd = npm_claude
                    logger.info(f"✓ Claude CLI found at: {npm_claude}")
            except (FileNotFoundError, Exception):
                pass

        if self.claude_cmd:
            logger.info("✓ Claude CLI client initialized (using local claude command)")
        else:
            logger.warning("⚠ Claude command not found. Complex queries will fail.")
            logger.info("Install Claude Desktop or add claude to PATH")

    def generate_sql(
        self,
        question: str,
        schema_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate SQL using local Claude Code CLI.

        Args:
            question: Natural language question
            schema_info: Database schema information

        Returns:
            Dictionary containing SQL, type, risk level, and explanation
        """
        try:
            # Format schema for prompt
            schema_text = self._format_schema(schema_info)

            # Build prompt
            prompt = f"""Generate a T-SQL query for this question.

DATABASE SCHEMA:
{schema_text}

QUESTION:
{question}

Return ONLY a JSON object with these fields:
{{
  "sql": "The T-SQL query",
  "query_type": "READ|WRITE_SAFE|WRITE_RISKY|ADMIN",
  "risk_level": "low|medium|high|critical",
  "explanation": "Brief explanation of what the query does"
}}

IMPORTANT: Return ONLY the JSON, no markdown formatting or extra text."""

            if not self.claude_cmd:
                raise RuntimeError(
                    "Claude CLI not found. Please ensure Claude Code is installed and "
                    "'claude' command is available in PATH"
                )

            logger.info(f"Calling Claude CLI for question: {question[:50]}...")

            # Call claude CLI using stdin (like teams-support-analyst bot)
            # This approach is more reliable and matches the pattern from the support bot
            result = subprocess.run(
                [self.claude_cmd, '--print'],
                input=prompt,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )

            if result.returncode != 0:
                raise RuntimeError(f"Claude CLI error: {result.stderr}")

            output = result.stdout.strip()

            # Remove markdown code blocks if present
            if '```json' in output:
                output = output.split('```json')[1].split('```')[0].strip()
            elif '```' in output:
                output = output.split('```')[1].split('```')[0].strip()

            # Parse JSON response
            response = json.loads(output)

            logger.info(f"Generated SQL: {response.get('sql', 'N/A')[:100]}")
            return response

        except subprocess.TimeoutExpired:
            logger.error("Claude CLI timed out")
            raise RuntimeError("Claude CLI timed out after 30 seconds")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response: {e}")
            logger.error(f"Raw output: {output[:500]}")
            raise RuntimeError(f"Failed to parse Claude response: {e}")

        except Exception as e:
            logger.error(f"Claude CLI error: {e}")
            raise

    def _format_schema(self, schema_info: Dict[str, Any]) -> str:
        """Format schema information for the prompt."""
        lines = []

        for table in schema_info.get("tables", []):
            lines.append(f"\nTable: {table['name']}")
            lines.append("  Columns:")
            for col in table.get("columns", []):
                pk_marker = " (PK)" if col.get("primary_key") else ""
                nullable = "NULL" if col.get("nullable") else "NOT NULL"
                lines.append(f"    - {col['name']}: {col['type']} {nullable}{pk_marker}")

            if table.get("foreign_keys"):
                lines.append("  Foreign Keys:")
                for fk in table["foreign_keys"]:
                    fk_cols = ", ".join(fk["columns"])
                    ref_table = fk["referred_table"]
                    ref_cols = ", ".join(fk["referred_columns"])
                    lines.append(f"    - {fk_cols} -> {ref_table}({ref_cols})")

        return "\n".join(lines)

    def explain_query(self, sql: str) -> str:
        """Generate explanation using Claude CLI."""
        try:
            prompt = f"Explain this SQL query in simple terms:\n\n{sql}"

            result = subprocess.run(
                ['claude', prompt],
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode != 0:
                return "Unable to generate explanation"

            return result.stdout.strip()

        except Exception as e:
            logger.error(f"Query explanation error: {e}")
            return "Unable to generate explanation"


# Global Claude CLI client instance
try:
    claude_cli_client = ClaudeCLIClient()
except Exception as e:
    logger.warning(f"Claude CLI client not initialized: {e}")
    claude_cli_client = None
