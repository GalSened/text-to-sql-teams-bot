#!/usr/bin/env python3
"""
Database Setup Script
Initializes the PostgreSQL database and creates sample test data
"""

import os
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv('.env.devtest')

# Database connection config
DB_CONFIG = {
    'host': os.getenv('QUEUE_DB_HOST', 'localhost'),
    'port': int(os.getenv('QUEUE_DB_PORT', 5432)),
    'database': os.getenv('QUEUE_DB_NAME', 'text_to_sql_queue'),
    'user': os.getenv('QUEUE_DB_USER', 'postgres'),
    'password': os.getenv('QUEUE_DB_PASSWORD', 'postgres')
}


def create_sample_schema():
    """Sample database schema for testing"""
    return {
        "tables": [
            {
                "name": "companies",
                "columns": [
                    {"name": "id", "type": "INT", "primary_key": True},
                    {"name": "company_name", "type": "VARCHAR(200)"},
                    {"name": "created_date", "type": "DATETIME"},
                    {"name": "status", "type": "VARCHAR(50)"}
                ]
            },
            {
                "name": "customers",
                "columns": [
                    {"name": "id", "type": "INT", "primary_key": True},
                    {"name": "customer_name", "type": "VARCHAR(200)"},
                    {"name": "email", "type": "VARCHAR(200)"},
                    {"name": "total_revenue", "type": "DECIMAL(18,2)"},
                    {"name": "status", "type": "VARCHAR(50)"}
                ]
            },
            {
                "name": "orders",
                "columns": [
                    {"name": "id", "type": "INT", "primary_key": True},
                    {"name": "customer_id", "type": "INT"},
                    {"name": "order_date", "type": "DATETIME"},
                    {"name": "total_amount", "type": "DECIMAL(18,2)"},
                    {"name": "status", "type": "VARCHAR(50)"}
                ]
            }
        ]
    }


def initialize_database():
    """Initialize database with schema"""
    print("🔌 Connecting to database...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✅ Connected successfully")

        # Read and execute schema
        print("\n📝 Creating database schema...")
        with open('database/schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        cursor.execute(schema_sql)
        conn.commit()
        print("✅ Schema created successfully")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def add_sample_requests():
    """Add sample test requests to the queue"""
    print("\n📥 Adding sample test requests...")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        schema_info = create_sample_schema()

        # Sample requests in English
        english_requests = [
            ("How many companies joined in the past 3 months?", "en", "devtest"),
            ("Show top 10 customers by revenue", "en", "devtest"),
            ("List all active customers", "en", "prod"),
            ("Show all orders from last week", "en", "devtest"),
        ]

        # Sample requests in Hebrew
        hebrew_requests = [
            ("כמה חברות הצטרפו ב-3 החודשים האחרונים?", "he", "devtest"),
            ("הראה את 10 הלקוחות המובילים לפי הכנסות", "he", "devtest"),
            ("הצג את כל הלקוחות הפעילים", "he", "prod"),
        ]

        # Insert requests
        count = 0
        for question, language, environment in english_requests + hebrew_requests:
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
                str(uuid.uuid4()),
                question,
                Json(schema_info),
                environment,
                language,
                'pending',
                'test_user'
            ))
            count += 1
            print(f"   ✓ Added request {count}: {question[:50]}...")

        conn.commit()
        print(f"\n✅ Added {count} sample requests")

        # Show queue status
        cursor.execute("""
            SELECT environment, language, COUNT(*) as count
            FROM sql_queue
            WHERE status = 'pending'
            GROUP BY environment, language
            ORDER BY environment, language
        """)

        print("\n📊 Queue Status:")
        print("   Environment | Language | Count")
        print("   " + "-" * 35)
        for row in cursor.fetchall():
            print(f"   {row[0]:11} | {row[1]:8} | {row[2]:5}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error adding sample requests: {e}")
        return False


def verify_setup():
    """Verify database is set up correctly"""
    print("\n🔍 Verifying setup...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'sql_queue'
            )
        """)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            print("❌ sql_queue table not found")
            return False

        # Count pending requests
        cursor.execute("SELECT COUNT(*) FROM sql_queue WHERE status = 'pending'")
        pending_count = cursor.fetchone()[0]

        print(f"✅ Database setup verified")
        print(f"   - sql_queue table exists")
        print(f"   - {pending_count} pending requests")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


def main():
    """Main setup process"""
    print("=" * 60)
    print("SQL Queue Database Setup")
    print("=" * 60)

    # Step 1: Initialize database
    if not initialize_database():
        print("\n❌ Setup failed during database initialization")
        return

    # Step 2: Add sample requests
    if not add_sample_requests():
        print("\n❌ Setup failed during sample data creation")
        return

    # Step 3: Verify setup
    if not verify_setup():
        print("\n❌ Setup verification failed")
        return

    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("=" * 60)
    print("\nYou can now run:")
    print("  python process_queue.py")
    print("\nOr check the queue status:")
    print("  SELECT * FROM queue_stats;")
    print("=" * 60)


if __name__ == '__main__':
    main()
