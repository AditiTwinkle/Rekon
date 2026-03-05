"""Custom exceptions for Rekon application."""


class RekonException(Exception):
    """Base exception for all Rekon errors."""

    def __init__(self, code: str, message: str, details: dict | None = None):
        """Initialize exception.

        Args:
            code: Error code identifier
            message: Human-readable error message
            details: Additional error details
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class RegulationFetchError(RekonException):
    """Raised when regulation fetching fails."""

    def __init__(self, framework: str, message: str, details: dict | None = None):
        """Initialize exception."""
        super().__init__(
            code="REGULATION_FETCH_ERROR",
            message=f"Failed to fetch {framework} regulations: {message}",
            details={"framework": framework, **(details or {})},
        )


class ChecklistGenerationError(RekonException):
    """Raised when checklist generation fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize exception."""
        super().__init__(
            code="CHECKLIST_GENERATION_ERROR",
            message=f"Checklist generation failed: {message}",
            details=details or {},
        )


class DeltaAnalysisError(RekonException):
    """Raised when delta analysis fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize exception."""
        super().__init__(
            code="DELTA_ANALYSIS_ERROR",
            message=f"Delta analysis failed: {message}",
            details=details or {},
        )


class GapAssessmentError(RekonException):
    """Raised when gap assessment fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize exception."""
        super().__init__(
            code="GAP_ASSESSMENT_ERROR",
            message=f"Gap assessment failed: {message}",
            details=details or {},
        )


class RemediationError(RekonException):
    """Raised when remediation generation fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize exception."""
        super().__init__(
            code="REMEDIATION_ERROR",
            message=f"Remediation generation failed: {message}",
            details=details or {},
        )


class DatabaseError(RekonException):
    """Raised when database operations fail."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize exception."""
        super().__init__(
            code="DATABASE_ERROR",
            message=f"Database operation failed: {message}",
            details=details or {},
        )


class AuthenticationError(RekonException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", details: dict | None = None):
        """Initialize exception."""
        super().__init__(
            code="AUTHENTICATION_ERROR",
            message=message,
            details=details or {},
        )


class AuthorizationError(RekonException):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Insufficient permissions", details: dict | None = None):
        """Initialize exception."""
        super().__init__(
            code="AUTHORIZATION_ERROR",
            message=message,
            details=details or {},
        )


class ValidationError(RekonException):
    """Raised when validation fails."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize exception."""
        super().__init__(
            code="VALIDATION_ERROR",
            message=f"Validation failed: {message}",
            details=details or {},
        )
