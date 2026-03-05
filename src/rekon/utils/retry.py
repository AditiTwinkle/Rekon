"""Retry utilities with exponential backoff."""

import logging
import time
from functools import wraps
from typing import Callable, Type, Tuple, Optional

logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """Decorator for retrying functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exceptions: Tuple of exceptions to catch

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            last_exception = None

            while attempt < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    attempt += 1

                    if attempt >= max_retries:
                        logger.error(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}"
                        )
                        raise

                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    logger.warning(
                        f"Attempt {attempt} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)

            raise last_exception

        return wrapper

    return decorator


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
    ):
        """Initialize retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number.

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        delay = self.base_delay * (2 ** attempt)
        return min(delay, self.max_delay)
