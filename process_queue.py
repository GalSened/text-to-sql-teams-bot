#!/usr/bin/env python3
"""
SQL Queue Processor
Processes pending natural language queries from the PostgreSQL queue
"""

import os
import json
import psycopg2
from psycopg2.extras import Json, DictCursor
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pyodbc
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.devtest')

# Database connection strings
QUEUE_DB_CONFIG = {
    'host': os.getenv('QUEUE_DB_HOST', 'localhost'),
    'port': int(os.getenv('QUEUE_DB_PORT', 5432)),
    'database': os.getenv('QUEUE_DB_NAME', 'text_to_sql_queue'),
    'user': os.getenv('QUEUE_DB_USER', 'postgres'),
    'password': os.getenv('QUEUE_DB_PASSWORD', 'postgres')
}

TARGET_DB_CONFIG = {
    'driver': os.getenv('DB_DRIVER', 'ODBC Driver 18 for SQL Server'),
    'server': os.getenv('DB_SERVER', 'localhost'),
    'port': os.getenv('DB_PORT', '1433'),
    'database': os.getenv('DB_NAME', 'TestDB'),
    'user': os.getenv('DB_USER', 'sa'),
    'password': os.getenv('DB_PASSWORD', ''),
    'trusted_connection': os.getenv('DB_TRUSTED_CONNECTION', 'no')
}

ENVIRONMENT = os.getenv('DEPLOYMENT_ENVIRONMENT', 'devtest')
BATCH_SIZE = int(os.getenv('BATCH_PROCESSING_SIZE', 10))


class QueryClassifier:
    """Classifies SQL queries by type and risk level"""

    @staticmethod
    def classify_query(sql: str) -> Tuple[str, str]:
        """
        Returns (query_type, risk_level)
        query_type: READ, WRITE_SAFE, WRITE_RISKY, ADMIN
        risk_level: low, medium, high, critical
        """
        sql_upper = sql.upper().strip()

        # ADMIN operations
        admin_keywords = ['CREATE', 'DROP', 'ALTER', 'TRUNCATE', 'GRANT', 'REVOKE']
        if any(sql_upper.startswith(kw) for kw in admin_keywords):
            return 'ADMIN', 'critical'

        # READ operations
        if sql_upper.startswith('SELECT'):
            # Check complexity for risk assessment
            if ' JOIN ' in sql_upper or ' UNION ' in sql_upper:
                return 'READ', 'medium'
            return 'READ', 'low'

        # WRITE operations
        write_keywords = ['INSERT', 'UPDATE', 'DELETE']
        for keyword in write_keywords:
            if sql_upper.startswith(keyword):
                # Check if it has WHERE clause (safer)
                if ' WHERE ' in sql_upper:
                    return 'WRITE_SAFE', 'medium'
                else:
                    # No WHERE clause = affects all rows
                    return 'WRITE_RISKY', 'high'

        # Unknown type
        return 'READ', 'low'

    @staticmethod
    def is_execution_allowed(query_type: str, environment: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Returns (allowed, error_message, error_type)
        Production: Only READ queries allowed
        DevTest: All queries allowed
        """
        if environment == 'prod' and query_type != 'READ':
            error_msg = f"{query_type} operations are not allowed in production. Only SELECT queries are permitted."
            return False, error_msg, 'environment_restriction'

        return True, None, None


class NaturalLanguageGenerator:
    """Generates natural language responses in English or Hebrew"""

    @staticmethod
    def generate_response(
        question: str,
        language: str,
        sql: str,
        query_type: str,
        results: Optional[List[Dict]] = None,
        row_count: int = 0,
        error_message: Optional[str] = None,
        execution_allowed: bool = True
    ) -> str:
        """Generate natural language response based on query results"""

        # Error responses
        if not execution_allowed:
            if language == 'he':
                return f"פעולת {query_type} זו אינה מותרת בסביבת ייצור. רק שאילתות SELECT מותרות בסביבת הייצור למען הבטיחות."
            else:
                return f"This {query_type} operation is not allowed in production. Only SELECT queries are permitted in the production environment for safety."

        if error_message:
            if language == 'he':
                return f"אירעה שגיאה בעיבוד בקשתך: {error_message}"
            else:
                return f"An error occurred while processing your request: {error_message}"

        # Success responses
        if query_type == 'READ':
            if row_count == 0:
                if language == 'he':
                    return "לא נמצאו תוצאות התואמות את הקריטריונים שלך."
                else:
                    return "No results found matching your criteria."

            # Check if it's a COUNT query
            if results and len(results) > 0:
                first_result = results[0]
                if len(first_result) == 1:
                    # Single column result - might be COUNT
                    col_name = list(first_result.keys())[0]
                    if 'count' in col_name.lower() or 'total' in col_name.lower():
                        count_value = first_result[col_name]
                        if language == 'he':
                            return f"נמצאו {count_value} תוצאות."
                        else:
                            return f"Found {count_value} results."

            # Generic multi-row results
            if language == 'he':
                return f"נמצאו {row_count} תוצאות. הנה הפרטים."
            else:
                return f"Found {row_count} results. Here are the details."

        # WRITE operations
        elif query_type in ['WRITE_SAFE', 'WRITE_RISKY']:
            if language == 'he':
                return f"הפעולה הושלמה בהצלחה. {row_count} שורות הושפעו."
            else:
                return f"Operation completed successfully. {row_count} rows affected."

        # ADMIN operations
        elif query_type == 'ADMIN':
            if language == 'he':
                return f"פעולת ניהול הושלמה בהצלחה."
            else:
                return f"Administrative operation completed successfully."

        # Default
        if language == 'he':
            return "השאילתה בוצעה בהצלחה."
        else:
            return "Query executed successfully."


class SQLQueueProcessor:
    """Main processor for SQL queue"""

    def __init__(self):
        self.classifier = QueryClassifier()
        self.nl_generator = NaturalLanguageGenerator()
        self.queue_conn = None
        self.target_conn = None

    def connect_to_queue_db(self):
        """Connect to PostgreSQL queue database"""
        try:
            self.queue_conn = psycopg2.connect(**QUEUE_DB_CONFIG)
            return True
        except Exception as e:
            print(f"❌ Failed to connect to queue database: {e}")
            return False

    def connect_to_target_db(self):
        """Connect to SQL Server target database"""
        try:
            conn_str = (
                f"DRIVER={{{TARGET_DB_CONFIG['driver']}}};"
                f"SERVER={TARGET_DB_CONFIG['server']},{TARGET_DB_CONFIG['port']};"
                f"DATABASE={TARGET_DB_CONFIG['database']};"
                f"UID={TARGET_DB_CONFIG['user']};"
                f"PWD={TARGET_DB_CONFIG['password']};"
                f"TrustServerCertificate=yes;"
            )
            self.target_conn = pyodbc.connect(conn_str, timeout=30)
            return True
        except Exception as e:
            print(f"⚠️  Failed to connect to target database: {e}")
            print("    Will continue processing but queries cannot be executed")
            return False

    def fetch_pending_requests(self, limit: int = BATCH_SIZE) -> List[Dict]:
        """Fetch pending requests from queue"""
        try:
            with self.queue_conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT
                        job_id,
                        question,
                        schema_info,
                        environment,
                        language,
                        user_id,
                        created_at
                    FROM sql_queue
                    WHERE status = 'pending'
                    ORDER BY created_at ASC
                    LIMIT %s
                """, (limit,))

                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            print(f"❌ Error fetching pending requests: {e}")
            return []

    def generate_sql(self, question: str, schema_info: Optional[Dict]) -> str:
        """
        Generate SQL query from natural language question.
        This is a placeholder - in practice, this would use an AI model.
        """
        # For demo purposes, return a simple SELECT
        # In production, this would call OpenAI/Claude to generate SQL

        # Simple pattern matching for demo
        question_lower = question.lower()

        if 'count' in question_lower or 'how many' in question_lower or 'כמה' in question_lower:
            if 'companies' in question_lower or 'חברות' in question_lower:
                if 'last month' in question_lower or 'בחודש שעבר' in question_lower:
                    return "SELECT COUNT(*) as company_count FROM companies WHERE created_date >= DATEADD(month, -1, GETDATE())"
                elif '3 month' in question_lower or '3 חודשים' in question_lower:
                    return "SELECT COUNT(*) as company_count FROM companies WHERE created_date >= DATEADD(month, -3, GETDATE())"
                else:
                    return "SELECT COUNT(*) as company_count FROM companies"

        if 'show' in question_lower or 'list' in question_lower or 'הראה' in question_lower:
            if 'customers' in question_lower or 'לקוחות' in question_lower:
                if 'top' in question_lower:
                    return "SELECT TOP 10 * FROM customers ORDER BY total_revenue DESC"
                return "SELECT * FROM customers"

        # Default - need more context
        return "-- Unable to generate SQL: question unclear or missing schema information"

    def execute_sql(self, sql: str) -> Tuple[Optional[List[Dict]], int, Optional[str]]:
        """
        Execute SQL query on target database
        Returns (results, row_count, error_message)
        """
        if not self.target_conn:
            return None, 0, "Not connected to target database"

        try:
            cursor = self.target_conn.cursor()
            start_time = datetime.now()

            cursor.execute(sql)

            # Get results
            if cursor.description:
                # SELECT query with results
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                results = [dict(zip(columns, row)) for row in rows]
                row_count = len(results)
            else:
                # UPDATE/INSERT/DELETE
                results = None
                row_count = cursor.rowcount
                self.target_conn.commit()

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return results, row_count, None

        except Exception as e:
            if self.target_conn:
                self.target_conn.rollback()
            return None, 0, str(e)

    def update_request_status(
        self,
        job_id: str,
        status: str,
        sql_query: Optional[str] = None,
        query_type: Optional[str] = None,
        risk_level: Optional[str] = None,
        execution_allowed: Optional[bool] = None,
        query_results: Optional[List[Dict]] = None,
        rows_affected: Optional[int] = None,
        execution_time_ms: Optional[float] = None,
        natural_language_response: Optional[str] = None,
        error_message: Optional[str] = None,
        error_type: Optional[str] = None
    ):
        """Update request status in queue database"""
        try:
            with self.queue_conn.cursor() as cursor:
                update_fields = ['status = %s']
                params = [status]

                if sql_query is not None:
                    update_fields.append('sql_query = %s')
                    params.append(sql_query)

                if query_type is not None:
                    update_fields.append('query_type = %s')
                    params.append(query_type)

                if risk_level is not None:
                    update_fields.append('risk_level = %s')
                    params.append(risk_level)

                if execution_allowed is not None:
                    update_fields.append('execution_allowed = %s')
                    params.append(execution_allowed)

                if query_results is not None:
                    update_fields.append('query_results = %s')
                    params.append(Json(query_results))

                if rows_affected is not None:
                    update_fields.append('rows_affected = %s')
                    params.append(rows_affected)

                if execution_time_ms is not None:
                    update_fields.append('execution_time_ms = %s')
                    params.append(execution_time_ms)

                if natural_language_response is not None:
                    update_fields.append('natural_language_response = %s')
                    params.append(natural_language_response)

                if error_message is not None:
                    update_fields.append('error_message = %s')
                    params.append(error_message)

                if error_type is not None:
                    update_fields.append('error_type = %s')
                    params.append(error_type)

                if status == 'completed':
                    update_fields.append('completed_at = NOW()')
                    update_fields.append('executed_at = NOW()')
                elif status == 'failed':
                    update_fields.append('completed_at = NOW()')

                if sql_query is not None:
                    update_fields.append('sql_generated_at = NOW()')

                update_fields.append('total_processing_time_ms = EXTRACT(EPOCH FROM (NOW() - created_at)) * 1000')

                params.append(job_id)

                sql = f"""
                    UPDATE sql_queue
                    SET {', '.join(update_fields)}
                    WHERE job_id = %s
                """

                cursor.execute(sql, params)
                self.queue_conn.commit()

        except Exception as e:
            print(f"❌ Error updating request {job_id}: {e}")
            self.queue_conn.rollback()

    def process_request(self, request: Dict) -> Dict:
        """Process a single request"""
        job_id = str(request['job_id'])
        question = request['question']
        schema_info = request.get('schema_info')
        environment = request.get('environment', 'devtest')
        language = request.get('language', 'en')

        print(f"\n{'='*60}")
        print(f"Processing Job: {job_id}")
        print(f"Question ({language}): {question}")

        result = {
            'job_id': job_id,
            'question': question,
            'language': language,
            'status': 'failed'
        }

        try:
            # Mark as processing
            self.update_request_status(job_id, 'processing')

            # Generate SQL
            print("📝 Generating SQL...")
            sql = self.generate_sql(question, schema_info)
            print(f"   SQL: {sql}")

            # Check if SQL generation failed
            if sql.startswith('--'):
                error_msg = "Unable to generate SQL from question"
                nl_response = self.nl_generator.generate_response(
                    question, language, sql, 'READ',
                    error_message=error_msg,
                    execution_allowed=False
                )
                self.update_request_status(
                    job_id,
                    'failed',
                    sql_query=sql,
                    error_message=error_msg,
                    error_type='sql_generation_failed',
                    natural_language_response=nl_response
                )
                result['status'] = 'failed'
                result['error'] = error_msg
                print(f"❌ {error_msg}")
                return result

            # Classify query
            query_type, risk_level = self.classifier.classify_query(sql)
            print(f"🏷️  Type: {query_type}, Risk: {risk_level}")

            # Check if execution is allowed
            execution_allowed, error_msg, error_type = self.classifier.is_execution_allowed(
                query_type, environment
            )

            if not execution_allowed:
                print(f"🚫 Blocked: {error_msg}")
                nl_response = self.nl_generator.generate_response(
                    question, language, sql, query_type,
                    execution_allowed=False
                )
                self.update_request_status(
                    job_id,
                    'failed',
                    sql_query=sql,
                    query_type=query_type,
                    risk_level=risk_level,
                    execution_allowed=False,
                    error_message=error_msg,
                    error_type=error_type,
                    natural_language_response=nl_response
                )
                result['status'] = 'blocked'
                result['error'] = error_msg
                return result

            # Execute SQL
            print("⚙️  Executing SQL...")
            query_results, rows_affected, exec_error = self.execute_sql(sql)

            if exec_error:
                print(f"❌ Execution error: {exec_error}")
                nl_response = self.nl_generator.generate_response(
                    question, language, sql, query_type,
                    error_message=exec_error
                )
                self.update_request_status(
                    job_id,
                    'failed',
                    sql_query=sql,
                    query_type=query_type,
                    risk_level=risk_level,
                    execution_allowed=True,
                    error_message=exec_error,
                    error_type='sql_execution_error',
                    natural_language_response=nl_response
                )
                result['status'] = 'failed'
                result['error'] = exec_error
                return result

            # Generate natural language response
            print(f"✅ Success: {rows_affected} rows")
            nl_response = self.nl_generator.generate_response(
                question, language, sql, query_type,
                results=query_results,
                row_count=rows_affected
            )
            print(f"💬 Response: {nl_response}")

            # Update database with success
            self.update_request_status(
                job_id,
                'completed',
                sql_query=sql,
                query_type=query_type,
                risk_level=risk_level,
                execution_allowed=True,
                query_results=query_results,
                rows_affected=rows_affected,
                natural_language_response=nl_response
            )

            result['status'] = 'completed'
            result['sql'] = sql
            result['rows'] = rows_affected
            result['response'] = nl_response

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            self.update_request_status(
                job_id,
                'failed',
                error_message=str(e),
                error_type='unexpected_error'
            )
            result['status'] = 'failed'
            result['error'] = str(e)

        return result

    def process_batch(self):
        """Process a batch of pending requests"""
        print(f"\n{'='*60}")
        print(f"SQL Queue Processor - {ENVIRONMENT.upper()} Environment")
        print(f"{'='*60}\n")

        # Connect to databases
        print("🔌 Connecting to databases...")
        if not self.connect_to_queue_db():
            return
        print("   ✅ Connected to queue database")

        if self.connect_to_target_db():
            print("   ✅ Connected to target database")
        else:
            print("   ⚠️  Target database not available - will process but not execute")

        # Fetch pending requests
        print(f"\n📥 Fetching pending requests (batch size: {BATCH_SIZE})...")
        requests = self.fetch_pending_requests()

        if not requests:
            print("   No pending requests in queue")
            return

        print(f"   Found {len(requests)} pending request(s)")

        # Process each request
        results = {
            'completed': 0,
            'blocked': 0,
            'failed': 0
        }

        for request in requests:
            result = self.process_request(request)
            results[result['status']] += 1

        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Completed: {results['completed']}")
        print(f"🚫 Blocked: {results['blocked']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"{'='*60}\n")

    def close(self):
        """Close database connections"""
        if self.queue_conn:
            self.queue_conn.close()
        if self.target_conn:
            self.target_conn.close()


def main():
    """Main entry point"""
    processor = SQLQueueProcessor()
    try:
        processor.process_batch()
    finally:
        processor.close()


if __name__ == '__main__':
    main()
