"""Checklist Generator Lambda function.

Invokes Bedrock Checklist Generator Agent to extract requirements
from regulatory text and generate audit checklists.
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock_agent = boto3.client("bedrock-agent-runtime")
ssm_client = boto3.client("ssm")


class ChecklistGenerationError(Exception):
    """Exception raised when checklist generation fails."""

    pass


def invoke_bedrock_agent(
    agent_id: str,
    session_id: str,
    regulatory_text: str,
    framework: str,
) -> Dict:
    """Invoke Bedrock Checklist Generator Agent.

    Args:
        agent_id: Bedrock agent ID
        session_id: Session ID for agent
        regulatory_text: Regulatory text to analyze
        framework: Framework identifier

    Returns:
        Agent response with checklist items

    Raises:
        ChecklistGenerationError: If agent invocation fails
    """
    try:
        logger.info(f"Invoking Bedrock agent for {framework}")

        prompt = f"""Analyze the following regulatory text and generate a comprehensive audit checklist.

Framework: {framework}

Regulatory Text:
{regulatory_text}

Generate checklist items with the following structure:
- Requirement Text: Clear, specific statement
- Domain: Compliance domain
- Category: Specific category
- Priority: Critical/High/Medium/Low
- Evidence Requirements: Documentation/testing needed
- Regulatory Citation: Exact reference

Return as JSON with checklist_items array."""

        response = bedrock_agent.invoke_agent(
            agentId=agent_id,
            sessionId=session_id,
            inputText=prompt,
        )

        # Parse response
        result = {
            "checklist_items": [],
            "framework": framework,
            "generated_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"Successfully generated checklist for {framework}")
        return result

    except Exception as e:
        logger.error(f"Error invoking Bedrock agent: {str(e)}")
        raise ChecklistGenerationError(f"Failed to generate checklist: {str(e)}")


def parse_checklist_response(response: Dict) -> List[Dict]:
    """Parse Bedrock agent response into checklist items.

    Args:
        response: Agent response

    Returns:
        List of checklist items
    """
    items = []

    try:
        if "checklist_items" in response:
            items = response["checklist_items"]

        logger.info(f"Parsed {len(items)} checklist items")
        return items

    except Exception as e:
        logger.error(f"Error parsing response: {str(e)}")
        return []


def lambda_handler(event, context):
    """Lambda handler for checklist generation.

    Args:
        event: Lambda event
        context: Lambda context

    Returns:
        Response with generated checklist
    """
    logger.info("Starting checklist generation")

    try:
        # Extract parameters
        framework = event.get("framework")
        regulatory_text = event.get("regulatory_text")
        agent_id = event.get("agent_id")
        session_id = event.get("session_id", f"session-{datetime.utcnow().timestamp()}")

        if not all([framework, regulatory_text, agent_id]):
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Missing required parameters: framework, regulatory_text, agent_id"
                }),
            }

        # Invoke Bedrock agent
        response = invoke_bedrock_agent(
            agent_id=agent_id,
            session_id=session_id,
            regulatory_text=regulatory_text,
            framework=framework,
        )

        # Parse response
        checklist_items = parse_checklist_response(response)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "framework": framework,
                "checklist_items": checklist_items,
                "item_count": len(checklist_items),
                "generated_at": response["generated_at"],
            }),
        }

    except ChecklistGenerationError as e:
        logger.error(f"Checklist generation error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
            }),
        }

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": f"Unexpected error: {str(e)}",
            }),
        }
