"""
Context utilities for getting environment and system information
"""

import os
import platform
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional


def get_working_directory() -> str:
    """Get current working directory"""
    return os.getcwd()


def is_directory_a_git_repo() -> str:
    """Check if current directory is a git repository"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        return "Yes" if result.returncode == 0 else "No"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "No"


def get_platform() -> str:
    """Get platform information"""
    return platform.system()


def get_os_version() -> str:
    """Get OS version information"""
    try:
        return platform.platform()
    except Exception:
        return "Unknown"


def get_today_date() -> str:
    """Get today's date"""
    return datetime.now().strftime("%Y-%m-%d")


def get_last_5_recent_commits() -> str:
    """Get last 5 recent commits from git"""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "No commits found"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "Git not available"


def get_context_variables() -> Dict[str, Any]:
    """Get all context variables needed for lead agent prompt"""
    return {
        "working_directory": get_working_directory(),
        "is_directory_a_git_repo": is_directory_a_git_repo(),
        "platform": get_platform(),
        "os_version": get_os_version(),
        "today_date": get_today_date(),
        "last_5_recent_commits": get_last_5_recent_commits(),
    }


def get_context_variable(key: str, default: str = "Unknown") -> str:
    """Get a specific context variable"""
    context = get_context_variables()
    return context.get(key, default)
