# Project Organization and Folder Structure

## Recommended Project Structure

```
rekon/
├── .kiro/                          # Kiro configuration and specs
│   ├── specs/                      # Specification documents
│   │   └── rekon/                  # Rekon feature specs
│   │       ├── requirements.md     # Requirements document
│   │       ├── design.md           # Design document
│   │       └── tasks.md            # Implementation tasks
│   └── steering/                   # Steering documents (this folder)
│       ├── product.md              # Product overview
│       ├── tech.md                 # Technology stack
│       └── structure.md            # Project structure
│
├── src/                            # Python source code
│   ├── rekon/                      # Main package
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── api/                    # API layer
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py     # API dependencies
│   │   │   └── routes/             # API routes
│   │   │       ├── __init__.py
│   │   │       ├── regulations.py  # Regulation endpoints
│   │   │       ├── checklists.py   # Checklist endpoints
│   │   │       ├── compliance.py   # Compliance endpoints
│   │   │       └── remediation.py  # Remediation endpoints
│   │   ├── core/                   # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── config.py           # Configuration
│   │   │   └── exceptions.py       # Custom exceptions
│   │   ├── domain/                 # Domain models and logic
│   │   │   ├── __init__.py
│   │   │   ├── models/             # Pydantic models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── regulation.py   # Regulation models
│   │   │   │   ├── checklist.py    # Checklist models
│   │   │   │   └── compliance.py   # Compliance models
│   │   │   └── schemas/            # Database schemas (SQLAlchemy)
│   │   │       ├── __init__.py
│   │   │       ├── base.py         # Base model
│   │   │       └── regulation.py   # Regulation schema
│   │   ├── services/               # Business services
│   │   │   ├── __init__.py
│   │   │   ├── regulation_puller.py # Regulation fetching service
│   │   │   ├── checklist_generator.py # Checklist generation service
│   │   │   ├── delta_analyzer.py   # Delta analysis service
│   │   │   └── remediation_engine.py # Remediation service
│   │   ├── agents/                 # AI agents
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py       # Base agent class
│   │   │   ├── checklist_agent.py  # Checklist generation agent
│   │   │   └── gap_identifier.py   # Gap identification agent
│   │   ├── db/                     # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── session.py          # Database session
│   │   │   └── repositories/       # Data repositories
│   │   │       ├── __init__.py
│   │   │       └── regulation.py   # Regulation repository
│   │   └── utils/                  # Utilities
│   │       ├── __init__.py
│   │       ├── logging.py          # Logging configuration
│   │       └── validators.py       # Data validators
│   │
├── tests/                          # Test files
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures
│   ├── unit/                       # Unit tests
│   │   ├── __init__.py
│   │   ├── test_services/          # Service tests
│   │   │   ├── __init__.py
│   │   │   └── test_regulation_puller.py
│   │   ├── test_agents/            # Agent tests
│   │   │   ├── __init__.py
│   │   │   └── test_checklist_agent.py
│   │   └── test_utils/             # Utility tests
│   │       ├── __init__.py
│   │       └── test_validators.py
│   ├── integration/                # Integration tests
│   │   ├── __init__.py
│   │   └── test_api/               # API integration tests
│   │       ├── __init__.py
│   │       └── test_regulations.py
│   └── property/                   # Property-based tests
│       ├── __init__.py
│       └── test_compliance_properties.py
│
├── docs/                           # Documentation
│   ├── api/                        # API documentation
│   ├── architecture/               # Architecture diagrams
│   └── user-guides/                # User guides
│
├── infrastructure/                 # AWS CDK Infrastructure
│   ├── cdk.json                    # CDK configuration
│   ├── app.py                      # CDK app entry point
│   ├── stacks/                     # CDK stacks
│   │   ├── __init__.py
│   │   ├── bedrock_stack.py        # Bedrock agents and knowledge bases
│   │   ├── lambda_stack.py         # Lambda functions for agents
│   │   ├── api_stack.py            # API Gateway and FastAPI
│   │   ├── database_stack.py       # RDS, DynamoDB, ElastiCache
│   │   └── monitoring_stack.py     # CloudWatch, X-Ray, SNS
│   └── constructs/                 # CDK constructs
│       ├── __init__.py
│       ├── bedrock_agent.py        # Bedrock agent construct
│       └── compliance_lambda.py    # Compliance Lambda construct
│
├── agents/                         # Bedrock Agent Definitions
│   ├── regulation_parser/          # Regulation parsing agent
│   │   ├── agent.json              # Bedrock agent configuration
│   │   ├── instructions.md         # Agent instructions
│   │   ├── action_groups/          # Action groups
│   │   └── knowledge_bases/        # Knowledge base configurations
│   ├── compliance_checker/         # Compliance checking agent
│   │   ├── agent.json
│   │   ├── instructions.md
│   │   └── action_groups/
│   ├── gap_identifier/             # Gap identification agent
│   │   ├── agent.json
│   │   ├── instructions.md
│   │   └── action_groups/
│   └── remediation_engine/         # Remediation guidance agent
│       ├── agent.json
│       ├── instructions.md
│       └── action_groups/
│
├── lambda_functions/               # AWS Lambda Functions
│   ├── regulation_puller/          # Regulation fetching Lambda
│   │   ├── app.py                  # Lambda handler
│   │   ├── requirements.txt        # Lambda dependencies
│   │   └── events/                 # Test events
│   ├── checklist_generator/        # Checklist generation Lambda
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── events/
│   ├── delta_analyzer/             # Delta analysis Lambda
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── events/
│   └── remediation_engine/         # Remediation Lambda
│       ├── app.py
│       ├── requirements.txt
│       └── events/
│
├── step_functions/                 # AWS Step Functions Workflows
│   ├── compliance_assessment.asl.json  # Compliance assessment workflow
│   ├── regulation_update.asl.json      # Regulation update workflow
│   └── audit_preparation.asl.json      # Audit preparation workflow
│
├── scripts/                        # Build and utility scripts
│   ├── deploy_agents.py            # Deploy Bedrock agents
│   ├── test_workflows.py           # Test Step Functions workflows
│   └── setup_aws.py                # AWS setup script
│
├── config/                         # Configuration files
│   ├── aws/                        # AWS-specific configs
│   │   ├── development.yaml        # Development AWS config
│   │   ├── production.yaml         # Production AWS config
│   │   └── bedrock_models.yaml     # Bedrock model configurations
│   └── agents/                     # Agent configurations
│       ├── regulation_parser.yaml
│       ├── compliance_checker.yaml
│       └── gap_identifier.yaml
│
├── .github/                        # GitHub workflows
│   └── workflows/
│       ├── aws_deploy.yml          # AWS deployment pipeline
│       ├── agent_testing.yml       # Agent testing pipeline
│       └── security_scan.yml       # Security scanning
│
├── requirements/                   # Python dependencies
│   ├── base.txt                    # Base dependencies
│   ├── dev.txt                     # Development dependencies
│   ├── lambda.txt                  # Lambda function dependencies
│   └── cdk.txt                     # CDK infrastructure dependencies
│
├── pyproject.toml                  # Python project config
├── README.md                       # Project README
├── .env.example                    # Environment variables example
├── .python-version                 # Python version (3.9+)
└── samconfig.toml                  # SAM configuration
```

## Key Directories and Their Purposes

### `.kiro/`
- **Purpose**: Contains Kiro-specific configuration and specifications
- **Contents**: Specification documents, steering rules, and agent configurations
- **Usage**: Guides AI assistants in understanding project requirements and constraints

### `src/rekon/` (Main Python Package)
- **Purpose**: Main Python package containing all source code
- **Organization**: Follows FastAPI/domain-driven design with clear separation of concerns
- **Key Components**:
  - `api/`: FastAPI routes and endpoint definitions
  - `core/`: Core application configuration and exceptions
  - `domain/`: Business domain models and schemas
  - `services/`: Business logic and service layer
  - `agents/`: AI agent implementations
  - `db/`: Database layer and repositories
  - `utils/`: Utility functions and helpers

### `tests/`
- **Purpose**: Comprehensive test suite
- **Organization**: Separated by test type and component
- **Key Sections**:
  - `unit/`: Isolated unit tests for individual components
  - `integration/`: Integration tests for component interaction
  - `property/`: Property-based tests for correctness properties

### `docs/`
- **Purpose**: Project documentation
- **Organization**: Categorized by audience and purpose
- **Key Sections**:
  - `api/`: API documentation and usage examples
  - `architecture/`: System design and architecture
  - `user-guides/`: End-user documentation

## Naming Conventions

### Files
- **Python files**: Use snake_case (e.g., `regulation_puller.py`)
- **Configuration**: Use kebab-case (e.g., `development.yaml`)
- **Test files**: Use `test_` prefix (e.g., `test_regulation_puller.py`)

### Directories
- Use lowercase with hyphens for multi-word directory names
- Keep directory names descriptive and consistent
- Avoid abbreviations unless widely understood

## Python-Specific Guidelines

### Package Structure
1. **src/rekon/**: Main package directory
2. **__init__.py files**: Required for Python packages
3. **Type hints**: Use type hints for all function signatures
4. **Imports**: Use absolute imports within the package
5. **Dependencies**: Manage with `pyproject.toml` and `requirements/` directory

### Code Organization Principles

1. **Separation of Concerns**: Each directory has a clear, single responsibility
2. **Modularity**: Components are independently testable and replaceable
3. **Consistency**: Follow established patterns throughout the codebase
4. **Documentation**: All major components should be documented
5. **Testability**: Structure facilitates comprehensive testing

## Development Workflow

1. **Start with specs**: Always reference `.kiro/specs/` for requirements
2. **Follow steering rules**: Adhere to guidelines in `.kiro/steering/`
3. **Implement incrementally**: Build features according to task priorities
4. **Test thoroughly**: Write tests for all new functionality
5. **Document changes**: Update relevant documentation as code evolves