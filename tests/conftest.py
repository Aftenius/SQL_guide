"""Pytest configuration."""

from sql_guide.infrastructure.event_loop import use_selector_event_loop

use_selector_event_loop()
