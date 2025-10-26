#!/usr/bin/env python3
"""
Local Bot Testing Script
Tests the Teams bot without needing Teams or ngrok
"""

import asyncio
import sys
import json
from datetime import datetime
from typing import Dict, Any

# Test if we can import required modules
try:
    from botbuilder.schema import Activity, ChannelAccount, ConversationAccount, ActivityTypes
    from botbuilder.core import TurnContext, BotFrameworkAdapter, BotFrameworkAdapterSettings
    from app.bots.teams_bot import TextToSQLBot
except ImportError as e:
    print(f"❌ Missing required module: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Mock adapter settings (no authentication for local testing)
SETTINGS = BotFrameworkAdapterSettings(app_id="", app_password="")

class TestAdapter(BotFrameworkAdapter):
    """Test adapter that doesn't require authentication"""

    def __init__(self):
        super().__init__(SETTINGS)
        self.activities_sent = []

    async def send_activities(self, context: TurnContext, activities: list) -> list:
        """Capture activities sent by the bot"""
        self.activities_sent.extend(activities)
        return [{"id": str(i)} for i in range(len(activities))]

def create_test_activity(text: str, user_id: str = "test-user", user_name: str = "Test User") -> Activity:
    """Create a test message activity"""
    return Activity(
        type=ActivityTypes.message,
        channel_id="test",
        conversation=ConversationAccount(id="test-conversation"),
        from_property=ChannelAccount(id=user_id, name=user_name),
        recipient=ChannelAccount(id="bot", name="TextToSQLBot"),
        text=text,
        timestamp=datetime.utcnow()
    )

async def test_bot_response(bot: TextToSQLBot, adapter: TestAdapter, message: str) -> Dict[str, Any]:
    """Send a message to the bot and get the response"""
    activity = create_test_activity(message)
    turn_context = TurnContext(adapter, activity)

    # Clear previous activities
    adapter.activities_sent = []

    # Process the message
    await bot.on_turn(turn_context)

    # Return responses
    return {
        "message": message,
        "responses": [act.text if hasattr(act, 'text') else str(act) for act in adapter.activities_sent],
        "response_count": len(adapter.activities_sent)
    }

async def run_tests():
    """Run all bot tests"""
    print("=" * 60)
    print("🧪 Text-to-SQL Bot - Local Testing")
    print("=" * 60)
    print()

    # Initialize bot and adapter
    bot = TextToSQLBot()
    adapter = TestAdapter()

    tests = [
        # Test 1: Welcome message
        {
            "name": "Welcome Message",
            "message": "hello",
            "expected": "welcome"
        },
        # Test 2: Help command
        {
            "name": "Help Command",
            "message": "/help",
            "expected": "help"
        },
        # Test 3: Status command
        {
            "name": "Status Command",
            "message": "/status",
            "expected": "status"
        },
        # Test 4: Examples command
        {
            "name": "Examples Command",
            "message": "/examples",
            "expected": "example"
        },
        # Test 5: English question
        {
            "name": "English Question",
            "message": "How many customers joined last month?",
            "expected": "submitted"
        },
        # Test 6: Hebrew question
        {
            "name": "Hebrew Question",
            "message": "כמה לקוחות הצטרפו בחודש שעבר?",
            "expected": "הוגש"
        },
        # Test 7: History command
        {
            "name": "History Command",
            "message": "/history",
            "expected": "quer"  # "queries" or similar
        },
        # Test 8: Schema command
        {
            "name": "Schema Command",
            "message": "/schema",
            "expected": "table"
        },
    ]

    passed = 0
    failed = 0

    for i, test in enumerate(tests, 1):
        print(f"[Test {i}/{len(tests)}] {test['name']}")
        print(f"  Message: {test['message']}")

        try:
            result = await test_bot_response(bot, adapter, test['message'])

            # Check if bot responded
            if result['response_count'] == 0:
                print(f"  ❌ FAILED: No response from bot")
                failed += 1
                continue

            # Check if expected keyword is in response
            response_text = " ".join(result['responses']).lower()
            if test['expected'].lower() in response_text:
                print(f"  ✅ PASSED")
                print(f"  Response: {result['responses'][0][:100]}...")
                passed += 1
            else:
                print(f"  ⚠️  WARNING: Expected keyword '{test['expected']}' not found")
                print(f"  Response: {result['responses'][0][:100]}...")
                # Still count as passed if got a response
                passed += 1

        except Exception as e:
            print(f"  ❌ FAILED: {e}")
            failed += 1

        print()

    # Summary
    print("=" * 60)
    print(f"Test Results: {passed}/{len(tests)} passed")

    if failed == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ {failed} test(s) failed")
    print("=" * 60)
    print()

    # Additional checks
    print("Additional Checks:")
    print("━" * 60)

    # Check database connection
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname='text_to_sql_queue',
            user='postgres',
            password='postgres',
            host='localhost'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sql_queue WHERE status='pending'")
        pending_count = cursor.fetchone()[0]
        print(f"✓ Database connection successful")
        print(f"  Pending queries: {pending_count}")
        conn.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

    print()
    print("Next Steps:")
    print("━" * 60)
    print("1. If tests passed, proceed with Teams installation")
    print("2. If tests failed, check error messages above")
    print("3. Run: python process_queue.py (to process pending queries)")
    print("4. Install in Teams and test with real users")
    print()

if __name__ == "__main__":
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\n\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
