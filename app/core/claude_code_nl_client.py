"""
Claude Code NL Client - Integration for Natural Language Query Processing

This client submits natural language questions to n8n webhooks, which store them
in a database queue. Claude Code then processes the queue manually, generating SQL,
executing queries, and creating natural language responses in English or Hebrew.

Flow:
1. FastAPI → Submit question to n8n webhook
2. n8n → Store in PostgreSQL queue
3. User tells Claude Code: "Process SQL queue"
4. Claude Code → Generate SQL, execute, create response
5. FastAPI → Poll n8n for results
6. Return natural language response to user
"""

import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import requests
from app.config import settings
from loguru import logger


class ClaudeCodeNLClient:
    """
    Client for natural language query processing via Claude Code.

    This client uses n8n webhooks as middleware between FastAPI and Claude Code.
    Responses include natural language explanations in the same language as the question.

    Attributes:
        n8n_webhook_url: URL for submitting questions
        n8n_status_url: URL for checking status
        n8n_pending_url: URL for listing pending queries
        poll_interval: Seconds between status checks
        max_wait_seconds: Maximum time to wait for processing
    """

    def __init__(self):
        """Initialize Claude Code NL client with configuration from settings."""
        self.n8n_webhook_url = getattr(
            settings, 'n8n_webhook_url',
            'http://localhost:5678/webhook/nl-query'
        )
        self.n8n_status_url = getattr(
            settings, 'n8n_status_url',
            'http://localhost:5678/webhook/nl-status'
        )
        self.n8n_pending_url = getattr(
            settings, 'n8n_pending_url',
            'http://localhost:5678/webhook/pending-queries'
        )
        self.poll_interval = getattr(settings, 'claude_code_poll_interval', 5)
        self.max_wait_seconds = getattr(settings, 'claude_code_max_wait', 300)

        logger.info(f"Claude Code NL Client initialized")
        logger.info(f"  Webhook URL: {self.n8n_webhook_url}")
        logger.info(f"  Status URL: {self.n8n_status_url}")
        logger.info(f"  Poll interval: {self.poll_interval}s")
        logger.info(f"  Max wait: {self.max_wait_seconds}s")

    def generate_sql_with_nl_response(
        self,
        question: str,
        schema_info: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Submit natural language question and wait for SQL generation + execution + NL response.

        This method:
        1. Submits question to n8n webhook
        2. Gets job_id back immediately
        3. Polls for completion (Claude Code must process queue)
        4. Returns full result with natural language response

        Args:
            question: Natural language question in English or Hebrew
            schema_info: Optional schema information (fetched from n8n if not provided)
            user_id: User identifier for tracking

        Returns:
            Dict containing:
                - job_id: Unique job identifier
                - status: completed, failed, or timeout
                - question: Original question
                - language: Detected language (en/he)
                - answer: Natural language response in same language
                - sql_executed: SQL query that was run
                - query_type: READ, WRITE_SAFE, WRITE_RISKY, or ADMIN
                - risk_level: low, medium, high, or critical
                - execution_allowed: Whether query was allowed to execute
                - error: Error message if any
                - processing_time_seconds: Time taken to process

        Raises:
            TimeoutError: If Claude Code doesn't process within max_wait_seconds
            requests.RequestException: If network/HTTP errors occur
        """
        # Step 1: Submit question to n8n
        logger.info(f"Submitting question: {question[:100]}...")

        try:
            submit_response = requests.post(
                self.n8n_webhook_url,
                json={
                    "question": question,
                    "user_id": user_id
                },
                timeout=10
            )
            submit_response.raise_for_status()
            submit_data = submit_response.json()

        except requests.RequestException as e:
            logger.error(f"Failed to submit question to n8n: {e}")
            raise RuntimeError(
                f"Failed to submit question: {e}. "
                f"Ensure n8n is running at {self.n8n_webhook_url}"
            )

        job_id = submit_data.get('job_id')
        if not job_id:
            raise RuntimeError("No job_id returned from n8n webhook")

        logger.info(f"Question submitted successfully (job_id: {job_id})")
        logger.info(f"Status URL: {self.n8n_status_url}/{job_id}")
        logger.info(f"⏳ Waiting for Claude Code to process...")
        logger.info(f"💡 Tell Claude Code: 'Process SQL queue'")

        # Step 2: Poll for completion
        start_time = time.time()
        poll_count = 0

        while (time.time() - start_time) < self.max_wait_seconds:
            poll_count += 1

            try:
                status_response = requests.get(
                    f"{self.n8n_status_url}/{job_id}",
                    timeout=10
                )
                status_response.raise_for_status()
                status_data = status_response.json()

            except requests.RequestException as e:
                logger.warning(f"Failed to check status (attempt {poll_count}): {e}")
                time.sleep(self.poll_interval)
                continue

            status = status_data.get('status')
            logger.debug(f"Poll #{poll_count}: Status = {status}")

            if status == 'completed':
                elapsed = time.time() - start_time
                logger.info(f"✅ Processing completed in {elapsed:.1f}s")

                return {
                    'job_id': job_id,
                    'status': 'completed',
                    'question': status_data.get('question'),
                    'language': self._detect_language(question),
                    'answer': status_data.get('answer'),
                    'sql_executed': status_data.get('sql_executed'),
                    'query_type': status_data.get('query_type'),
                    'risk_level': status_data.get('risk_level'),
                    'execution_allowed': status_data.get('execution_allowed'),
                    'error': None,
                    'processing_time_seconds': status_data.get('processing_time_seconds', elapsed)
                }

            elif status == 'failed':
                logger.error(f"❌ Processing failed: {status_data.get('error')}")

                return {
                    'job_id': job_id,
                    'status': 'failed',
                    'question': status_data.get('question'),
                    'language': self._detect_language(question),
                    'answer': status_data.get('answer'),  # Error message in correct language
                    'sql_executed': status_data.get('sql_executed'),
                    'query_type': status_data.get('query_type'),
                    'risk_level': status_data.get('risk_level'),
                    'execution_allowed': status_data.get('execution_allowed'),
                    'error': status_data.get('error'),
                    'processing_time_seconds': status_data.get('processing_time_seconds')
                }

            elif status == 'processing':
                logger.info(f"⚙️  Claude Code is processing (poll #{poll_count})...")

            # Still pending or processing, wait and retry
            time.sleep(self.poll_interval)

        # Timeout
        elapsed = time.time() - start_time
        logger.error(f"⏱️  Processing timed out after {elapsed:.1f}s ({poll_count} polls)")

        language = self._detect_language(question)
        timeout_message = (
            "עיבוד השאילתה חרג מזמן ההמתנה. אנא נסה שוב מאוחר יותר."
            if language == 'he'
            else "Query processing timed out. Please try again later."
        )

        raise TimeoutError(
            f"SQL generation timed out after {self.max_wait_seconds} seconds. "
            f"Claude Code may not have processed the request yet. "
            f"Job ID: {job_id}. "
            f"You can check status at: {self.n8n_status_url}/{job_id}"
        )

    def check_queue_status(self) -> Dict[str, Any]:
        """
        Check the current queue status (how many pending, processing, etc.).

        Returns:
            Dict with queue statistics:
                - total_pending: Number of pending requests
                - oldest_age_seconds: Age of oldest pending request
                - requests: List of pending requests
                - recommendation: Action recommendation
        """
        try:
            response = requests.get(self.n8n_pending_url, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Failed to check queue status: {e}")
            return {
                'total_pending': -1,
                'error': str(e),
                'recommendation': 'Unable to connect to n8n'
            }

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check status of a specific job by job_id.

        Args:
            job_id: Job identifier returned from submit

        Returns:
            Dict with job details and current status
        """
        try:
            response = requests.get(f"{self.n8n_status_url}/{job_id}", timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Failed to get job status for {job_id}: {e}")
            return {
                'job_id': job_id,
                'status': 'unknown',
                'error': str(e)
            }

    @staticmethod
    def _detect_language(text: str) -> str:
        """
        Detect if text is Hebrew or English.

        Args:
            text: Text to analyze

        Returns:
            'he' for Hebrew, 'en' for English
        """
        import re
        hebrew_pattern = re.compile(r'[\u0590-\u05FF]')
        return 'he' if hebrew_pattern.search(text) else 'en'

    def generate_sql(self, question: str, schema_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy method for compatibility with existing code.

        This provides the same interface as OpenAIClient.generate_sql()
        but returns natural language responses instead of just SQL.

        Args:
            question: Natural language question
            schema_info: Database schema (ignored, fetched by n8n)

        Returns:
            Dict compatible with existing code:
                - sql: Generated SQL query
                - query_type: READ, WRITE_SAFE, etc.
                - risk_level: low, medium, high, critical
                - explanation: Natural language explanation
                - estimated_impact: Impact description
                - warnings: List of warnings
        """
        result = self.generate_sql_with_nl_response(question, schema_info)

        # Map to legacy format
        return {
            'sql': result.get('sql_executed', ''),
            'query_type': result.get('query_type', 'READ'),
            'risk_level': result.get('risk_level', 'low'),
            'explanation': result.get('answer', ''),  # Natural language response
            'estimated_impact': f"Query processed in {result.get('processing_time_seconds', 0):.1f}s",
            'warnings': [result.get('error')] if result.get('error') else []
        }


# Create singleton instance
claude_code_nl_client = ClaudeCodeNLClient()
