# Text-to-SQL Application

AI-powered application that converts natural language questions into SQL queries for SQL Server databases, with comprehensive safety features for all CRUD operations.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-orange.svg)](https://openai.com/)
[![SQL Server](https://img.shields.io/badge/SQL_Server-Supported-red.svg)](https://www.microsoft.com/sql-server)

## ✨ Features

- 🤖 **AI-Powered SQL Generation**: Convert natural language to T-SQL using OpenAI GPT models
- 🛡️ **Multi-Layer Safety**: Query classification, risk assessment, and confirmation workflows
- 🔍 **Full CRUD Support**: SELECT, INSERT, UPDATE, DELETE with appropriate safety checks
- 👁️ **Preview Before Execute**: See affected rows before committing write operations
- 📊 **Schema Introspection**: Automatic database schema discovery and caching
- 🔄 **Transaction Support**: Transactional execution for data consistency
- 📝 **Query History**: Track all executed queries with audit trail
- 🚀 **REST API**: FastAPI-based endpoints for easy integration
- 🐳 **Docker Ready**: Containerized deployment with docker-compose

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Client    │─────▶│  FastAPI API │─────▶│  OpenAI API │
│ (Frontend)  │      │   Endpoints  │      │   (GPT-4)   │
└─────────────┘      └──────────────┘      └─────────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
            ┌───────────────┐  ┌─────────────┐
            │    Query      │  │  Database   │
            │  Classifier   │  │   Manager   │
            └───────────────┘  └─────────────┘
                    │                 │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │   SQL Server    │
                    │    Database     │
                    └─────────────────┘
```

## 🔒 Safety Features

### Query Classification

Queries are automatically classified into four types:

- **READ**: SELECT operations (low risk)
- **WRITE_SAFE**: INSERT or targeted UPDATE/DELETE with WHERE clause (medium risk)
- **WRITE_RISKY**: Bulk operations or operations without WHERE clause (high risk)
- **ADMIN**: CREATE, DROP, ALTER operations (critical risk)

### Confirmation Workflow

1. **READ queries**: Can execute immediately (configurable)
2. **WRITE_SAFE queries**: Require user confirmation
3. **WRITE_RISKY queries**: Show preview of affected rows + require confirmation
4. **ADMIN queries**: Disabled by default, require explicit configuration

### Risk Assessment

Each query receives a risk level:
- **Low**: No data modification
- **Medium**: Targeted single/multi-row operations
- **High**: Bulk operations affecting many rows
- **Critical**: Operations without WHERE clause or schema changes

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- SQL Server (local, remote, or Azure SQL)
- OpenAI API key
- Docker (optional)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/text-to-sql-app.git
cd text-to-sql-app
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your settings
```

Required environment variables:
```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# SQL Server
DB_SERVER=your_server_name
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password

# Security
SECRET_KEY=your_secret_key_here
```

5. **Run the application**:
```bash
python -m app.main
# Or with uvicorn
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 📖 API Usage

### 1. Ask a Question

Convert natural language to SQL:

```bash
curl -X POST "http://localhost:8000/query/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me all customers from New York",
    "execute_immediately": true
  }'
```

Response:
```json
{
  "query_id": "123e4567-e89b-12d3-a456-426614174000",
  "sql": "SELECT * FROM customers WHERE city = 'New York'",
  "query_type": "READ",
  "risk_level": "low",
  "explanation": "This query retrieves all customers located in New York",
  "requires_confirmation": false,
  "executed": true,
  "results": [...],
  "row_count": 42
}
```

### 2. Preview Write Operations

Before executing a write operation, preview affected rows:

```bash
curl -X GET "http://localhost:8000/query/preview/{query_id}"
```

Response:
```json
{
  "query_id": "123e4567-e89b-12d3-a456-426614174000",
  "affected_rows": 145,
  "sample_data": [...],
  "warnings": ["Large operation: 145 rows will be affected"]
}
```

### 3. Execute with Confirmation

Execute a pending query:

```bash
curl -X POST "http://localhost:8000/query/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": "123e4567-e89b-12d3-a456-426614174000",
    "confirmed": true
  }'
```

### 4. Get Schema Information

```bash
curl -X GET "http://localhost:8000/schema"
```

### 5. View Query History

```bash
curl -X GET "http://localhost:8000/query/history?limit=50"
```

## 📚 API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | OpenAI model to use | gpt-4o-mini |
| `DB_SERVER` | SQL Server hostname/IP | Required |
| `DB_PORT` | SQL Server port | 1433 |
| `DB_NAME` | Database name | Required |
| `DB_USER` | Database username | Required |
| `DB_PASSWORD` | Database password | Required |
| `REQUIRE_CONFIRMATION_FOR_WRITES` | Require confirmation for write operations | true |
| `ENABLE_ADMIN_OPERATIONS` | Enable CREATE/DROP/ALTER operations | false |
| `MAX_ROWS_RETURN` | Maximum rows to return | 1000 |
| `QUERY_TIMEOUT_SECONDS` | Query execution timeout | 30 |

### Security Settings

**Production Recommendations**:
- Set `REQUIRE_CONFIRMATION_FOR_WRITES=true`
- Keep `ENABLE_ADMIN_OPERATIONS=false` unless absolutely necessary
- Use strong `SECRET_KEY` (generate with `openssl rand -hex 32`)
- Configure CORS appropriately in `app/main.py`
- Use SQL Server authentication with least-privilege accounts
- Enable SSL/TLS for database connections

## 🧪 Example Use Cases

### 1. Data Exploration
```
Question: "How many orders were placed last month?"
SQL: SELECT COUNT(*) FROM orders WHERE order_date >= DATEADD(month, -1, GETDATE())
```

### 2. Data Updates
```
Question: "Update the email for customer with ID 12345"
SQL: UPDATE customers SET email = 'new@email.com' WHERE customer_id = 12345
Preview: Shows current customer data
Confirmation: Required
```

### 3. Complex Queries
```
Question: "Show top 10 customers by total purchase amount"
SQL: SELECT TOP 10 c.customer_id, c.name, SUM(o.total_amount) as total_spent
     FROM customers c
     JOIN orders o ON c.customer_id = o.customer_id
     GROUP BY c.customer_id, c.name
     ORDER BY total_spent DESC
```

## 🛠️ Development

### Project Structure

```
text-to-sql-app/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── core/
│   │   ├── database.py         # Database connection & execution
│   │   ├── openai_client.py    # OpenAI integration
│   │   ├── query_classifier.py # Query classification & validation
│   │   └── query_executor.py   # Query execution workflow
│   ├── models/
│   │   └── query_models.py     # Pydantic models
│   └── utils/
├── tests/                       # Test suite
├── docs/                        # Additional documentation
├── .env.example                 # Example environment configuration
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image definition
├── docker-compose.yml          # Docker compose configuration
└── README.md                    # This file
```

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black app/

# Lint
flake8 app/

# Type checking
mypy app/
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ⚠️ Security Considerations

- **Never expose this API directly to the internet without authentication**
- Use strong database credentials with minimal required permissions
- Regularly rotate API keys and secrets
- Review query logs for suspicious activity
- Test thoroughly in development before production use
- Consider rate limiting for production deployments

## 🐛 Troubleshooting

### Database Connection Issues

1. **ODBC Driver not found**:
   ```bash
   # Install ODBC Driver 18 for SQL Server
   # Windows: Download from Microsoft
   # Linux: Follow installation steps in Dockerfile
   ```

2. **Authentication failed**:
   - Verify credentials in `.env`
   - Check SQL Server allows remote connections
   - Verify firewall rules allow port 1433

3. **SSL/TLS errors**:
   - Add `TrustServerCertificate=yes` to connection string
   - Or configure proper SSL certificates

### OpenAI API Issues

1. **Rate limits**:
   - Use lower-tier models for development
   - Implement request throttling
   - Consider caching common queries

2. **Invalid API key**:
   - Verify key in `.env`
   - Check key has not expired
   - Ensure sufficient credits

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [OpenAI](https://openai.com/) for the GPT models
- [SQLAlchemy](https://www.sqlalchemy.org/) for database abstraction
- Inspired by the [KDNuggets tutorial](https://www.kdnuggets.com/creating-a-text-to-sql-app-with-openai-fastapi-sqlite)

---

**Built with ❤️ for data teams who want to query databases in plain English**
