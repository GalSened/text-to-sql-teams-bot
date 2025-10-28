"""Test Claude CLI client import"""
try:
    from app.core.claude_cli_client import claude_cli_client
    print(f"✓ Claude CLI client imported successfully")
    print(f"  Client: {claude_cli_client}")

    if claude_cli_client:
        print("  Client is initialized and ready")
    else:
        print("  Client is None - initialization failed")

except Exception as e:
    print(f"✗ Failed to import Claude CLI client: {e}")
    import traceback
    traceback.print_exc()
