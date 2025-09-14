"""
Centralized logging configuration for Claude-Code-Python
"""

import logging
import sys
from typing import Optional
from datetime import datetime
import os


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to the level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logger(
    name: str = "claude_code",
    level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True,
    enable_colors: bool = True
) -> logging.Logger:
    """
    Set up a logger with console and optional file output
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        enable_console: Whether to enable console output
        enable_colors: Whether to use colored output (console only)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Set level
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create formatters
    if enable_colors and enable_console:
        console_formatter = ColoredFormatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
    
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name (defaults to 'claude_code')
    
    Returns:
        Logger instance
    """
    if name is None:
        name = "claude_code"
    
    return logging.getLogger(name)


def log_function_call(logger: logging.Logger, func_name: str, **kwargs):
    """
    Log a function call with parameters
    
    Args:
        logger: Logger instance
        func_name: Function name
        **kwargs: Function parameters to log
    """
    params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.debug(f"Calling {func_name}({params})")


def log_function_result(logger: logging.Logger, func_name: str, result: any, success: bool = True):
    """
    Log a function result
    
    Args:
        logger: Logger instance
        func_name: Function name
        result: Function result
        success: Whether the function succeeded
    """
    level = logging.INFO if success else logging.ERROR
    result_str = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
    logger.log(level, f"{func_name} result: {result_str}")


def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """
    Log an error with context
    
    Args:
        logger: Logger instance
        error: Exception to log
        context: Additional context
    """
    context_str = f" in {context}" if context else ""
    logger.error(f"Error{context_str}: {str(error)}", exc_info=True)


def log_performance(logger: logging.Logger, operation: str, duration: float, **kwargs):
    """
    Log performance metrics
    
    Args:
        logger: Logger instance
        operation: Operation name
        duration: Duration in seconds
        **kwargs: Additional metrics
    """
    metrics = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.info(f"Performance | {operation} took {duration:.3f}s | {metrics}")


# Initialize default logger
default_logger = setup_logger(
    level=os.getenv("CLAUDE_CODE_LOG_LEVEL", "INFO"),
    log_file=os.getenv("CLAUDE_CODE_LOG_FILE", "logs/claude_code.log"),
    enable_console=True,
    enable_colors=True
)
