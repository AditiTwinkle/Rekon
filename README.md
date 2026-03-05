# Rekon - AI-Powered Audit and Compliance Platform

Rekon is an enterprise-grade AI-powered compliance platform that automates regulatory compliance monitoring, audit preparation, and remediation guidance for financial institutions and enterprises.

## Features

- **Automated Compliance**: Reduces manual effort in regulatory analysis and audit preparation
- **Multi-Framework Support**: Integrates DORA, SOX, BMR, IOSCO, NIST, and other regulatory frameworks
- **AI-Powered Analysis**: Uses intelligent agents for requirement extraction, gap identification, and remediation guidance
- **Continuous Monitoring**: Provides real-time compliance status and alerts for regulatory changes
- **Evidence Management**: Collection and organization of compliance evidence
- **Report Generation**: Comprehensive compliance reporting for management and regulators

## Supported Regulatory Frameworks

- **DORA (Digital Operational Resilience Act)**: Category A and B requirements
- **SOX (Sarbanes-Oxley Act)**: Financial reporting and internal controls
- **BMR (EU Benchmark Regulation)**: Financial benchmark administration
- **IOSCO Principles**: International securities regulation standards
- **NIST Cybersecurity Framework**: Federal cybersecurity requirements
- **AppHealth**: Application security and health compliance

## Technology Stack

- **Language**: Python 3.9+
- **Web Framework**: FastAPI
- **AI/ML**: AWS Bedrock with Claude 3
- **Database**: Amazon RDS PostgreSQL (Aurora)
- **Cache**: Amazon ElastiCache (Redis)
- **Storage**: Amazon S3
- **Infrastructure**: AWS CDK (Python)
- **Orchestration**: AWS Step Functions, EventBridge
- **Monitoring**: CloudWatch, X-Ray

## Project Structure

```
rekon/
├── src/rekon/              # Main Python package
│   ├── api/                # FastAPI routes
│   ├── core/               # Configuration and exceptions
│   ├── domain/             # Domain models
│   ├── db/                 # Database layer
│   ├── services/           # Business services
│   ├── agents/             # AI agents
│   └── utils/              # Utilities
├── infrastructure/         # AWS CDK infrastructure
├── tests/                  # Test suite
├── requirements/           # Python dependencies
└── docs/                   # Documentation
```

## Getting Started

### Prerequisites

- Python 3.9+
- AWS Account with appropriate permissions
- PostgreSQL 13+ (for local development)
- Redis 6+ (for local development)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/rekon/rekon.git
cd rekon
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements/dev.txt
pip install -r requirements/cdk.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Local Development

Start the FastAPI development server:
```bash
python -m uvicorn rekon.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=rekon --cov-report=html
```

Run specific test category:
```bash
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest tests/property/       # Property-based tests only
```

### AWS Infrastructure

Deploy infrastructure with CDK:
```bash
cd infrastructure
cdk deploy
```

Synthesize CloudFormation template:
```bash
cdk synth
```

## API Documentation

The API follows OpenAPI 3.0 specification. Full documentation is available at `/docs` endpoint when running the server.

### Key Endpoints

- `GET /api/v1/regulations` - List regulations
- `POST /api/v1/regulations/sync` - Trigger regulation sync
- `GET /api/v1/checklists` - List checklists
- `POST /api/v1/checklists/generate` - Generate checklist
- `POST /api/v1/compliance/analyze` - Initiate delta analysis
- `POST /api/v1/gaps/assess` - Start gap assessment
- `POST /api/v1/remediation/generate` - Generate remediation plan
- `GET /api/v1/dashboard` - Get compliance dashboard

## Development Guidelines

### Code Style

- Use Black for code formatting
- Use isort for import sorting
- Use mypy for type checking
- Use flake8 for linting

Format code:
```bash
black src/rekon tests
isort src/rekon tests
```

Check code quality:
```bash
flake8 src/rekon
mypy src/rekon
```

### Testing

- Write unit tests for all new functions
- Write integration tests for workflows
- Write property-based tests for core logic
- Aim for 80%+ code coverage

### Commit Guidelines

- Use descriptive commit messages
- Reference issue numbers when applicable
- Keep commits focused and atomic

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For support, please contact support@rekon.io or open an issue on GitHub.
