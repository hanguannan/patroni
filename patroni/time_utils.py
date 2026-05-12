"""Time utilities for Patroni.

This module provides time-related functions to handle system time and monotonic time
appropriately for different use cases in Patroni.

Key Principles:
1. Use monotonic time for internal calculations, timeouts, and state duration tracking
2. Use system time for display purposes, DCS timestamps, and cross-node comparisons
3. Monotonic time is immune to system time jumps (NTP adjustments, manual changes, etc.)
4. System time should be used when the absolute time matters across different nodes
"""

import time
from typing import Optional
from datetime import datetime, timezone


def get_monotonic_time() -> float:
    """Get the current monotonic time.

    Monotonic time is immune to system time jumps and should be used for:
    - Timeout calculations and deadline tracking
    - State duration measurements
    - Relative time differences
    - Scheduling and loop timing
    - Internal coordination logic

    Returns:
        float: Current monotonic time in seconds as a floating point number.
               The absolute value is meaningless; only differences between calls matter.
    """
    return time.monotonic()


def get_system_time() -> float:
    """Get the current system time (wall-clock time).

    System time represents the actual real-world time and should be used for:
    - User-facing displays (logs, API responses, CLI output)
    - DCS timestamps that need to be comparable across different nodes
    - Scheduled events that need to happen at specific real-world times
    - Backup/restore timestamps
    - Any time value that will be serialized and shared externally

    Note: System time can jump forward or backward due to NTP adjustments,
    manual time changes, timezone changes, etc.

    Returns:
        float: Current system time in seconds since the Unix epoch (Jan 1, 1970).
    """
    return time.time()


def get_system_datetime(tz: Optional[timezone] = None) -> datetime:
    """Get the current system time as a datetime object.

    This should be used for display purposes and when you need a datetime object
    instead of a raw timestamp.

    Args:
        tz: Optional timezone. If None, uses the system's local timezone.
            For Patroni internal use, typically timezone.utc is recommended.

    Returns:
        datetime: Current system time as a datetime object.
    """
    if tz is None:
        return datetime.now()
    return datetime.now(tz)


def create_timeout_deadline(timeout_seconds: float) -> float:
    """Create a deadline timestamp from a timeout value.

    This uses monotonic time to create a deadline that is immune to system time jumps.

    Args:
        timeout_seconds: Number of seconds from now until the deadline.

    Returns:
        float: A monotonic timestamp that represents the deadline.
    """
    return get_monotonic_time() + timeout_seconds


def get_timeout_remaining(deadline: float) -> float:
    """Get the remaining time until a deadline.

    Args:
        deadline: A monotonic timestamp created by create_timeout_deadline().

    Returns:
        float: Number of seconds remaining until the deadline.
               Returns 0 if the deadline has already passed.
    """
    remaining = deadline - get_monotonic_time()
    return max(0.0, remaining)


def format_timestamp_for_display(timestamp: float, precision: int = 23) -> str:
    """Format a system timestamp for human-readable display.

    Args:
        timestamp: A system timestamp from get_system_time().
        precision: Maximum number of characters to return (default: 23).
                   The format is "YYYY-MM-DD HH:MM:SS.ffffff".

    Returns:
        str: Formatted timestamp string.
    """
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')[:precision - 7]
