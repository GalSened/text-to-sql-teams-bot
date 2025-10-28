"""Test if settings are loading correctly"""
from app.config import settings

print("Settings loaded:")
print(f"  use_claude_cli: {settings.use_claude_cli}")
print(f"  claude_cli_command: {settings.claude_cli_command}")
print(f"  anthropic_api_key: {settings.anthropic_api_key}")
print(f"  openai_api_key: {settings.openai_api_key}")
