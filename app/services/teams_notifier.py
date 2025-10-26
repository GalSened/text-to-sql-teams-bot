"""
Teams Proactive Messaging Service
Sends results back to users automatically
"""
import asyncio
from typing import List, Dict, Any
from botbuilder.schema import Activity, ActivityTypes, ConversationReference
from botbuilder.core import BotFrameworkAdapter
from loguru import logger

from app.config import settings


async def send_proactive_message(
    user_id: str,
    conversation_id: str,
    language: str,
    question: str,
    results: List[Dict[str, Any]],
    rows_affected: int,
    execution_time: float
):
    """
    Send proactive message to user with query results.

    Args:
        user_id: Teams user ID
        conversation_id: Teams conversation ID
        language: User's language (en/he)
        question: Original question
        results: Query results
        rows_affected: Number of rows
        execution_time: Execution time in ms
    """
    try:
        logger.info(f"Sending proactive message to {user_id} in conversation {conversation_id}")

        # Format results message based on language
        if language == 'he':
            message = _format_hebrew_results(question, results, rows_affected, execution_time)
        else:
            message = _format_english_results(question, results, rows_affected, execution_time)

        # TODO: Implement actual Teams proactive messaging
        # This requires:
        # 1. Storing conversation references when users first interact
        # 2. Using BotFrameworkAdapter.continue_conversation()
        # 3. Sending activity to stored conversation reference

        # For now, just log (user can check /history)
        logger.info(f"Proactive message prepared (actual sending pending implementation): {message[:100]}")

        # FUTURE: Implement full proactive messaging
        # await _send_to_teams(user_id, conversation_id, message)

    except Exception as e:
        logger.error(f"Failed to send proactive message: {e}")


def _format_english_results(
    question: str,
    results: List[Dict],
    rows_affected: int,
    execution_time: float
) -> str:
    """Format results in English."""
    message_lines = [
        f"✅ **Query Complete**",
        f"",
        f"**Question:** {question}",
        f"",
        f"**Results:** {rows_affected} row(s) found in {execution_time:.2f}ms",
        f""
    ]

    if results:
        # Show first few results
        message_lines.append("**Sample Data:**")
        for i, row in enumerate(results[:5], 1):
            row_str = ", ".join(f"{k}={v}" for k, v in row.items())
            message_lines.append(f"{i}. {row_str}")

        if len(results) > 5:
            message_lines.append(f"... and {len(results) - 5} more rows")
    else:
        message_lines.append("No rows returned.")

    message_lines.append("")
    message_lines.append("Use `/history` to see all your queries.")

    return "\n".join(message_lines)


def _format_hebrew_results(
    question: str,
    results: List[Dict],
    rows_affected: int,
    execution_time: float
) -> str:
    """Format results in Hebrew."""
    message_lines = [
        f"✅ **השאילתה הושלמה**",
        f"",
        f"**שאלה:** {question}",
        f"",
        f"**תוצאות:** {rows_affected} שורות נמצאו תוך {execution_time:.2f}ms",
        f""
    ]

    if results:
        # Show first few results
        message_lines.append("**דוגמת נתונים:**")
        for i, row in enumerate(results[:5], 1):
            row_str = ", ".join(f"{k}={v}" for k, v in row.items())
            message_lines.append(f"{i}. {row_str}")

        if len(results) > 5:
            message_lines.append(f"... ועוד {len(results) - 5} שורות")
    else:
        message_lines.append("לא נמצאו שורות.")

    message_lines.append("")
    message_lines.append("השתמש ב `/history` לראות את כל השאילתות שלך.")

    return "\n".join(message_lines)


async def _send_to_teams(user_id: str, conversation_id: str, message: str):
    """
    Actually send message to Teams (future implementation).

    Requires:
    1. ConversationReference storage when user first interacts
    2. Bot adapter configured with app credentials
    3. Proper permissions in Azure Bot
    """
    # FUTURE IMPLEMENTATION:
    # 1. Load conversation reference from database
    # 2. Create bot adapter
    # 3. Use adapter.continue_conversation() to send message
    pass
