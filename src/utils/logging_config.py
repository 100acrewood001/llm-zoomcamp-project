"""
Structured logging configuration for Annual Report Analyzer.
Provides consistent logging across all components with JSON formatting.
"""

import logging
import structlog
import sys
from typing import Any, Dict
from pathlib import Path


def setup_logging(
    level: str = "INFO", 
    log_file: str = None,
    format_type: str = "json"
) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        format_type: Format type ("json" or "console")
    """
    
    # Ensure logs directory exists
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Configure standard logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[]
    )
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Add file handler if specified
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        handlers.append(file_handler)
    
    # Configure structlog
    if format_type == "json":
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ]
    else:
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers = handlers


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)


def log_function_call(func_name: str, **kwargs) -> Dict[str, Any]:
    """
    Create a log context for function calls.
    
    Args:
        func_name: Name of the function being called
        **kwargs: Additional context to log
        
    Returns:
        Dictionary with logging context
    """
    return {
        "function": func_name,
        "context": kwargs
    }


def log_performance(operation: str, duration: float, **kwargs) -> Dict[str, Any]:
    """
    Create a log context for performance metrics.
    
    Args:
        operation: Name of the operation
        duration: Duration in seconds
        **kwargs: Additional metrics
        
    Returns:
        Dictionary with performance logging context
    """
    return {
        "operation": operation,
        "duration_seconds": duration,
        "metrics": kwargs
    }


def log_error(error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create a log context for errors.
    
    Args:
        error: Exception that occurred
        context: Additional context about the error
        
    Returns:
        Dictionary with error logging context
    """
    return {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {}
    }


# Pre-configured loggers for common use cases
azure_logger = get_logger("azure")
rag_logger = get_logger("rag") 
api_logger = get_logger("api")
extract_logger = get_logger("extractor")


if __name__ == "__main__":
    # Test logging configuration
    setup_logging(level="DEBUG", format_type="console")
    
    test_logger = get_logger("test")
    
    test_logger.info("Testing structured logging", component="test", status="success")
    test_logger.warning("This is a warning", warning_type="test")
    test_logger.error("This is an error", error_code=500)
    
    # Test performance logging
    import time
    start_time = time.time()
    time.sleep(0.1)
    duration = time.time() - start_time
    
    test_logger.info(
        "Performance test completed",
        **log_performance("test_operation", duration, items_processed=100)
    )
