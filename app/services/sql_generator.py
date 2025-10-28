"""
Intelligent SQL Generator - Pattern-based with Claude CLI fallback
Generates SQL queries from natural language questions
"""
import re
from typing import Dict, Any, Optional, List
from loguru import logger
from app.config import settings


class IntelligentSQLGenerator:
    """
    Pattern-based SQL generation with fallback to AI.

    Architecture:
    1. Pattern matching for common queries (fast, no cost)
    2. Template-based generation for standard patterns
    3. AI API fallback for complex queries (future)
    """

    def __init__(self):
        """Initialize SQL generator with patterns."""
        self.patterns = self._load_patterns()
        self.use_ai_fallback = settings.use_claude_cli

        # Import Claude CLI client if enabled
        self.claude_cli_client = None
        if self.use_ai_fallback:
            try:
                from app.core.claude_cli_client import claude_cli_client
                self.claude_cli_client = claude_cli_client
                logger.info("✓ Claude CLI fallback enabled for complex queries")
            except Exception as e:
                logger.warning(f"Claude CLI not available: {e}")
                self.use_ai_fallback = False

    def _load_patterns(self) -> List[Dict]:
        """
        Load SQL generation patterns.

        Each pattern has:
        - keywords: List of words to match (English/Hebrew)
        - sql_template: SQL template with placeholders
        - confidence: How confident we are in this pattern
        """
        return [
            # COUNT patterns
            {
                'keywords': ['how many', 'count', 'כמה', 'ספור', 'מספר'],
                'pattern_type': 'COUNT',
                'sql_template': 'SELECT COUNT(*) as count FROM {table} {where}',
                'confidence': 0.9
            },
            # SUM patterns
            {
                'keywords': ['total', 'sum', 'סכום', 'סה"כ'],
                'pattern_type': 'SUM',
                'sql_template': 'SELECT SUM({column}) as total FROM {table} {where}',
                'confidence': 0.85
            },
            # AVERAGE patterns
            {
                'keywords': ['average', 'mean', 'ממוצע'],
                'pattern_type': 'AVG',
                'sql_template': 'SELECT AVG({column}) as average FROM {table} {where}',
                'confidence': 0.85
            },
            # LIST/SELECT patterns
            {
                'keywords': ['list', 'show', 'get', 'רשימה', 'הצג', 'הראה'],
                'pattern_type': 'SELECT',
                'sql_template': 'SELECT TOP {limit} * FROM {table} {where} {orderby}',
                'confidence': 0.8
            },
            # RECENT patterns (time-based)
            {
                'keywords': ['recent', 'last', 'latest', 'אחרונים', 'לאחרונה'],
                'pattern_type': 'RECENT',
                'sql_template': 'SELECT TOP {limit} * FROM {table} WHERE {date_column} >= DATEADD({unit}, -{value}, GETDATE()) {orderby}',
                'confidence': 0.75
            },
            # GROUP BY patterns
            {
                'keywords': ['by', 'group', 'per', 'לפי', 'קבוצה'],
                'pattern_type': 'GROUP',
                'sql_template': 'SELECT {group_column}, COUNT(*) as count FROM {table} {where} GROUP BY {group_column}',
                'confidence': 0.7
            },
        ]

    def detect_pattern(self, question: str) -> Optional[Dict]:
        """Detect which pattern best matches the question."""
        question_lower = question.lower()

        best_match = None
        best_score = 0

        for pattern in self.patterns:
            # Count matching keywords
            matches = sum(1 for kw in pattern['keywords'] if kw in question_lower)

            if matches > 0:
                score = matches * pattern['confidence']
                if score > best_score:
                    best_score = score
                    best_match = pattern

        return best_match if best_score > 0.5 else None

    def extract_entities(self, question: str) -> Dict[str, Any]:
        """
        Extract entities from question.

        Entities:
        - table: Table name to query
        - column: Column to aggregate/filter
        - value: Value for filtering
        - limit: Result limit
        - date_column: Date column for time filters
        - unit: Time unit (day, week, month)
        """
        entities = {
            'table': None,
            'column': None,
            'where': '',
            'limit': 100,
            'date_column': 'created_at',
            'unit': 'day',
            'value': 1,
            'orderby': '',
            'group_column': None
        }

        # Extract table name (WeSign-specific tables)
        table_mappings = {
            # English keywords -> WeSign table
            'companies': 'Companies',
            'company': 'Companies',
            'contacts': 'Contacts',
            'contact': 'Contacts',
            'documents': 'Documents',
            'document': 'Documents',
            'document collections': 'DocumentCollections',
            'collections': 'DocumentCollections',
            'groups': 'Groups',
            'group': 'Groups',
            'contact groups': 'ContactsGroups',
            'configurations': 'ActiveDirectoryConfigurations',
            'configuration': 'ActiveDirectoryConfigurations',
            'active directory': 'ActiveDirectoryConfigurations',
            'logs': 'Logs',
            'log': 'Logs',
            'licenses': 'AvailableLicenses',
            'license': 'AvailableLicenses',
            'signers': 'CompanySigner1Details',
            'signer': 'CompanySigner1Details',
            'messages': 'CompanyMessages',
            'message': 'CompanyMessages',
        }

        # Check for table matches
        question_lower = question.lower()
        for keyword, table in table_mappings.items():
            if keyword in question_lower:
                entities['table'] = table
                break

        # Hebrew table mappings
        hebrew_tables = {
            'חברות': 'Companies',
            'חברה': 'Companies',
            'אנשי קשר': 'Contacts',
            'קשר': 'Contacts',
            'מסמכים': 'Documents',
            'מסמך': 'Documents',
            'אוספים': 'DocumentCollections',
            'קבוצות': 'Groups',
            'קבוצה': 'Groups',
            'תצורות': 'ActiveDirectoryConfigurations',
            'תצורה': 'ActiveDirectoryConfigurations',
            'לוגים': 'Logs',
            'רישיונות': 'AvailableLicenses',
            'חותמים': 'CompanySigner1Details',
            'הודעות': 'CompanyMessages',
        }
        for hebrew, table in hebrew_tables.items():
            if hebrew in question:
                entities['table'] = table
                break

        # Extract time period
        if 'last month' in question.lower() or 'בחודש שעבר' in question:
            entities['unit'] = 'month'
            entities['value'] = 1
        elif 'last week' in question.lower() or 'בשבוע שעבר' in question:
            entities['unit'] = 'week'
            entities['value'] = 1
        elif 'last year' in question.lower() or 'בשנה שעברה' in question:
            entities['unit'] = 'year'
            entities['value'] = 1
        elif 'today' in question.lower() or 'היום' in question:
            entities['unit'] = 'day'
            entities['value'] = 0

        # Extract numeric values
        numbers = re.findall(r'\d+', question)
        if numbers:
            entities['value'] = int(numbers[0])

        return entities

    def generate_from_pattern(self, pattern: Dict, entities: Dict) -> str:
        """Generate SQL from matched pattern and entities."""
        sql = pattern['sql_template']

        # Fill in placeholders
        for key, value in entities.items():
            placeholder = f'{{{key}}}'
            if placeholder in sql:
                sql = sql.replace(placeholder, str(value))

        return sql

    def generate_sql(
        self,
        question: str,
        language: str = 'en',
        schema_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate SQL from natural language question.

        Args:
            question: Natural language question
            language: Question language (en/he)
            schema_info: Optional database schema information

        Returns:
            Dict with: success, sql, confidence, method
        """
        logger.info(f"Generating SQL for: {question} (language: {language})")

        try:
            # Step 1: Detect pattern
            pattern = self.detect_pattern(question)

            if not pattern:
                logger.warning("No pattern matched")
                logger.warning(f"  use_ai_fallback={self.use_ai_fallback}, claude_cli_client={self.claude_cli_client}, schema_info={'present' if schema_info else 'missing'}")

                # Try Claude CLI fallback for complex queries
                if self.use_ai_fallback and self.claude_cli_client and schema_info:
                    logger.info("→ Using Claude CLI for complex query...")
                    return self.generate_with_ai(question, schema_info)
                else:
                    if not self.use_ai_fallback:
                        logger.warning("  Claude CLI fallback is disabled (use_ai_fallback=False)")
                    if not self.claude_cli_client:
                        logger.warning("  Claude CLI client not available")
                    if not schema_info:
                        logger.warning("  Schema info not provided")

                    return {
                        'success': False,
                        'error': 'Could not understand the question. Please rephrase or ask something like: "How many companies are in the system?"',
                        'sql': None,
                        'confidence': 0,
                        'method': 'no_match'
                    }

            logger.info(f"Matched pattern: {pattern['pattern_type']} (confidence: {pattern['confidence']})")

            # Step 2: Extract entities
            entities = self.extract_entities(question)

            if not entities['table']:
                return {
                    'success': False,
                    'error': 'Could not identify which table to query. Please mention a table name like "customers", "orders", etc.',
                    'sql': None,
                    'confidence': 0,
                    'method': 'no_table'
                }

            logger.info(f"Extracted entities: {entities}")

            # Step 3: Generate SQL
            sql = self.generate_from_pattern(pattern, entities)

            logger.success(f"Generated SQL: {sql}")

            # ═══════════════════════════════════════════════════════════
            # SECURITY: READ-ONLY MODE - Block non-SELECT queries
            # ═══════════════════════════════════════════════════════════
            if not self._is_read_only_query(sql):
                logger.warning(f"SECURITY BLOCK: Non-SELECT query blocked: {sql}")
                return {
                    'success': False,
                    'error': 'The bot only supports read queries (SELECT)\nהבוט תומך רק בשאילתות קריאה (SELECT)',
                    'sql': None,
                    'confidence': 0,
                    'method': 'security_block'
                }

            return {
                'success': True,
                'sql': sql,
                'confidence': pattern['confidence'],
                'method': 'pattern_matching',
                'pattern_type': pattern['pattern_type'],
                'entities': entities
            }

        except Exception as e:
            logger.error(f"SQL generation error: {e}")
            return {
                'success': False,
                'error': f'Failed to generate SQL: {str(e)}',
                'sql': None,
                'confidence': 0,
                'method': 'error'
            }

    def generate_with_ai(self, question: str, schema_info: Dict) -> Dict[str, Any]:
        """
        Generate SQL using local Claude CLI for complex queries.

        This is used as a fallback when pattern matching doesn't work.
        No API keys needed - uses local Claude Code CLI.
        """
        try:
            if not self.claude_cli_client:
                return {
                    'success': False,
                    'error': 'Claude CLI not available. Please ensure Claude Code is installed.',
                    'sql': None,
                    'confidence': 0,
                    'method': 'ai_not_available'
                }

            logger.info("Calling Claude CLI for complex query...")
            result = self.claude_cli_client.generate_sql(question, schema_info)

            # SECURITY: Check Claude CLI generated SQL is also read-only
            sql = result.get('sql', '')
            if not self._is_read_only_query(sql):
                logger.warning(f"SECURITY BLOCK: Claude CLI generated non-SELECT query: {sql}")
                return {
                    'success': False,
                    'error': 'The bot only supports read queries (SELECT)\nהבוט תומך רק בשאילתות קריאה (SELECT)',
                    'sql': None,
                    'confidence': 0,
                    'method': 'security_block'
                }

            # Claude CLI returns: {sql, query_type, risk_level, explanation}
            return {
                'success': True,
                'sql': sql,
                'confidence': 0.85,  # AI-generated, high confidence
                'method': 'claude_cli',
                'pattern_type': 'AI_GENERATED',
                'query_type': result.get('query_type', 'READ'),
                'risk_level': result.get('risk_level', 'low'),
                'explanation': result.get('explanation', '')
            }

        except Exception as e:
            logger.error(f"Claude CLI error: {e}")
            return {
                'success': False,
                'error': f'Claude CLI failed: {str(e)}',
                'sql': None,
                'confidence': 0,
                'method': 'ai_error'
            }

    def _is_read_only_query(self, sql: str) -> bool:
        """
        Check if SQL query is read-only (SELECT only).

        Returns True if query is SELECT, False for any write operation.
        """
        if not sql:
            return False

        # Remove leading/trailing whitespace
        sql_clean = sql.strip().upper()

        # Remove SQL comments
        sql_clean = re.sub(r'--.*$', '', sql_clean, flags=re.MULTILINE)
        sql_clean = re.sub(r'/\*.*?\*/', '', sql_clean, flags=re.DOTALL)

        # Get first keyword
        first_word = sql_clean.split()[0] if sql_clean.split() else ''

        # Only allow SELECT and WITH (for CTEs that lead to SELECT)
        allowed_keywords = ['SELECT', 'WITH']

        if first_word not in allowed_keywords:
            logger.warning(f"Non-SELECT query detected: starts with '{first_word}'")
            return False

        # Additional check: ensure no dangerous keywords anywhere
        dangerous_keywords = [
            'UPDATE', 'DELETE', 'INSERT', 'DROP', 'CREATE', 'ALTER',
            'TRUNCATE', 'EXEC', 'EXECUTE', 'MERGE', 'GRANT', 'REVOKE'
        ]

        for keyword in dangerous_keywords:
            if keyword in sql_clean:
                logger.warning(f"Dangerous keyword '{keyword}' found in query")
                return False

        return True


# Global instance
intelligent_sql_generator = IntelligentSQLGenerator()
