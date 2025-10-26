#!/usr/bin/env python3
"""
Background Worker Service - Automated Queue Processing
Runs 24/7 to automatically process text-to-SQL requests
"""
import asyncio
import time
import signal
import sys
from datetime import datetime
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from loguru import logger

from app.config import settings
from app.services.sql_generator import intelligent_sql_generator
from app.core.database import db_manager
from app.services.teams_notifier import send_proactive_message


class WorkerService:
    """Background worker for automated queue processing."""

    def __init__(self, poll_interval: int = 10):
        """
        Initialize worker service.

        Args:
            poll_interval: Seconds between queue checks (default: 10)
        """
        self.poll_interval = poll_interval
        self.running = False
        self.processed_count = 0
        self.error_count = 0

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info(f"Worker service initialized (poll_interval={poll_interval}s)")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def get_queue_connection(self):
        """Get connection to PostgreSQL queue database."""
        return psycopg2.connect(
            host=settings.queue_db_host,
            port=settings.queue_db_port,
            dbname=settings.queue_db_name,
            user=settings.queue_db_user,
            password=settings.queue_db_password
        )

    def fetch_pending_requests(self) -> list:
        """Fetch pending requests from queue."""
        try:
            with self.get_queue_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT *
                        FROM sql_queue
                        WHERE status = 'pending'
                        ORDER BY created_at ASC
                        LIMIT 10
                    """)
                    return cur.fetchall()
        except Exception as e:
            logger.error(f"Failed to fetch pending requests: {e}")
            return []

    def update_request_status(
        self,
        request_id: int,
        status: str,
        generated_sql: Optional[str] = None,
        result_data: Optional[str] = None,
        error_message: Optional[str] = None,
        rows_affected: Optional[int] = None,
        execution_time_ms: Optional[float] = None
    ):
        """Update request status in queue."""
        try:
            with self.get_queue_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE sql_queue
                        SET status = %s,
                            sql_query = COALESCE(%s, sql_query),
                            query_results = COALESCE(%s, query_results),
                            error_message = COALESCE(%s, error_message),
                            rows_affected = COALESCE(%s, rows_affected),
                            execution_time_ms = COALESCE(%s, execution_time_ms),
                            completed_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (
                        status,
                        generated_sql,
                        result_data,
                        error_message,
                        rows_affected,
                        execution_time_ms,
                        request_id
                    ))
                    conn.commit()
        except Exception as e:
            logger.error(f"Failed to update request {request_id}: {e}")

    def process_request(self, request: dict):
        """Process a single request from queue."""
        request_id = request['id']
        question = request['question']
        language = request.get('language', 'en')
        user_id = request.get('user_id')
        conversation_id = request.get('conversation_id')

        logger.info(f"Processing request {request_id}: {question[:50]}...")

        try:
            # Step 1: Generate SQL using intelligent generator
            logger.info(f"Generating SQL for: {question}")
            sql_result = intelligent_sql_generator.generate_sql(
                question=question,
                language=language
            )

            if not sql_result['success']:
                raise Exception(sql_result.get('error', 'SQL generation failed'))

            generated_sql = sql_result['sql']
            logger.info(f"Generated SQL: {generated_sql}")

            # Step 2: Execute SQL query
            logger.info("Executing SQL query...")
            results, rows_affected, execution_time = db_manager.execute_query(
                sql=generated_sql,
                fetch_results=True
            )

            logger.info(f"Query executed: {rows_affected} rows, {execution_time:.2f}ms")

            # Step 3: Format results
            import json
            result_data = json.dumps(results, default=str, ensure_ascii=False)

            # Step 4: Update database
            self.update_request_status(
                request_id=request_id,
                status='completed',
                generated_sql=generated_sql,
                result_data=result_data,
                rows_affected=rows_affected,
                execution_time_ms=execution_time
            )

            # Step 5: Send proactive Teams message with results (if Teams info available)
            if user_id and conversation_id:
                try:
                    asyncio.run(send_proactive_message(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        language=language,
                        question=question,
                        results=results,
                        rows_affected=rows_affected,
                        execution_time=execution_time
                    ))
                    logger.info("Teams notification sent successfully")
                except Exception as e:
                    logger.warning(f"Failed to send Teams notification: {e}")
            else:
                logger.info("Skipping Teams notification (no user_id/conversation_id)")

            self.processed_count += 1
            logger.success(f"Request {request_id} completed successfully")

        except Exception as e:
            logger.error(f"Failed to process request {request_id}: {e}")
            self.update_request_status(
                request_id=request_id,
                status='failed',
                error_message=str(e)
            )
            self.error_count += 1

    def run(self):
        """Main worker loop - runs continuously."""
        self.running = True
        logger.info("=" * 60)
        logger.info("🚀 Worker Service Started")
        logger.info(f"Poll Interval: {self.poll_interval}s")
        logger.info(f"Environment: {settings.deployment_environment}")
        logger.info("=" * 60)

        while self.running:
            try:
                # Fetch pending requests
                pending = self.fetch_pending_requests()

                if pending:
                    logger.info(f"Found {len(pending)} pending request(s)")

                    for request in pending:
                        if not self.running:
                            break
                        self.process_request(request)
                else:
                    # No pending requests, show status
                    if self.processed_count > 0 and self.processed_count % 10 == 0:
                        logger.info(
                            f"Status: {self.processed_count} processed, "
                            f"{self.error_count} errors"
                        )

                # Wait before next poll
                time.sleep(self.poll_interval)

            except KeyboardInterrupt:
                logger.info("Interrupted by user")
                break
            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                time.sleep(self.poll_interval)

        logger.info("=" * 60)
        logger.info("Worker Service Stopped")
        logger.info(f"Total Processed: {self.processed_count}")
        logger.info(f"Total Errors: {self.error_count}")
        logger.info("=" * 60)


def main():
    """Entry point for worker service."""
    import argparse

    parser = argparse.ArgumentParser(description='Text-to-SQL Background Worker')
    parser.add_argument(
        '--poll-interval',
        type=int,
        default=10,
        help='Seconds between queue checks (default: 10)'
    )
    parser.add_argument(
        '--fast',
        action='store_true',
        help='Fast mode: 5 second polling'
    )

    args = parser.parse_args()

    poll_interval = 5 if args.fast else args.poll_interval

    worker = WorkerService(poll_interval=poll_interval)

    try:
        worker.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
