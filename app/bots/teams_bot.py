"""
Teams Bot for Text-to-SQL
Handles conversations and routes queries to the SQL queue
"""

from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes, Attachment
from typing import Dict, List
import uuid
import json
import psycopg2
from psycopg2.extras import Json as PgJson, DictCursor
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv('.env.devtest')

# Database configuration
QUEUE_DB_CONFIG = {
    'host': os.getenv('QUEUE_DB_HOST', 'localhost'),
    'port': int(os.getenv('QUEUE_DB_PORT', 5432)),
    'database': os.getenv('QUEUE_DB_NAME', 'text_to_sql_queue'),
    'user': os.getenv('QUEUE_DB_USER', 'postgres'),
    'password': os.getenv('QUEUE_DB_PASSWORD', 'postgres')
}

class TextToSQLBot(ActivityHandler):
    """
    Teams bot that handles text-to-SQL queries.
    Routes questions to PostgreSQL queue for Claude Code processing.
    """

    def __init__(self):
        super().__init__()
        self.pending_confirmations = {}  # Track pending confirmations

    def detect_language(self, text: str) -> str:
        """Detect if text is English or Hebrew"""
        if not text:
            return 'en'

        hebrew_chars = sum(1 for c in text if '\u0590' <= c <= '\u05FF')
        return 'he' if hebrew_chars > len(text) * 0.3 else 'en'

    async def on_message_activity(self, turn_context: TurnContext):
        """
        Handle incoming messages from Teams users
        """
        text = turn_context.activity.text.strip()
        user_id = turn_context.activity.from_property.id
        user_name = turn_context.activity.from_property.name or "User"

        # Detect language
        language = self.detect_language(text)

        # Handle commands
        if text.startswith('/'):
            await self.handle_command(turn_context, text, language)
            return

        # Check for confirmation responses
        if text.lower() in ['yes', 'no', 'כן', 'לא', 'confirm', 'cancel']:
            await self.handle_confirmation(turn_context, text, user_id, language)
            return

        # Regular question - add to queue
        await self.handle_question(turn_context, text, user_id, user_name, language)

    async def handle_command(self, turn_context: TurnContext, command: str, language: str):
        """Handle bot commands"""
        command_lower = command.lower()

        if command_lower == '/help':
            await self.send_help_message(turn_context, language)

        elif command_lower == '/status':
            await self.send_status(turn_context, language)

        elif command_lower == '/history':
            await self.send_history(turn_context, turn_context.activity.from_property.id, language)

        elif command_lower == '/schema':
            await self.send_schema_info(turn_context, language)

        elif command_lower == '/examples':
            await self.send_examples(turn_context, language)

        else:
            msg = "Unknown command" if language == 'en' else "פקודה לא מוכרת"
            await turn_context.send_activity(f"{msg}. /help")

    async def handle_question(self, turn_context: TurnContext, question: str, user_id: str, user_name: str, language: str):
        """
        Handle a user question by adding it to the queue
        """
        try:
            # Send "processing" message
            processing_msg = "⏳ Processing your question..." if language == 'en' else "⏳ מעבד את השאילתה..."
            await turn_context.send_activity(processing_msg)

            # Get schema info
            schema_info = self.get_schema_info()

            # Insert into queue
            job_id = str(uuid.uuid4())
            environment = os.getenv('DEPLOYMENT_ENVIRONMENT', 'devtest')

            conn = psycopg2.connect(**QUEUE_DB_CONFIG)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO sql_queue (
                    job_id,
                    question,
                    schema_info,
                    environment,
                    language,
                    status,
                    user_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                job_id,
                question,
                PgJson(schema_info),
                environment,
                language,
                'pending',
                f"{user_id}:{user_name}"
            ))

            conn.commit()
            cursor.close()
            conn.close()

            # Send confirmation with adaptive card
            card = self.create_query_submitted_card(job_id, question, language)
            await turn_context.send_activity(MessageFactory.attachment(card))

            # Notify about manual processing
            if language == 'en':
                note = "📝 Note: Claude Code will process this query. Check back in a moment!"
            else:
                note = "📝 הערה: Claude Code יעבד את השאילתה. בדוק שוב בעוד רגע!"

            await turn_context.send_activity(note)

        except Exception as e:
            error_msg = f"❌ Error: {str(e)}" if language == 'en' else f"❌ שגיאה: {str(e)}"
            await turn_context.send_activity(error_msg)

    async def handle_confirmation(self, turn_context: TurnContext, response: str, user_id: str, language: str):
        """Handle confirmation for write operations"""
        # Check if user has pending confirmation
        if user_id not in self.pending_confirmations:
            msg = "No pending confirmation" if language == 'en' else "אין אישור ממתין"
            await turn_context.send_activity(msg)
            return

        # Get pending query
        job_id = self.pending_confirmations[user_id]
        confirmed = response.lower() in ['yes', 'כן', 'confirm']

        # Update queue with confirmation
        try:
            conn = psycopg2.connect(**QUEUE_DB_CONFIG)
            cursor = conn.cursor()

            if confirmed:
                cursor.execute("""
                    UPDATE sql_queue
                    SET status = 'confirmed'
                    WHERE job_id = %s
                """, (job_id,))

                msg = "✅ Confirmed! Processing..." if language == 'en' else "✅ אושר! מעבד..."
            else:
                cursor.execute("""
                    UPDATE sql_queue
                    SET status = 'cancelled'
                    WHERE job_id = %s
                """, (job_id,))

                msg = "❌ Cancelled" if language == 'en' else "❌ בוטל"

            conn.commit()
            cursor.close()
            conn.close()

            await turn_context.send_activity(msg)

            # Remove from pending
            del self.pending_confirmations[user_id]

        except Exception as e:
            error_msg = f"❌ Error: {str(e)}" if language == 'en' else f"❌ שגיאה: {str(e)}"
            await turn_context.send_activity(error_msg)

    async def send_help_message(self, turn_context: TurnContext, language: str):
        """Send help message"""
        if language == 'en':
            help_text = """
📚 **Text-to-SQL Bot Help**

**How to Use:**
Just ask your question in plain English or Hebrew!

**Example Questions:**
• "How many companies are in the system?"
• "Show all contacts from last month"
• "List active documents"
• "Count documents by status"

**Commands:**
• `/help` - Show this help
• `/status` - Check queue status
• `/history` - Your recent queries
• `/schema` - View available tables
• `/examples` - See more examples

**Tips:**
✓ Be specific about date ranges
✓ Mention table names if you know them
✓ Use "top N" to limit results
"""
        else:
            help_text = """
📚 **עזרה לבוט Text-to-SQL**

**איך להשתמש:**
פשוט שאל את השאילתה שלך בעברית או אנגלית!

**דוגמאות לשאילתות:**
• "כמה חברות יש במערכת?"
• "הצג את כל אנשי הקשר מהחודש שעבר"
• "רשום מסמכים פעילים"
• "ספור מסמכים לפי סטטוס"

**פקודות:**
• `/help` - הצג עזרה זו
• `/status` - בדוק סטטוס התור
• `/history` - השאילתות האחרונות שלך
• `/schema` - הצג טבלאות זמינות
• `/examples` - צפה בדוגמאות נוספות

**טיפים:**
✓ היה ספציפי לגבי טווחי תאריכים
✓ ציין שמות טבלאות אם אתה יודע אותם
✓ השתמש ב"top N" להגבלת תוצאות
"""

        await turn_context.send_activity(help_text)

    async def send_status(self, turn_context: TurnContext, language: str):
        """Send queue status"""
        try:
            conn = psycopg2.connect(**QUEUE_DB_CONFIG)
            cursor = conn.cursor(cursor_factory=DictCursor)

            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM sql_queue
                WHERE created_at > NOW() - INTERVAL '1 hour'
                GROUP BY status
                ORDER BY status
            """)

            results = cursor.fetchall()
            cursor.close()
            conn.close()

            if language == 'en':
                status_text = "📊 **Queue Status (Last Hour)**\n\n"
                for row in results:
                    status_text += f"• {row['status'].title()}: {row['count']}\n"
            else:
                status_text = "📊 **סטטוס תור (שעה אחרונה)**\n\n"
                for row in results:
                    status_text += f"• {row['status']}: {row['count']}\n"

            await turn_context.send_activity(status_text)

        except Exception as e:
            error_msg = f"❌ Error: {str(e)}" if language == 'en' else f"❌ שגיאה: {str(e)}"
            await turn_context.send_activity(error_msg)

    async def send_history(self, turn_context: TurnContext, user_id: str, language: str):
        """Send user's query history"""
        try:
            conn = psycopg2.connect(**QUEUE_DB_CONFIG)
            cursor = conn.cursor(cursor_factory=DictCursor)

            cursor.execute("""
                SELECT
                    question,
                    status,
                    natural_language_response,
                    created_at
                FROM sql_queue
                WHERE user_id LIKE %s
                ORDER BY created_at DESC
                LIMIT 5
            """, (f"{user_id}%",))

            results = cursor.fetchall()
            cursor.close()
            conn.close()

            if not results:
                msg = "No query history found" if language == 'en' else "לא נמצאו שאילתות"
                await turn_context.send_activity(msg)
                return

            if language == 'en':
                history_text = "📝 **Your Recent Queries**\n\n"
                for i, row in enumerate(results, 1):
                    history_text += f"{i}. {row['question'][:50]}...\n"
                    history_text += f"   Status: {row['status']} | {row['created_at'].strftime('%Y-%m-%d %H:%M')}\n\n"
            else:
                history_text = "📝 **השאילתות האחרונות שלך**\n\n"
                for i, row in enumerate(results, 1):
                    history_text += f"{i}. {row['question'][:50]}...\n"
                    history_text += f"   סטטוס: {row['status']} | {row['created_at'].strftime('%Y-%m-%d %H:%M')}\n\n"

            await turn_context.send_activity(history_text)

        except Exception as e:
            error_msg = f"❌ Error: {str(e)}" if language == 'en' else f"❌ שגיאה: {str(e)}"
            await turn_context.send_activity(error_msg)

    async def send_examples(self, turn_context: TurnContext, language: str):
        """Send example questions"""
        if language == 'en':
            examples = """
💡 **Example Questions**

**Counting & Aggregation:**
• "How many companies joined last month?"
• "Count total documents"
• "Count active directory configurations"

**Filtering & Searching:**
• "Show companies created this year"
• "List all contacts"
• "Find documents by status"

**Top N Queries:**
• "Top 10 companies"
• "Show 5 most recent documents"
• "Latest 20 contact entries"

**Time-based:**
• "Documents from last week"
• "Companies created today"
• "Contacts added this year"
"""
        else:
            examples = """
💡 **דוגמאות לשאילתות**

**ספירה וצבירה:**
• "כמה חברות הצטרפו בחודש שעבר?"
• "ספור סך המסמכים"
• "ספור תצורות Active Directory"

**סינון וחיפוש:**
• "הצג חברות שנוצרו השנה"
• "רשום את כל אנשי הקשר"
• "מצא מסמכים לפי סטטוס"

**שאילתות Top N:**
• "10 החברות המובילות"
• "הצג 5 המסמכים האחרונים"
• "20 רשומות אנשי הקשר האחרונות"

**מבוססות זמן:**
• "מסמכים מהשבוע שעבר"
• "חברות שנוצרו היום"
• "אנשי קשר שנוספו השנה"
"""

        await turn_context.send_activity(examples)

    async def send_schema_info(self, turn_context: TurnContext, language: str):
        """Send database schema information"""
        schema = self.get_schema_info()

        if language == 'en':
            schema_text = "📊 **Available Tables**\n\n"
            for table in schema.get('tables', []):
                schema_text += f"• **{table['name']}**\n"
                for col in table.get('columns', [])[:5]:  # Show first 5 columns
                    schema_text += f"  - {col['name']} ({col['type']})\n"
                schema_text += "\n"
        else:
            schema_text = "📊 **טבלאות זמינות**\n\n"
            for table in schema.get('tables', []):
                schema_text += f"• **{table['name']}**\n"
                for col in table.get('columns', [])[:5]:
                    schema_text += f"  - {col['name']} ({col['type']})\n"
                schema_text += "\n"

        await turn_context.send_activity(schema_text)

    def get_schema_info(self) -> Dict:
        """Get database schema information"""
        # WeSign database schema
        return {
            "tables": [
                {
                    "name": "Companies",
                    "columns": [
                        {"name": "Id", "type": "INT"},
                        {"name": "CompanyName", "type": "NVARCHAR"},
                        {"name": "Email", "type": "NVARCHAR"},
                        {"name": "CreatedDate", "type": "DATETIME"},
                        {"name": "IsActive", "type": "BIT"}
                    ]
                },
                {
                    "name": "Contacts",
                    "columns": [
                        {"name": "Id", "type": "INT"},
                        {"name": "FirstName", "type": "NVARCHAR"},
                        {"name": "LastName", "type": "NVARCHAR"},
                        {"name": "Email", "type": "NVARCHAR"},
                        {"name": "Phone", "type": "NVARCHAR"},
                        {"name": "CompanyId", "type": "INT"}
                    ]
                },
                {
                    "name": "Documents",
                    "columns": [
                        {"name": "Id", "type": "INT"},
                        {"name": "DocumentName", "type": "NVARCHAR"},
                        {"name": "DocumentType", "type": "NVARCHAR"},
                        {"name": "Status", "type": "NVARCHAR"},
                        {"name": "CreatedDate", "type": "DATETIME"},
                        {"name": "CompanyId", "type": "INT"}
                    ]
                },
                {
                    "name": "DocumentCollections",
                    "columns": [
                        {"name": "Id", "type": "INT"},
                        {"name": "CollectionName", "type": "NVARCHAR"},
                        {"name": "Status", "type": "NVARCHAR"},
                        {"name": "CreatedDate", "type": "DATETIME"}
                    ]
                },
                {
                    "name": "ActiveDirectoryConfigurations",
                    "columns": [
                        {"name": "Id", "type": "INT"},
                        {"name": "ConfigName", "type": "NVARCHAR"},
                        {"name": "Domain", "type": "NVARCHAR"},
                        {"name": "IsEnabled", "type": "BIT"}
                    ]
                },
                {
                    "name": "Groups",
                    "columns": [
                        {"name": "Id", "type": "INT"},
                        {"name": "GroupName", "type": "NVARCHAR"},
                        {"name": "Description", "type": "NVARCHAR"},
                        {"name": "CreatedDate", "type": "DATETIME"}
                    ]
                },
                {
                    "name": "Logs",
                    "columns": [
                        {"name": "Id", "type": "INT"},
                        {"name": "LogLevel", "type": "NVARCHAR"},
                        {"name": "Message", "type": "NVARCHAR"},
                        {"name": "Timestamp", "type": "DATETIME"},
                        {"name": "UserId", "type": "INT"}
                    ]
                }
            ]
        }

    def create_query_submitted_card(self, job_id: str, question: str, language: str) -> Attachment:
        """Create Adaptive Card for query submitted"""
        if language == 'en':
            card_content = {
                "type": "AdaptiveCard",
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.4",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "✅ Query Submitted",
                        "weight": "bolder",
                        "size": "medium",
                        "color": "good"
                    },
                    {
                        "type": "TextBlock",
                        "text": question,
                        "wrap": True,
                        "separator": True
                    },
                    {
                        "type": "FactSet",
                        "facts": [
                            {"title": "Job ID", "value": job_id[:8]},
                            {"title": "Status", "value": "Pending"},
                            {"title": "Environment", "value": os.getenv('DEPLOYMENT_ENVIRONMENT', 'devtest')}
                        ]
                    }
                ]
            }
        else:
            card_content = {
                "type": "AdaptiveCard",
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.4",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "✅ שאילתה הוגשה",
                        "weight": "bolder",
                        "size": "medium",
                        "color": "good"
                    },
                    {
                        "type": "TextBlock",
                        "text": question,
                        "wrap": True,
                        "separator": True
                    },
                    {
                        "type": "FactSet",
                        "facts": [
                            {"title": "מזהה משימה", "value": job_id[:8]},
                            {"title": "סטטוס", "value": "ממתין"},
                            {"title": "סביבה", "value": os.getenv('DEPLOYMENT_ENVIRONMENT', 'devtest')}
                        ]
                    }
                ]
            }

        return Attachment(
            content_type="application/vnd.microsoft.card.adaptive",
            content=card_content
        )

    async def on_members_added_activity(
        self, members_added: List[ChannelAccount], turn_context: TurnContext
    ):
        """
        Handle new members (bot added to chat)
        """
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                # Detect language from Teams locale
                language = 'en'  # Default

                welcome_en = """
👋 **Welcome to Text-to-SQL Bot!**

I can help you query your database using natural language in English or Hebrew.

**Try asking:**
• "How many companies are in the system?"
• "Show all contacts"
• "List active documents"

Type `/help` for more information.
"""

                welcome_he = """
👋 **ברוכים הבאים לבוט Text-to-SQL!**

אני יכול לעזור לך לבצע שאילתות למסד הנתונים בעברית או אנגלית.

**נסה לשאול:**
• "כמה חברות יש במערכת?"
• "הצג את כל אנשי הקשר"
• "רשום מסמכים פעילים"

הקלד `/help` למידע נוסף.
"""

                await turn_context.send_activity(welcome_en)
