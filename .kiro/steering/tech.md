# Technology Stack and Build System

## Build System & Infrastructure
- **Package Manager**: pip/poetry (Python)
- **Infrastructure as Code**: AWS CDK (Python)
- **CI/CD**: AWS CodePipeline, GitHub Actions with AWS integration
- **Containerization**: Docker with ECS/EKS deployment
- **Dependency Management**: `pyproject.toml` with `requirements/` directory

## AWS-First Tech Stack

### Core Framework & Agentic Architecture
- **Language**: Python 3.9+ (optimized for AWS Lambda and Bedrock)
- **Web Framework**: FastAPI (async, high-performance) for API Gateway integration
- **Agent Framework**: AWS Bedrock AgentCore for agent orchestration
- **Validation**: Pydantic v2 (data validation and settings management)
- **Async Support**: asyncio with async/await patterns for Lambda functions

### AWS AI/ML Services (Primary)
- **LLM Capabilities**: Amazon Bedrock (Claude, Llama, Titan models)
- **Agent Orchestration**: AWS Bedrock AgentCore for intelligent agent workflows
- **Vector Database**: Amazon Aurora PostgreSQL with pgvector extension
- **Model Training**: Amazon SageMaker for custom model fine-tuning
- **Document Processing**: Amazon Textract for regulatory document extraction
- **Search**: Amazon OpenSearch for regulatory text search
- **Knowledge Bases**: Amazon Bedrock Knowledge Bases for RAG

### AWS Compute & Serverless
- **Serverless Functions**: AWS Lambda (Python runtime)
- **Container Orchestration**: Amazon ECS/EKS for long-running agents
- **API Management**: Amazon API Gateway with FastAPI integration
- **Event Processing**: Amazon EventBridge for agent workflow orchestration
- **Message Queues**: Amazon SQS for async agent communication
- **Stream Processing**: Amazon Kinesis for real-time compliance events

### AWS Data & Storage
- **Relational Database**: Amazon RDS PostgreSQL (Aurora)
- **Document Storage**: Amazon S3 for regulatory documents and evidence
- **Caching**: Amazon ElastiCache (Redis) for agent session management
- **Secrets Management**: AWS Secrets Manager for API keys and credentials
- **Configuration**: AWS AppConfig for dynamic agent configuration

### AWS Monitoring & Observability
- **Metrics**: Amazon CloudWatch Metrics and Dashboards
- **Logging**: Amazon CloudWatch Logs with structured logging
- **Tracing**: AWS X-Ray for distributed tracing of agent workflows
- **Alerting**: Amazon CloudWatch Alarms and SNS notifications
- **Error Tracking**: CloudWatch Log Insights for agent error analysis

### Development & Testing Tools
- **Local Development**: AWS SAM CLI for local Lambda testing
- **Testing**: pytest with moto for AWS service mocking
- **Property Testing**: hypothesis for agent behavior validation
- **Code Quality**: black, isort, flake8, mypy
- **Infrastructure Testing**: AWS CDK assertions
- **Security Scanning**: AWS CodeGuru for security and quality

## Common Commands

### Development & Local Testing
```bash
# Install dependencies
pip install -r requirements/base.txt
pip install -r requirements/dev.txt

# Start local API server
python -m uvicorn rekon.main:app --reload --host 0.0.0.0 --port 8000

# Test Lambda functions locally with SAM
sam local start-api
sam local invoke RegulationPullerFunction

# Test Bedrock agents locally (if supported)
python -m pytest tests/agents/ --bedrock-mock

# Run all tests
pytest

# Run specific test category
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest tests/agents/         # Agent tests only

# Run with AWS service mocking
pytest --mock-aws

# Lint code
flake8 src/rekon
black src/rekon --check
isort src/rekon --check-only
mypy src/rekon
```

### AWS Infrastructure & Deployment
```bash
# Synthesize CDK stack
cdk synth

# Deploy to AWS
cdk deploy

# Deploy specific stack
cdk deploy RekonAgentsStack
cdk deploy RekonApiStack

# Destroy infrastructure
cdk destroy

# List stacks
cdk list

# Diff changes
cdk diff

# Bootstrap CDK (first time)
cdk bootstrap aws://ACCOUNT-NUMBER/REGION
```

### AWS Bedrock & Agent Management
```bash
# List Bedrock models
aws bedrock list-foundation-models

# Create Rekon agent
aws bedrock-agent create-agent --agent-name "Rekon"

# Create specialized Rekon sub-agents
aws bedrock-agent create-agent --agent-name "Rekon-RegulationParser"
aws bedrock-agent create-agent --agent-name "Rekon-ComplianceChecker"
aws bedrock-agent create-agent --agent-name "Rekon-GapIdentifier"
aws bedrock-agent create-agent --agent-name "Rekon-RemediationEngine"

# List agents
aws bedrock-agent list-agents

# Test Rekon agent locally
python scripts/test_agent.py --agent-id REKON_AGENT_ID --input "Check DORA compliance"

# Deploy agent changes
aws bedrock-agent update-agent --agent-id REKON_AGENT_ID --agent-name "Rekon"
```

### Lambda & Serverless Development
```bash
# Build Lambda layer
sam build --use-container

# Package for deployment
sam package --s3-bucket rekon-artifacts --output-template-file packaged.yaml

# Deploy SAM application
sam deploy --template-file packaged.yaml --stack-name rekon-stack --capabilities CAPABILITY_IAM

# Invoke Lambda locally
sam local invoke RegulationPullerFunction --event events/regulation-pull.json

# Tail Lambda logs
sam logs --name RegulationPullerFunction --tail
```

### Testing & Quality
```bash
# Run all tests with AWS mocking
pytest --mock-aws

# Run agent-specific tests
pytest tests/agents/ -v

# Run integration tests (requires AWS credentials)
pytest tests/integration/ --aws-profile rekon-dev

# Generate coverage report
pytest --cov=rekon --cov-report=html

# Run property-based tests for agent behavior
pytest tests/property/ -v

# Security scanning
bandit -r src/rekon
safety check
```

## Development Guidelines

### Agentic Workflow Design
- **Agent Architecture**: Design the Rekon agent system with specialized sub-agents (Rekon-RegulationParser, Rekon-ComplianceChecker, Rekon-GapIdentifier, Rekon-RemediationEngine)
- **Primary Agent**: The main "Rekon" agent orchestrates workflow and delegates to specialized sub-agents
- **Orchestration**: Use AWS Step Functions or EventBridge for Rekon multi-agent workflow orchestration
- **Agent Communication**: Implement event-driven communication between Rekon agents via EventBridge/SQS
- **State Management**: Maintain Rekon agent state in DynamoDB with TTL for session management
- **Error Recovery**: Implement retry logic with exponential backoff and dead-letter queues for Rekon agents
- **Observability**: Comprehensive CloudWatch logging and X-Ray tracing for Rekon agent decisions

### AWS Bedrock Agent Development
- **Primary Agent**: Create the main "Rekon" agent using Bedrock AgentCore as the orchestrator
- **Sub-Agent Specialization**: Create focused Rekon sub-agents for specific compliance tasks
- **Knowledge Base Integration**: Use Bedrock Knowledge Bases with RAG for regulatory documents in Rekon agents
- **Tool Use**: Implement function calling for agent tool usage (Lambda integration)
- **Memory Management**: Use Bedrock Conversation Memory for agent context preservation
- **Guardrails**: Implement Bedrock Guardrails for content filtering and compliance
- **Multi-modal Support**: Plan for document processing with Amazon Textract integration

### Serverless Agent Architecture
- **Lambda Functions**: Stateless, event-driven Lambda functions (Python 3.9+)
- **Step Functions**: Orchestrate complex regulatory compliance workflows
- **EventBridge**: Event-driven communication between compliance agents
- **SQS/SNS**: Asynchronous message passing for agent coordination
- **DynamoDB Streams**: Real-time updates for compliance state changes

### Security & Compliance (Critical for Audit Platform)
- **Bedrock Guardrails**: Content filtering, PII detection, and safety checks
- **Data Privacy**: Implement PII redaction and data anonymization for sensitive information
- **Compliance Logging**: Immutable audit trails for all agent decisions in CloudWatch Logs
- **Access Control**: IAM roles with least privilege and Bedrock access policies
- **Encryption**: KMS encryption for data at rest (S3, RDS) and in transit
- **Compliance Evidence**: Automated evidence collection and storage in S3 with versioning

### Performance Optimization for Compliance Workloads
- **Lambda Optimization**: Right-size memory (1-3GB) for Bedrock model inference
- **Caching Strategy**: Use ElastiCache Redis for agent context and regulation caching
- **Concurrency**: Implement agent concurrency with Step Functions map states
- **Cold Start Optimization**: Provisioned concurrency for critical compliance agents
- **Cost Optimization**: Spot instances for non-critical agents, reserved capacity for production

### Monitoring & Observability for Agent Workflows
- **CloudWatch Metrics**: Agent invocation counts, error rates, Bedrock token usage
- **X-Ray Tracing**: End-to-end tracing of compliance assessment workflows
- **CloudWatch Logs**: Structured JSON logging for agent decisions and regulatory citations
- **Custom Metrics**: Business metrics (compliance score, gap count, remediation progress)
- **Dashboarding**: CloudWatch dashboards for agent health and compliance status

### Testing Strategy for Agentic Systems
- **Unit Tests**: Mock Bedrock and AWS services with moto and boto3 stubs
- **Integration Tests**: Test agent workflows with Step Functions Local and SAM Local
- **Property Tests**: Hypothesis for testing agent behavior properties and compliance rules
- **Load Testing**: Load test compliance workflows with varying regulatory document sizes
- **Chaos Testing**: Test agent resilience to AWS service failures (Bedrock, Lambda, etc.)

### Deployment & CI/CD for Agent Infrastructure
- **Infrastructure as Code**: AWS CDK (Python) for agent infrastructure definition
- **Blue/Green Deployments**: Canary deployments for agent updates with traffic shifting
- **Feature Flags**: Control agent behavior with AWS AppConfig feature flags
- **Canary Analysis**: Monitor agent performance and compliance accuracy in production
- **Rollback Strategies**: Automated rollback on agent failures or compliance regressions

### Cost Optimization & Governance
- **Lambda Concurrency**: Right-size based on compliance assessment volume
- **Bedrock Pricing**: Optimize for token usage and model selection (Claude vs. Llama)
- **Data Transfer**: Minimize data transfer between AWS services (use VPC endpoints)
- **Reserved Capacity**: Reserved concurrency for critical compliance assessment agents
- **Cost Allocation**: Tag-based cost allocation by regulatory framework and business unit

### Regulatory Framework Integration
- **Regulation Ingestion**: Automated fetching from official regulatory sources
- **Framework Mapping**: Cross-reference requirements across DORA, SOX, BMR, IOSCO, NIST
- **Compliance Tracking**: Real-time compliance status tracking with evidence linking
- **Audit Trail**: Immutable audit trail for all compliance assessments and changes
- **Reporting**: Automated compliance reporting with executive dashboards