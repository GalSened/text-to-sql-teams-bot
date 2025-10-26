"""
Interactive configuration helper for Text-to-SQL application.
Run this to set up your .env file with the correct values.
"""
import os
import sys

def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def print_section(text):
    print(f"\n>>> {text}")

def get_input(prompt, default=None, required=True):
    """Get user input with optional default value."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "

    while True:
        value = input(prompt).strip()

        if not value and default:
            return default

        if not value and required:
            print("❌ This field is required. Please enter a value.")
            continue

        if not value and not required:
            return ""

        return value

def main():
    print_header("Text-to-SQL Application Configuration")
    print("\nThis wizard will help you configure your .env file.")
    print("Press Ctrl+C at any time to exit.\n")

    config = {}

    try:
        # OpenAI Configuration
        print_section("1. OpenAI API Configuration")
        print("Get your API key from: https://platform.openai.com/api-keys")

        has_key = get_input("Do you have an OpenAI API key? (yes/no)", "no", False).lower()

        if has_key in ['yes', 'y']:
            config['OPENAI_API_KEY'] = get_input("Enter your OpenAI API key")
        else:
            print("⚠️  You can add the API key later in the .env file")
            config['OPENAI_API_KEY'] = "sk-placeholder-add-your-key-here"

        config['OPENAI_MODEL'] = get_input("OpenAI model to use", "gpt-4o-mini")

        # Database Configuration
        print_section("2. Database Configuration")

        db_type = get_input(
            "Database type (1=Local SQL Server, 2=Remote SQL Server, 3=Azure SQL, 4=Skip for now)",
            "4"
        )

        if db_type in ['1', '2', '3']:
            if db_type == '1':
                config['DB_SERVER'] = get_input("SQL Server instance", "localhost")
            elif db_type == '2':
                config['DB_SERVER'] = get_input("SQL Server hostname or IP")
            elif db_type == '3':
                config['DB_SERVER'] = get_input("Azure SQL Server (e.g., myserver.database.windows.net)")

            config['DB_PORT'] = get_input("SQL Server port", "1433")
            config['DB_NAME'] = get_input("Database name")
            config['DB_USER'] = get_input("Database username")
            config['DB_PASSWORD'] = get_input("Database password")
        else:
            print("⚠️  Skipping database configuration. You can add it later.")
            config['DB_SERVER'] = "localhost"
            config['DB_PORT'] = "1433"
            config['DB_NAME'] = "TestDB"
            config['DB_USER'] = "sa"
            config['DB_PASSWORD'] = "ChangeMe123!"

        # Application Configuration
        print_section("3. Application Configuration")
        config['APP_PORT'] = get_input("Application port", "8000")
        config['DEBUG'] = get_input("Enable debug mode? (true/false)", "true")

        # Security
        print_section("4. Security Configuration")
        print("Generating secure SECRET_KEY...")
        import secrets
        config['SECRET_KEY'] = secrets.token_hex(32)
        print(f"✓ Generated: {config['SECRET_KEY'][:20]}...")

        config['REQUIRE_CONFIRMATION_FOR_WRITES'] = get_input(
            "Require confirmation for write operations? (true/false)", "true"
        )
        config['ENABLE_ADMIN_OPERATIONS'] = get_input(
            "Enable admin operations (DROP, CREATE, ALTER)? (true/false)", "false"
        )

        # Generate .env file
        print_section("5. Generating .env file")

        env_content = f"""# OpenAI Configuration
OPENAI_API_KEY={config['OPENAI_API_KEY']}
OPENAI_MODEL={config['OPENAI_MODEL']}

# SQL Server Configuration
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_SERVER={config['DB_SERVER']}
DB_PORT={config['DB_PORT']}
DB_NAME={config['DB_NAME']}
DB_USER={config['DB_USER']}
DB_PASSWORD={config['DB_PASSWORD']}
DB_TRUSTED_CONNECTION=no

# Application Configuration
APP_NAME=Text-to-SQL Application
APP_VERSION=1.0.0
APP_HOST=0.0.0.0
APP_PORT={config['APP_PORT']}
DEBUG={config['DEBUG']}

# Security
SECRET_KEY={config['SECRET_KEY']}
REQUIRE_CONFIRMATION_FOR_WRITES={config['REQUIRE_CONFIRMATION_FOR_WRITES']}
ENABLE_ADMIN_OPERATIONS={config['ENABLE_ADMIN_OPERATIONS']}

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Query Limits
MAX_ROWS_RETURN=1000
QUERY_TIMEOUT_SECONDS=30
"""

        # Backup existing .env if it exists
        if os.path.exists('.env'):
            backup_file = '.env.backup'
            print(f"⚠️  Backing up existing .env to {backup_file}")
            with open('.env', 'r') as f:
                with open(backup_file, 'w') as bf:
                    bf.write(f.read())

        # Write new .env
        with open('.env', 'w') as f:
            f.write(env_content)

        print_header("✅ Configuration Complete!")
        print("\n✓ .env file created successfully!")
        print("\nNext steps:")
        print("1. Review the .env file and update if needed")
        print("2. Run: python test_basic.py")
        print("3. Start app: uvicorn app.main:app --reload")
        print("4. Open: http://localhost:8000/docs")

        print("\n" + "=" * 60)

        # Test configuration
        print("\nTesting configuration...")
        try:
            sys.path.insert(0, os.path.dirname(__file__))
            from app.config import settings
            print("✓ Configuration loaded successfully!")
            print(f"  - App: {settings.app_name}")
            print(f"  - Database: {settings.db_server}/{settings.db_name}")
            print(f"  - Port: {settings.app_port}")
        except Exception as e:
            print(f"⚠️  Configuration test failed: {e}")
            print("   Please review your .env file and fix any issues.")

    except KeyboardInterrupt:
        print("\n\n❌ Configuration cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
