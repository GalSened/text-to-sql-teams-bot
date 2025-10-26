"""
Basic test script for Text-to-SQL application.
Tests core functionality without requiring a real database connection.
"""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all required modules can be imported."""
    print("=" * 60)
    print("Test 1: Module Imports")
    print("=" * 60)

    try:
        print("✓ Importing pydantic...")
        import pydantic

        print("✓ Importing fastapi...")
        import fastapi

        print("✓ Importing sqlalchemy...")
        import sqlalchemy

        print("✓ Importing openai...")
        import openai

        print("✓ Importing loguru...")
        from loguru import logger

        print("✓ Importing pyodbc...")
        import pyodbc

        print("✓ Importing pymssql...")
        import pymssql

        print("\n✅ All imports successful!")
        return True

    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        return False


def test_config():
    """Test configuration loading."""
    print("\n" + "=" * 60)
    print("Test 2: Configuration")
    print("=" * 60)

    try:
        # Check if .env file exists
        if not os.path.exists('.env'):
            print("⚠️  Warning: .env file not found")
            print("   Please create .env from .env.example")
            return False

        print("✓ .env file found")

        # Try to load config (will fail if required vars missing)
        from app.config import settings

        print(f"✓ App Name: {settings.app_name}")
        print(f"✓ App Version: {settings.app_version}")
        print(f"✓ Debug Mode: {settings.debug}")
        print(f"✓ OpenAI Model: {settings.openai_model}")
        print(f"✓ DB Server: {settings.db_server}")
        print(f"✓ DB Name: {settings.db_name}")
        print(f"✓ Max Rows Return: {settings.max_rows_return}")

        # Check if OpenAI key is set (don't print it!)
        if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
            print("✓ OpenAI API key configured")
        else:
            print("⚠️  OpenAI API key not configured or using default")

        print("\n✅ Configuration loaded successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Configuration failed: {e}")
        print("\nPlease ensure your .env file has all required variables:")
        print("  - OPENAI_API_KEY")
        print("  - DB_SERVER")
        print("  - DB_NAME")
        print("  - DB_USER")
        print("  - DB_PASSWORD")
        print("  - SECRET_KEY")
        return False


def test_models():
    """Test Pydantic models."""
    print("\n" + "=" * 60)
    print("Test 3: Data Models")
    print("=" * 60)

    try:
        from app.models.query_models import (
            QueryRequest,
            QueryType,
            RiskLevel,
            QueryResponse,
        )

        print("✓ Importing QueryRequest...")
        request = QueryRequest(
            question="Show me all customers",
            execute_immediately=True
        )
        print(f"  Question: {request.question}")
        print(f"  Execute immediately: {request.execute_immediately}")

        print("✓ Testing QueryType enum...")
        print(f"  Types: {[t.value for t in QueryType]}")

        print("✓ Testing RiskLevel enum...")
        print(f"  Levels: {[r.value for r in RiskLevel]}")

        print("\n✅ All models working!")
        return True

    except Exception as e:
        print(f"\n❌ Model test failed: {e}")
        return False


def test_query_classifier():
    """Test query classification logic."""
    print("\n" + "=" * 60)
    print("Test 4: Query Classifier")
    print("=" * 60)

    try:
        from app.core.query_classifier import query_classifier
        from app.models.query_models import QueryType, RiskLevel

        test_queries = [
            ("SELECT * FROM customers", QueryType.READ, RiskLevel.LOW),
            ("INSERT INTO customers VALUES (1, 'John')", QueryType.WRITE_SAFE, RiskLevel.MEDIUM),
            ("UPDATE customers SET status = 'active' WHERE id = 1", QueryType.WRITE_SAFE, RiskLevel.MEDIUM),
            ("DELETE FROM customers WHERE id = 1", QueryType.WRITE_SAFE, RiskLevel.MEDIUM),
            ("UPDATE customers SET status = 'inactive'", QueryType.WRITE_RISKY, RiskLevel.CRITICAL),
            ("DELETE FROM old_data", QueryType.WRITE_RISKY, RiskLevel.CRITICAL),
            ("DROP TABLE customers", QueryType.ADMIN, RiskLevel.CRITICAL),
            ("CREATE TABLE test (id INT)", QueryType.ADMIN, RiskLevel.CRITICAL),
        ]

        all_passed = True
        for sql, expected_type, expected_risk in test_queries:
            query_type, risk_level = query_classifier.classify_query(sql)

            passed = query_type == expected_type and risk_level == expected_risk
            symbol = "✓" if passed else "✗"

            print(f"\n{symbol} SQL: {sql[:50]}...")
            print(f"  Type: {query_type.value} (expected: {expected_type.value})")
            print(f"  Risk: {risk_level.value} (expected: {expected_risk.value})")

            if not passed:
                all_passed = False

        if all_passed:
            print("\n✅ Query classifier working correctly!")
        else:
            print("\n⚠️  Some classifications incorrect (may need tuning)")

        return all_passed

    except Exception as e:
        print(f"\n❌ Classifier test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_connection():
    """Test database connectivity."""
    print("\n" + "=" * 60)
    print("Test 5: Database Connection")
    print("=" * 60)

    try:
        from app.core.database import db_manager

        print("Attempting to connect to database...")

        if db_manager.test_connection():
            print("✅ Database connection successful!")

            # Try to get schema
            try:
                schema = db_manager.get_schema_info()
                print(f"✓ Found {len(schema.get('tables', []))} tables")

                if schema.get('tables'):
                    print("\nSample tables:")
                    for table in list(schema['tables'].keys())[:5]:
                        print(f"  - {table}")
            except Exception as e:
                print(f"⚠️  Could not retrieve schema: {e}")

            return True
        else:
            print("❌ Database connection failed")
            print("\nPossible issues:")
            print("  1. SQL Server not running")
            print("  2. Incorrect credentials in .env")
            print("  3. Network/firewall blocking connection")
            print("  4. ODBC driver not installed")
            return False

    except Exception as e:
        print(f"❌ Database test error: {e}")
        print("\nThis is expected if you don't have SQL Server configured yet.")
        print("You can still test other features without a database.")
        return False


def test_openai_client():
    """Test OpenAI client setup."""
    print("\n" + "=" * 60)
    print("Test 6: OpenAI Client")
    print("=" * 60)

    try:
        from app.core.openai_client import openai_client

        print("✓ OpenAI client initialized")

        # Check if API key is configured
        from app.config import settings
        if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
            print("✓ API key configured")
            print("⚠️  Note: Actual OpenAI calls will be tested when running the application")
            print("   (Test queries will be charged to your OpenAI account)")
        else:
            print("⚠️  OpenAI API key not configured")
            print("   Set OPENAI_API_KEY in .env to test SQL generation")

        return True

    except Exception as e:
        print(f"❌ OpenAI client test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and provide summary."""
    print("\n" + "=" * 60)
    print("TEXT-TO-SQL APPLICATION - BASIC TESTS")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Data Models", test_models()))
    results.append(("Query Classifier", test_query_classifier()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("OpenAI Client", test_openai_client()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    # Recommendations
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)

    if passed == total:
        print("✅ All tests passed! You're ready to start the application.")
        print("\nTo run the application:")
        print("  python -m app.main")
        print("  or")
        print("  uvicorn app.main:app --reload")
        print("\nThen open: http://localhost:8000/docs")
    else:
        print("⚠️  Some tests failed. Please address the issues above.")
        print("\nCommon fixes:")
        print("  1. Create .env file from .env.example")
        print("  2. Configure OpenAI API key")
        print("  3. Set up SQL Server connection")
        print("  4. Install ODBC Driver 18 for SQL Server")
        print("\nYou can still start the app, but some features may not work.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
