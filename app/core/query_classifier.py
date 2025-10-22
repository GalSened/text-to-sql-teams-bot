"""
Query classification and validation module.
"""
import re
from typing import Tuple, List

from app.models.query_models import QueryType, RiskLevel
from loguru import logger


class QueryClassifier:
    """Classifies and validates SQL queries."""

    # SQL keywords for different operation types
    READ_KEYWORDS = ["SELECT", "SHOW", "DESCRIBE", "EXPLAIN", "WITH"]
    WRITE_SAFE_KEYWORDS = ["INSERT"]
    WRITE_RISKY_KEYWORDS = ["UPDATE", "DELETE", "TRUNCATE", "MERGE"]
    ADMIN_KEYWORDS = ["CREATE", "DROP", "ALTER", "GRANT", "REVOKE", "EXEC", "EXECUTE"]

    def classify_query(self, sql: str) -> Tuple[QueryType, RiskLevel]:
        """
        Classify SQL query by type and assess risk level.

        Args:
            sql: SQL query string

        Returns:
            Tuple of (QueryType, RiskLevel)
        """
        sql_upper = sql.strip().upper()

        # Remove comments
        sql_upper = self._remove_comments(sql_upper)

        # Get first significant keyword
        first_keyword = self._get_first_keyword(sql_upper)

        # Classify by type
        if first_keyword in self.READ_KEYWORDS:
            return QueryType.READ, RiskLevel.LOW

        elif first_keyword in self.ADMIN_KEYWORDS:
            return QueryType.ADMIN, RiskLevel.CRITICAL

        elif first_keyword in self.WRITE_RISKY_KEYWORDS:
            # Check if UPDATE/DELETE has WHERE clause
            if first_keyword in ["UPDATE", "DELETE"]:
                has_where = self._has_where_clause(sql_upper)
                if has_where:
                    # Check if WHERE clause is specific enough
                    if self._is_where_clause_safe(sql_upper):
                        return QueryType.WRITE_SAFE, RiskLevel.MEDIUM
                    else:
                        return QueryType.WRITE_RISKY, RiskLevel.HIGH
                else:
                    # No WHERE clause - very risky
                    return QueryType.WRITE_RISKY, RiskLevel.CRITICAL
            else:
                # TRUNCATE, MERGE
                return QueryType.WRITE_RISKY, RiskLevel.HIGH

        elif first_keyword in self.WRITE_SAFE_KEYWORDS:
            # INSERT operations
            return QueryType.WRITE_SAFE, RiskLevel.MEDIUM

        else:
            # Unknown operation - treat as risky
            logger.warning(f"Unknown SQL operation: {first_keyword}")
            return QueryType.WRITE_RISKY, RiskLevel.HIGH

    def validate_query(self, sql: str, query_type: QueryType) -> Tuple[bool, List[str]]:
        """
        Validate SQL query and return validation status with warnings.

        Args:
            sql: SQL query string
            query_type: Classified query type

        Returns:
            Tuple of (is_valid, warnings_list)
        """
        warnings = []

        # Basic syntax validation
        if not sql.strip():
            return False, ["Empty query"]

        sql_upper = sql.strip().upper()

        # Check for dangerous patterns
        dangerous_patterns = [
            (r";\s*DROP", "Possible SQL injection: DROP after semicolon"),
            (r";\s*DELETE", "Multiple statements detected with DELETE"),
            (r"--", "SQL comment detected"),
            (r"/\*.*\*/", "Block comment detected"),
        ]

        for pattern, warning in dangerous_patterns:
            if re.search(pattern, sql_upper):
                warnings.append(warning)

        # Type-specific validation
        if query_type == QueryType.WRITE_RISKY:
            if not self._has_where_clause(sql_upper):
                warnings.append("WARNING: No WHERE clause - will affect ALL rows!")

        # Check for very broad WHERE clauses
        if "WHERE 1=1" in sql_upper or "WHERE 1 = 1" in sql_upper:
            warnings.append("WHERE 1=1 detected - effectively no filtering")

        # Validate has required keywords
        if query_type == QueryType.READ and "SELECT" not in sql_upper:
            return False, ["Invalid SELECT query"]

        return True, warnings

    def _remove_comments(self, sql: str) -> str:
        """Remove SQL comments from query."""
        # Remove single-line comments
        sql = re.sub(r"--.*$", "", sql, flags=re.MULTILINE)
        # Remove block comments
        sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
        return sql

    def _get_first_keyword(self, sql: str) -> str:
        """Get the first SQL keyword from query."""
        # Remove leading whitespace and get first word
        words = sql.split()
        if words:
            return words[0].upper()
        return ""

    def _has_where_clause(self, sql: str) -> bool:
        """Check if query has a WHERE clause."""
        return "WHERE" in sql.upper()

    def _is_where_clause_safe(self, sql: str) -> bool:
        """
        Determine if WHERE clause is specific enough.

        A safe WHERE clause should reference specific values,
        not overly broad conditions.
        """
        where_match = re.search(r"WHERE\s+(.+?)(?:ORDER BY|GROUP BY|;|$)", sql, re.IGNORECASE | re.DOTALL)

        if not where_match:
            return False

        where_clause = where_match.group(1).strip()

        # Unsafe patterns
        unsafe_patterns = [
            r"1\s*=\s*1",  # WHERE 1=1
            r".*IS NOT NULL",  # WHERE column IS NOT NULL (too broad)
            r".*>\s*0",  # WHERE id > 0 (too broad)
        ]

        for pattern in unsafe_patterns:
            if re.search(pattern, where_clause, re.IGNORECASE):
                return False

        # Safe if it has specific value comparisons
        has_specific_value = bool(re.search(r"=\s*['\"]?\w+['\"]?", where_clause))

        return has_specific_value

    def estimate_impact(self, sql: str, query_type: QueryType) -> str:
        """
        Estimate the impact of the query.

        Args:
            sql: SQL query
            query_type: Query type

        Returns:
            Human-readable impact description
        """
        if query_type == QueryType.READ:
            return "Read operation - no data will be modified"

        sql_upper = sql.upper()

        # Extract table name
        table_name = self._extract_table_name(sql_upper)

        if query_type == QueryType.WRITE_RISKY:
            if not self._has_where_clause(sql_upper):
                return f"⚠️ CRITICAL: Will affect ALL rows in table '{table_name}'"
            else:
                return f"⚠️ HIGH RISK: Will modify multiple rows in table '{table_name}'"

        elif query_type == QueryType.WRITE_SAFE:
            if "INSERT" in sql_upper:
                return f"Will insert new row(s) into table '{table_name}'"
            else:
                return f"Will modify specific row(s) in table '{table_name}'"

        elif query_type == QueryType.ADMIN:
            if "DROP" in sql_upper:
                return f"🚨 CRITICAL: Will permanently delete {table_name}"
            elif "CREATE" in sql_upper:
                return f"Will create new database object: {table_name}"
            elif "ALTER" in sql_upper:
                return f"Will modify structure of {table_name}"
            else:
                return "Administrative operation"

        return "Unknown impact"

    def _extract_table_name(self, sql: str) -> str:
        """Extract table name from SQL query."""
        # Try different patterns
        patterns = [
            r"FROM\s+(\w+)",
            r"UPDATE\s+(\w+)",
            r"INSERT\s+INTO\s+(\w+)",
            r"DELETE\s+FROM\s+(\w+)",
            r"DROP\s+TABLE\s+(\w+)",
            r"CREATE\s+TABLE\s+(\w+)",
            r"ALTER\s+TABLE\s+(\w+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, sql, re.IGNORECASE)
            if match:
                return match.group(1)

        return "unknown"


# Global classifier instance
query_classifier = QueryClassifier()
