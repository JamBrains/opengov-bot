#!/usr/bin/env python
"""
Test runner for JAM DAO Discord Bot.

This module provides functions for running various types of tests for the bot.
"""

import os
import sys
import unittest
import signal
import time
import contextlib
import types
from unittest.mock import patch, MagicMock

# Add the project root to the path so we can import our modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


def setup_discord_mocks():
    """Set up mocks for Discord modules

    Returns:
        list: List of patches that have been started
    """
    # Create mock objects
    discord_mock = MagicMock()
    discord_intents_mock = MagicMock()
    discord_file_mock = MagicMock()

    # Create Bot class for discord.ext.commands
    class MockBot(MagicMock):
        def __init__(self, *args, **kwargs):
            super().__init__()
            self.commands = {}

        def add_command(self, name, func=None):
            if func is None and isinstance(name, str):
                # Used as a decorator
                def decorator(func):
                    self.commands[name] = func
                    return func
                return decorator
            else:
                # Used directly
                self.commands[name] = func

        async def process_commands(self, message):
            pass

        async def on_ready(self):
            pass

    # Create mock modules for discord.ext
    discord_ext_mock = types.ModuleType('discord.ext')
    discord_ext_commands_mock = types.ModuleType('discord.ext.commands')
    discord_ext_tasks_mock = types.ModuleType('discord.ext.tasks')

    # Create Loop class for discord.ext.tasks
    class MockLoop:
        def __init__(self, *args, **kwargs):
            pass

        def __call__(self, func):
            self.func = func
            return self

        def start(self):
            pass

        def stop(self):
            pass

        def is_running(self):
            return False

        def before_loop(self, func):
            self.before_func = func
            return func

        def after_loop(self, func):
            self.after_func = func
            return func

        def error(self, func):
            self.error_func = func
            return func

    # Add Loop class to discord.ext.tasks
    discord_ext_tasks_mock.Loop = MockLoop
    discord_ext_tasks_mock.loop = MockLoop

    # Add Bot class to discord.ext.commands
    discord_ext_commands_mock.Bot = MockBot

    # Set up the module hierarchy
    sys.modules['discord.ext'] = discord_ext_mock
    sys.modules['discord.ext.commands'] = discord_ext_commands_mock
    sys.modules['discord.ext.tasks'] = discord_ext_tasks_mock

    # Create patches
    patches = [
        patch('discord.Client', discord_mock),
        patch('discord.Intents', discord_intents_mock),
        patch('discord.File', discord_file_mock)
    ]

    # Start all patches
    for p in patches:
        p.start()

    return patches


@contextlib.contextmanager
def suppress_stdout_stderr(suppress=True):
    """Context manager to suppress stdout and stderr output.

    Args:
        suppress (bool): Whether to suppress output or not
    """
    if suppress:
        with open(os.devnull, 'w') as devnull:
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = devnull
            sys.stderr = devnull
            try:
                yield
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
    else:
        yield


@contextlib.contextmanager
def test_timeout(seconds):
    """Context manager to timeout a test after a specified number of seconds.

    Args:
        seconds (int): Number of seconds to wait before timing out
    """
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Test timed out after {seconds} seconds")

    # Save the original handler
    original_handler = signal.getsignal(signal.SIGALRM)

    # Set the alarm
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        # Cancel the alarm and restore the original handler
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_handler)


def run_unit_tests(quiet=False, timeout=60):
    """Run all unit tests

    Args:
        quiet (bool): Whether to suppress output
        timeout (int): Number of seconds to wait before timing out

    Returns:
        bool: True if all tests passed, False otherwise
    """
    print("Running unit tests...")

    # Discover and run unit tests
    loader = unittest.TestLoader()
    unit_test_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test', 'unit')
    suite = loader.discover(unit_test_dir, pattern="test_*.py")

    try:
        with test_timeout(timeout):
            with suppress_stdout_stderr(suppress=quiet):
                runner = unittest.TextTestRunner(verbosity=2)
                result = runner.run(suite)

        return result.wasSuccessful()
    except TimeoutError as e:
        print(f"Error: {e}")
        return False


def run_integration_tests(quiet=False, timeout=60):
    """Run all integration tests

    Args:
        quiet (bool): Whether to suppress output
        timeout (int): Number of seconds to wait before timing out

    Returns:
        bool: True if all tests passed, False otherwise
    """
    print("Running integration tests...")

    # Discover and run integration tests
    loader = unittest.TestLoader()
    integration_test_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test', 'integration')
    suite = loader.discover(integration_test_dir, pattern="test_*.py")

    try:
        with test_timeout(timeout):
            with suppress_stdout_stderr(suppress=quiet):
                runner = unittest.TextTestRunner(verbosity=2)
                result = runner.run(suite)

        return result.wasSuccessful()
    except TimeoutError as e:
        print(f"Error: {e}")
        return False


def run_scheduled_tasks_tests(quiet=False, timeout=60):
    """Run tests for scheduled_tasks.py

    Args:
        quiet (bool): Whether to suppress output
        timeout (int): Number of seconds to wait before timing out

    Returns:
        bool: True if all tests passed, False otherwise
    """
    print("Running scheduled_tasks.py tests...")

    # Check if we should use real API or mocks
    use_real_api = os.getenv('USE_REAL_APIS', 'false').lower() == 'true'

    if not use_real_api:
        # Set up mocks for discord modules
        patches = setup_discord_mocks()

    try:
        # Import and run tests
        from bot.test import scheduled_tasks

        # Create a test suite for just this module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(scheduled_tasks)

        with test_timeout(timeout):
            # Run the tests with output suppression if quiet mode is enabled
            with suppress_stdout_stderr(suppress=quiet):
                runner = unittest.TextTestRunner(verbosity=2)
                result = runner.run(suite)

        return result.wasSuccessful()
    except TimeoutError as e:
        print(f"Error: {e}")
        return False
    finally:
        if not use_real_api:
            # Stop all patches
            for p in patches:
                p.stop()


def run_ongoing_ref_tests(quiet=False, timeout=60):
    """Run tests for ongoing_ref_call_data.py

    Args:
        quiet (bool): Whether to suppress output
        timeout (int): Number of seconds to wait before timing out

    Returns:
        bool: True if all tests passed, False otherwise
    """
    print("Running ongoing_ref_call_data.py tests...")

    # Check if we should use real API or mocks
    use_real_api = os.getenv('USE_REAL_APIS', 'false').lower() == 'true'

    # Set up environment variables for testing
    os.environ['DISCORD_TOKEN'] = 'mock_token_for_testing'

    if not use_real_api:
        # Set up mocks for Discord modules
        discord_patches = setup_discord_mocks()

        # Set up additional mocks for APIs used in ongoing_ref_call_data.py
        api_patches = [
            patch('requests.get', MagicMock()),
            patch('substrateinterface.SubstrateInterface', MagicMock()),
            patch('discord.client.Client.run', MagicMock())  # Prevent actual Discord connection
        ]

        # Start API patches
        for p in api_patches:
            p.start()

        # Combine all patches
        patches = discord_patches + api_patches

    try:
        # Import and run tests
        from bot.test import ongoing_ref_call_data

        # Create a test suite for just this module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(ongoing_ref_call_data)

        with test_timeout(timeout):
            # Run the tests with output suppression if quiet mode is enabled
            with suppress_stdout_stderr(suppress=quiet):
                runner = unittest.TextTestRunner(verbosity=2)
                result = runner.run(suite)

        return result.wasSuccessful()
    except TimeoutError as e:
        print(f"Error: {e}")
        return False
    finally:
        if not use_real_api:
            # Stop all patches
            for p in patches:
                p.stop()
