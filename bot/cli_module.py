#!/usr/bin/env python
"""
Unified command-line interface for JAM DAO Discord Bot.

This script provides a central entry point for various bot operations including:
- Running tests (unit, integration, API)
- Starting/stopping the bot
- Managing configuration
- Performing maintenance tasks

Usage:
    python -m bot [command] [options]

Commands:
    test        Run tests for the bot
    test-env    Run the bot in a test environment
    start       Start the bot
    config      Manage bot configuration
    help        Show help information

For detailed help on a specific command, use:
    python -m bot [command] --help
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Add the project root to the path so we can import our modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Load environment variables from .env file
load_dotenv()


def setup_test_parser(subparsers):
    """Set up the parser for the test command"""
    test_parser = subparsers.add_parser('test', help='Run tests for the bot')
    test_parser.add_argument('--unit', action='store_true', help='Run all unit tests')
    test_parser.add_argument('--integration', action='store_true', help='Run all integration tests')
    test_parser.add_argument('--api', action='store_true', help='Run all API-dependent tests')
    test_parser.add_argument('--scheduled-tasks', action='store_true', help='Run tests for scheduled_tasks.py')
    test_parser.add_argument('--ongoing-ref', action='store_true', help='Run tests for ongoing_ref_call_data.py')
    test_parser.add_argument('--all', action='store_true', help='Run all tests')
    test_parser.add_argument('--use-real-apis', action='store_true', help='Use real APIs instead of mocks (requires API credentials)')
    test_parser.add_argument('--timeout', type=int, default=60, help='Timeout for tests in seconds (default: 60)')
    test_parser.add_argument('--quiet', action='store_true', help='Suppress output from tests')


def setup_test_env_parser(subparsers):
    """Set up the parser for the test-env command"""
    test_env_parser = subparsers.add_parser('test-env', help='Run the bot in a test environment with simulated Discord server')
    test_env_parser.add_argument('--scenario', choices=['default', 'voting', 'custom'], default='default',
                               help='Test scenario to run (default: default)')
    test_env_parser.add_argument('--debug', action='store_true', help='Enable debug output')
    test_env_parser.add_argument('--duration', type=int, default=60,
                               help='Duration to run the test environment in seconds (default: 60)')


def setup_start_parser(subparsers):
    """Set up the parser for the start command"""
    start_parser = subparsers.add_parser('start', help='Start the bot')
    start_parser.add_argument('--dev', action='store_true', help='Start in development mode')
    start_parser.add_argument('--debug', action='store_true', help='Enable debug logging')


def setup_config_parser(subparsers):
    """Set up the parser for the config command"""
    config_parser = subparsers.add_parser('config', help='Manage bot configuration')
    config_parser.add_argument('--list', action='store_true', help='List current configuration')
    config_parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='Set a configuration value')
    config_parser.add_argument('--get', metavar='KEY', help='Get a configuration value')


def handle_test_command(args):
    """Handle the test command"""
    from bot.cli.test_runner import (
        run_unit_tests,
        run_integration_tests,
        run_scheduled_tasks_tests,
        run_ongoing_ref_tests
    )

    # Set environment variable for real API usage if specified
    if args.use_real_apis:
        os.environ['USE_REAL_APIS'] = 'true'
    else:
        os.environ['USE_REAL_APIS'] = 'false'

    # Track overall success
    success = True

    # Track test runs
    test_runs = []

    # Run the specified tests
    if args.unit or args.all:
        unit_success = run_unit_tests(quiet=args.quiet, timeout=args.timeout)
        test_runs.append(("Unit Tests", unit_success))
        if not unit_success:
            success = False

    if args.integration or args.all:
        integration_success = run_integration_tests(quiet=args.quiet, timeout=args.timeout)
        test_runs.append(("Integration Tests", integration_success))
        if not integration_success:
            success = False

    if args.scheduled_tasks or args.api or args.all:
        scheduled_tasks_success = run_scheduled_tasks_tests(quiet=args.quiet, timeout=args.timeout)
        test_runs.append(("Scheduled Tasks Tests", scheduled_tasks_success))
        if not scheduled_tasks_success:
            success = False

    if args.ongoing_ref or args.api or args.all:
        ongoing_ref_success = run_ongoing_ref_tests(quiet=args.quiet, timeout=args.timeout)
        test_runs.append(("Ongoing Ref Tests", ongoing_ref_success))
        if not ongoing_ref_success:
            success = False

    # If no specific tests were specified, run unit tests by default
    if not (args.unit or args.integration or args.api or args.scheduled_tasks or args.ongoing_ref or args.all):
        unit_success = run_unit_tests(quiet=args.quiet, timeout=args.timeout)
        test_runs.append(("Unit Tests", unit_success))
        if not unit_success:
            success = False

    # Print summary with emoji indicators
    print("\n" + "-" * 40)
    print("📋 Test Summary:")
    for test_name, test_success in test_runs:
        emoji = "✅" if test_success else "❌"
        print(f"{emoji} {test_name}: {'PASSED' if test_success else 'FAILED'}")
    print("-" * 40)
    print(f"{'✅ All tests passed!' if success else '❌ Some tests failed!'}")

    return 0 if success else 1


def handle_test_env_command(args):
    """Handle the test-env command"""
    print(f"Starting JAM DAO Discord Bot in test environment with scenario: {args.scenario}")

    if args.debug:
        print("Debug output enabled")
        # Set debug environment variable
        os.environ['DEBUG'] = 'true'

    # Set scenario environment variable
    os.environ['TEST_SCENARIO'] = args.scenario

    # Set duration environment variable if specified
    if args.duration:
        os.environ['TEST_DURATION'] = str(args.duration)

    # Import and run the test environment
    from bot.cli.test_env import main as run_test_env
    run_test_env()

    return 0


def handle_start_command(args):
    """Handle the start command"""
    print("Starting JAM DAO Discord Bot...")

    if args.dev:
        print("Development mode enabled")

    if args.debug:
        print("Debug logging enabled")

    # TODO: Implement bot startup logic
    print("Bot startup not yet implemented")

    return 0


def handle_config_command(args):
    """Handle the config command"""
    if args.list:
        print("Listing configuration...")
        # TODO: Implement configuration listing
    elif args.set:
        key, value = args.set
        print(f"Setting {key}={value}...")
        # TODO: Implement configuration setting
    elif args.get:
        print(f"Getting value for {args.get}...")
        # TODO: Implement configuration getting
    else:
        print("No config action specified. Use --list, --set, or --get")

    return 0


def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        prog='bot',
        description='JAM DAO Discord Bot CLI'
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Set up command parsers
    setup_test_parser(subparsers)
    setup_test_env_parser(subparsers)
    setup_start_parser(subparsers)
    setup_config_parser(subparsers)

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == 'test':
        return handle_test_command(args)
    elif args.command == 'test-env':
        return handle_test_env_command(args)
    elif args.command == 'start':
        return handle_start_command(args)
    elif args.command == 'config':
        return handle_config_command(args)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
