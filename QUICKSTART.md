# Rekon Quick Start Guide

## Project Setup

This guide will help you get Rekon up and running locally for development.

### Prerequisites

- Python 3.9+
- pip and virtualenv
- AWS CLI configured (for CDK deployment)
- PostgreSQL 13+ (for local development)
- Redis 6+ (for local development)

### Step 1: Clone and Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd rekon

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt
pip install -r requirements/cdk.txt
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# At minimum, set:
# - AWS_REGION
# - DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
# - REDIS_HOST, REDIS_PORT
```

### Step 3: Set Up Local Database

For local development, you can use Docker:

```bash
# Start PostgreSQL
docker run --name rekon-postgres \
  -e POSTGRES_USER=rekon \
  -e POSTGRES_PASSWORD=changeme \
  -e POSTGRES_DB=rekon \
  -p 5432:5432 \
  -d postgres:15

# Start Redis
docker run --name rekon-redis \
  -p 6379:6379 \
  -d redis:7
```

### Step 4: Run the Application

```bash
# Start the FastAPI development server
python -m uvicorn rekon.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Step 5: Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rekon --cov-report=html

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/property/
```

## Project Structure

```
rekon/
├── src/rekon/              # Main application code
│   ├── api/                # FastAPI routes and authentication
│   ├── core/               # Configuration and exceptions
│   ├── domain/             # Domain models
│   ├── db/                 # Database layer
│   ├── services/           # Business services
│   ├── agents/             # AI agents (Bedrock)
│   └── utils/              # Utilities
├── infrastructure/         # AWS CDK infrastructure
├── tests/                  # Test suite
├── requirements/           # Python dependencies
└── docs/                   # Documentation
```

## API Endpoints

### Regulations
- `GET /api/v1/regulations` - List regulations
- `POST /api/v1/regulations/sync` - Trigger sync
- `GET /api/v1/regulations/{id}` - Get regulation details

### Checklists
- `GET /api/v1/checklists` - List checklists
- `POST /api/v1/checklists/generate` - Generate checklist
- `GET /api/v1/checklists/{id}` - Get checklist details

### Compliance
- `POST /api/v1/compliance/analyze` - Initiate delta analysis
- `GET /api/v1/compliance/status` - Get compliance status
- `GET /api/v1/compliance/scores` - Get compliance scores

### Gaps
- `POST /api/v1/gaps/assess` - Start gap assessment
- `GET /api/v1/gaps/{id}` - Get gap details
- `POST /api/v1/gaps/{id}/respond` - Submit assessment response

### Remediation
- `POST /api/v1/remediation/generate` - Generate remediation plan
- `GET /api/v1/remediation/{id}` - Get remediation plan
- `PATCH /api/v1/remediation/{id}/progress` - Update progress

### Evidence
- `POST /api/v1/evidence/upload` - Upload evidence
- `GET /api/v1/evidence` - List evidence
- `DELETE /api/v1/evidence/{id}` - Delete evidence

### Reports
- `POST /api/v1/reports/generate` - Generate report
- `GET /api/v1/reports` - List reports
- `GET /api/v1/reports/{id}/download` - Download report

### Dashboard
- `GET /api/v1/dashboard` - Get dashboard data
- `GET /api/v1/dashboard/trends` - Get trend data
- `GET /api/v1/dashboard/alerts` - Get active alerts

## AWS Infrastructure Deployment

### Deploy with CDK

```bash
cd infrastructure

# Synthesize CloudFormation template
cdk synth

# Deploy to AWS
cdk deploy

# Deploy specific stack
cdk deploy RekonVpcStack
cdk deploy RekonDatabaseStack
```

### Infrastructure Components

- **VPC**: Virtual Private Cloud with public and private subnets
- **RDS Aurora**: PostgreSQL database with multi-AZ
- **S3**: Evidence and reports storage with encryption
- **DynamoDB**: Session and state management
- **ElastiCache**: Redis for caching
- **EventBridge**: Event routing
- **Step Functions**: Workflow orchestration

## Development Workflow

### Code Quality

```bash
# Format code
black src/rekon tests
isort src/rekon tests

# Check code quality
flake8 src/rekon
mypy src/rekon

# Run linting
isort --check-only src/rekon
black --check src/rekon
```

### Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_regulations.py

# Run with coverage report
pytest --cov=rekon --cov-report=html
```

## Troubleshooting

### Database Connection Issues

If you get database connection errors:

1. Verify PostgreSQL is running: `docker ps | grep postgres`
2. Check connection string in `.env`
3. Verify database exists: `psql -U rekon -d rekon -h localhost`

### Redis Connection Issues

If you get Redis connection errors:

1. Verify Redis is running: `docker ps | grep redis`
2. Check Redis connection: `redis-cli ping`
3. Verify Redis URL in `.env`

### Import Errors

If you get import errors:

1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements/dev.txt`
3. Check Python path: `echo $PYTHONPATH`

## Next Steps

1. Review the [Design Document](./docs/design.md)
2. Check the [API Documentation](./docs/api/)
3. Read the [Architecture Guide](./docs/architecture/)
4. Explore the [User Guide](./docs/user-guides/)

## Support

For issues or questions:
- Check existing GitHub issues
- Create a new issue with detailed description
- Contact the team at support@rekon.io

## License

This project is licensed under the MIT License - see LICENSE file for details.
