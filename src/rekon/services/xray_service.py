"""X-Ray tracing service for distributed tracing."""

import logging
from typing import Dict, Any, Optional
from functools import wraps

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

logger = logging.getLogger(__name__)

# Patch AWS SDK and other libraries
patch_all()


class XRayService:
    """Service for X-Ray distributed tracing."""

    @staticmethod
    def configure_xray(service_name: str) -> None:
        """Configure X-Ray recorder.

        Args:
            service_name: Service name for X-Ray
        """
        try:
            xray_recorder.configure(
                service=service_name,
                context_missing="LOG_ERROR",
            )
            logger.info(f"X-Ray configured for service: {service_name}")
        except Exception as e:
            logger.error(f"Error configuring X-Ray: {str(e)}")

    @staticmethod
    def trace_function(name: str):
        """Decorator to trace function execution.

        Args:
            name: Segment name

        Returns:
            Decorator function
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                with xray_recorder.capture(name):
                    return func(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def trace_async_function(name: str):
        """Decorator to trace async function execution.

        Args:
            name: Segment name

        Returns:
            Decorator function
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                with xray_recorder.capture(name):
                    return await func(*args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def add_annotation(key: str, value: Any) -> None:
        """Add annotation to current segment.

        Args:
            key: Annotation key
            value: Annotation value
        """
        try:
            xray_recorder.current_segment().put_annotation(key, value)
        except Exception as e:
            logger.debug(f"Error adding annotation: {str(e)}")

    @staticmethod
    def add_metadata(key: str, value: Any) -> None:
        """Add metadata to current segment.

        Args:
            key: Metadata key
            value: Metadata value
        """
        try:
            xray_recorder.current_segment().put_metadata(key, value)
        except Exception as e:
            logger.debug(f"Error adding metadata: {str(e)}")

    @staticmethod
    def trace_compliance_operation(
        operation_name: str,
        organization_id: str,
        framework: Optional[str] = None,
    ):
        """Context manager for tracing compliance operations.

        Args:
            operation_name: Operation name
            organization_id: Organization ID
            framework: Optional framework

        Yields:
            Segment for additional tracing
        """
        with xray_recorder.capture(operation_name) as segment:
            segment.put_annotation("organization_id", organization_id)
            if framework:
                segment.put_annotation("framework", framework)
            yield segment

    @staticmethod
    def trace_database_operation(
        operation_name: str,
        table_name: str,
    ):
        """Context manager for tracing database operations.

        Args:
            operation_name: Operation name (SELECT, INSERT, UPDATE, DELETE)
            table_name: Table name

        Yields:
            Segment for additional tracing
        """
        with xray_recorder.capture(f"database_{operation_name}") as segment:
            segment.put_annotation("operation", operation_name)
            segment.put_annotation("table", table_name)
            yield segment

    @staticmethod
    def trace_external_api_call(
        api_name: str,
        endpoint: str,
    ):
        """Context manager for tracing external API calls.

        Args:
            api_name: API name
            endpoint: API endpoint

        Yields:
            Segment for additional tracing
        """
        with xray_recorder.capture(f"external_api_{api_name}") as segment:
            segment.put_annotation("api", api_name)
            segment.put_annotation("endpoint", endpoint)
            yield segment

    @staticmethod
    def trace_bedrock_agent_invocation(
        agent_name: str,
        agent_id: str,
    ):
        """Context manager for tracing Bedrock agent invocations.

        Args:
            agent_name: Agent name
            agent_id: Agent ID

        Yields:
            Segment for additional tracing
        """
        with xray_recorder.capture(f"bedrock_agent_{agent_name}") as segment:
            segment.put_annotation("agent_name", agent_name)
            segment.put_annotation("agent_id", agent_id)
            yield segment

    @staticmethod
    def trace_lambda_invocation(
        function_name: str,
        request_id: str,
    ):
        """Context manager for tracing Lambda invocations.

        Args:
            function_name: Lambda function name
            request_id: Request ID

        Yields:
            Segment for additional tracing
        """
        with xray_recorder.capture(f"lambda_{function_name}") as segment:
            segment.put_annotation("function", function_name)
            segment.put_annotation("request_id", request_id)
            yield segment

    @staticmethod
    def record_exception(exception: Exception, message: str = "") -> None:
        """Record exception in X-Ray.

        Args:
            exception: Exception to record
            message: Optional message
        """
        try:
            xray_recorder.current_segment().add_exception(exception)
            if message:
                xray_recorder.current_segment().put_metadata(
                    "error_message",
                    message,
                )
        except Exception as e:
            logger.debug(f"Error recording exception: {str(e)}")

    @staticmethod
    def record_error(error_code: str, error_message: str) -> None:
        """Record error in X-Ray.

        Args:
            error_code: Error code
            error_message: Error message
        """
        try:
            segment = xray_recorder.current_segment()
            segment.put_annotation("error_code", error_code)
            segment.put_metadata("error_message", error_message)
        except Exception as e:
            logger.debug(f"Error recording error: {str(e)}")

    @staticmethod
    def record_performance_metric(
        metric_name: str,
        value: float,
        unit: str = "ms",
    ) -> None:
        """Record performance metric in X-Ray.

        Args:
            metric_name: Metric name
            value: Metric value
            unit: Unit of measurement
        """
        try:
            xray_recorder.current_segment().put_metadata(
                f"performance_{metric_name}",
                {"value": value, "unit": unit},
            )
        except Exception as e:
            logger.debug(f"Error recording metric: {str(e)}")
