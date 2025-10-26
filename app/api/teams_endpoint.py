"""
FastAPI Endpoint for Microsoft Teams Bot
Handles incoming activities from Teams
"""

from fastapi import APIRouter, Request, Response, HTTPException
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity
from app.bots.teams_bot import TextToSQLBot
import traceback
import os

# Create router
router = APIRouter(prefix="/api", tags=["teams"])

# Bot Framework Adapter Settings
SETTINGS = BotFrameworkAdapterSettings(
    app_id=os.getenv("MICROSOFT_APP_ID", ""),  # Empty for local development
    app_password=os.getenv("MICROSOFT_APP_PASSWORD", "")
)

# Create adapter and bot
ADAPTER = BotFrameworkAdapter(SETTINGS)
BOT = TextToSQLBot()


async def on_error(context: TurnContext, error: Exception):
    """
    Error handler for the bot adapter
    """
    print(f"\n [on_turn_error] unhandled error: {error}", flush=True)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("Sorry, something went wrong. Please try again later.")


ADAPTER.on_turn_error = on_error


@router.post("/messages")
async def messages_endpoint(request: Request):
    """
    Main endpoint for receiving messages from Microsoft Teams

    This endpoint receives Activities from the Bot Connector Service
    and processes them through our bot logic.
    """
    # Verify the request is from Bot Framework
    auth_header = request.headers.get("Authorization", "")

    try:
        # Parse the incoming activity
        body = await request.json()
        activity = Activity().deserialize(body)

        # Process the activity through the adapter
        async def call_bot(turn_context: TurnContext):
            await BOT.on_turn(turn_context)

        await ADAPTER.process_activity(activity, auth_header, call_bot)

        return Response(status_code=200)

    except Exception as e:
        print(f"Error processing Teams activity: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/teams")
async def teams_health():
    """
    Health check endpoint for Teams bot
    """
    return {
        "status": "healthy",
        "bot": "TextToSQL Bot",
        "version": "1.0.0",
        "adapter": "ready"
    }


@router.post("/teams/webhook")
async def teams_webhook(request: Request):
    """
    Webhook endpoint for proactive messages and notifications
    Could be used for:
    - Sending query results after processing
    - Alerts and notifications
    - Status updates
    """
    body = await request.json()

    # Handle webhook events
    # This could be triggered by queue processor to notify users of completed queries

    return {"status": "received"}
