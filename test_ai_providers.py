"""
Compare OpenAI and Claude side-by-side for SQL generation.
Run this to see which provider works better for your use case.
"""
import sys
import os
import json
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))


def test_provider(provider_name, client, question, schema):
    """Test a single provider."""
    print(f"\n{'='*60}")
    print(f"Testing: {provider_name.upper()}")
    print(f"{'='*60}")

    try:
        start_time = datetime.now()
        result = client.generate_sql(question, schema)
        duration = (datetime.now() - start_time).total_seconds()

        print(f"✅ Success ({duration:.2f}s)")
        print(f"\nSQL:")
        print(f"  {result['sql']}")
        print(f"\nQuery Type: {result['query_type']}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"\nExplanation:")
        print(f"  {result['explanation']}")

        if result.get('warnings'):
            print(f"\nWarnings:")
            for warning in result['warnings']:
                print(f"  ⚠️  {warning}")

        return {
            'success': True,
            'duration': duration,
            'result': result
        }

    except Exception as e:
        print(f"❌ Failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def run_comparison():
    """Run comparison between available providers."""
    print("="*60)
    print("AI PROVIDER COMPARISON TEST")
    print("="*60)

    # Sample question
    question = "Show me the top 10 customers by total purchase amount, including their name and total spent"

    # Sample schema (minimal)
    schema = {
        "tables": [
            {
                "name": "customers",
                "columns": [
                    {"name": "id", "type": "INT", "primary_key": True, "nullable": False},
                    {"name": "name", "type": "VARCHAR(100)", "nullable": False},
                    {"name": "email", "type": "VARCHAR(100)", "nullable": True}
                ]
            },
            {
                "name": "orders",
                "columns": [
                    {"name": "id", "type": "INT", "primary_key": True, "nullable": False},
                    {"name": "customer_id", "type": "INT", "nullable": False},
                    {"name": "total_amount", "type": "DECIMAL(10,2)", "nullable": False},
                    {"name": "order_date", "type": "DATETIME", "nullable": False}
                ],
                "foreign_keys": [
                    {
                        "columns": ["customer_id"],
                        "referred_table": "customers",
                        "referred_columns": ["id"]
                    }
                ]
            }
        ]
    }

    print(f"\nTest Question:")
    print(f"  {question}")
    print(f"\nSchema: customers, orders (with foreign key)")

    results = {}

    # Test Claude
    try:
        print("\n" + "="*60)
        print("Attempting to use CLAUDE")
        print("="*60)
        from app.core.claude_client import ClaudeClient
        claude = ClaudeClient()
        results['claude'] = test_provider('Claude', claude, question, schema)
    except Exception as e:
        print(f"❌ Claude not available: {e}")
        results['claude'] = {'success': False, 'error': str(e)}

    # Test OpenAI
    try:
        print("\n" + "="*60)
        print("Attempting to use OPENAI")
        print("="*60)
        from app.core.openai_client import OpenAIClient
        openai = OpenAIClient()
        results['openai'] = test_provider('OpenAI', openai, question, schema)
    except Exception as e:
        print(f"❌ OpenAI not available: {e}")
        results['openai'] = {'success': False, 'error': str(e)}

    # Summary
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)

    for provider, result in results.items():
        status = "✅ Working" if result['success'] else "❌ Failed"
        print(f"\n{provider.upper()}: {status}")

        if result['success']:
            print(f"  Duration: {result['duration']:.2f}s")
            print(f"  SQL: {result['result']['sql'][:60]}...")
        else:
            print(f"  Error: {result['error']}")

    # Recommendation
    print("\n" + "="*60)
    print("RECOMMENDATION")
    print("="*60)

    working_providers = [p for p, r in results.items() if r['success']]

    if 'claude' in working_providers:
        print("✅ Use CLAUDE (Recommended)")
        print("   - Better for complex SQL")
        print("   - Larger context window (200K)")
        print("   - More accurate with joins")
        print("   - Cost effective with Haiku model")
    elif 'openai' in working_providers:
        print("✅ Use OPENAI")
        print("   - Works well for simple queries")
        print("   - Widely supported")
    else:
        print("❌ No providers available!")
        print("   Configure ANTHROPIC_API_KEY or OPENAI_API_KEY in .env")

    print("\n" + "="*60)


def main():
    """Main entry point."""
    try:
        run_comparison()
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
