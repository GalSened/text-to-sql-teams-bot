"""
Intelligent SQL Generator - Pattern-based with AI-ready architecture
Generates SQL queries from natural language questions
"""
import re
from typing import Dict, Any, Optional, List
from loguru import logger


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
        self.use_ai_fallback = False  # Can enable later

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
                logger.warning("No pattern matched, using fallback")
                return {
                    'success': False,
                    'error': 'Could not understand the question. Please rephrase or ask something like: "How many customers joined last month?"',
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
        Generate SQL using AI API (Claude or OpenAI).

        Future implementation - for complex queries that don't match patterns.
        """
        # TODO: Implement AI API integration
        # 1. Format prompt with question + schema
        # 2. Call Claude API or OpenAI API
        # 3. Parse and validate SQL response
        # 4. Return result

        return {
            'success': False,
            'error': 'AI generation not implemented yet',
            'sql': None,
            'confidence': 0,
            'method': 'ai_not_available'
        }


# Global instance
intelligent_sql_generator = IntelligentSQLGenerator()
