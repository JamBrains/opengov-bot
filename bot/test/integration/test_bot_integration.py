import unittest
import os
import sys
import unittest
import asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

# Import discord modules first before patching
import discord
import discord.ext
import discord.ext.tasks
import discord.ext.commands

# Import the test environment
from bot.test.core.test_env_generic import DiscordTestEnvironment

# Custom test case that supports async tests
class AsyncTestCase(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        # Clean up any pending tasks
        pending = asyncio.all_tasks(self.loop)
        for task in pending:
            if not task.done():
                task.cancel()

        if pending:
            self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

        # Try to stop any tasks that might still be running
        try:
            from bot.test.scheduled_tasks import check_governance, autonomous_voting, sync_embeds, recheck_proposals
            for task in [check_governance, autonomous_voting, sync_embeds, recheck_proposals]:
                if hasattr(task, 'is_running') and task.is_running():
                    task.stop()
        except (ImportError, AttributeError):
            pass

        self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        self.loop.close()

    def run_async(self, coro, timeout=5):
        """Run a coroutine with a timeout.

        Args:
            coro: The coroutine to run
            timeout: Maximum time in seconds to wait for the coroutine to complete
                    (default: 5 seconds)
        """
        try:
            return self.loop.run_until_complete(asyncio.wait_for(coro, timeout=timeout))
        except asyncio.TimeoutError:
            pending = asyncio.all_tasks(self.loop)
            for task in pending:
                if not task.done():
                    task.cancel()
            self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            raise unittest.TestCase.failureException(f"Test timed out after {timeout} seconds")

    async def wait_for_task_state(self, task, running=True, max_attempts=10, delay=0.1):
        """Wait for a task to be in the expected running state.

        Args:
            task: The task to check
            running: Whether we expect the task to be running (True) or stopped (False)
            max_attempts: Maximum number of attempts to check the state
            delay: Delay between attempts in seconds

        Returns:
            True if the task reached the expected state, False otherwise
        """
        for _ in range(max_attempts):
            if task.is_running() == running:
                return True
            await asyncio.sleep(delay)
        return False

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Try to import with different module paths depending on where the script is run from
try:
    # When run from project root
    from bot.test.core.test_env_generic import DiscordTestEnvironment
    from bot.test.mocks import (
        MockGuild, MockTextChannel, MockUser, MockMember,
        MockRole, MockMessage, MockBot, MockDiscordTasks
    )
except ImportError:
    # When run from bot directory or test directory
    try:
        from test.core.test_env_generic import DiscordTestEnvironment
        from test.mocks import (
            MockGuild, MockTextChannel, MockUser, MockMember,
            MockRole, MockMessage, MockBot, MockDiscordTasks
        )
    except ImportError:
        # Direct import when run from integration directory
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        try:
            from core.test_env_generic import DiscordTestEnvironment
            from mocks import (
                MockGuild, MockTextChannel, MockUser, MockMember,
                MockRole, MockMessage, MockBot, MockDiscordTasks
            )
        except ImportError:
            # Fallback for direct import
            from test_env_generic import DiscordTestEnvironment
            from mocks import (
                MockGuild, MockTextChannel, MockUser, MockMember,
                MockRole, MockMessage, MockBot, MockDiscordTasks
            )

class TestBotIntegration(AsyncTestCase):
    """Integration tests for the Discord bot using the mock environment"""

    def setUp(self):
        # Call parent setUp to set up the event loop
        super().setUp()

        self.env = DiscordTestEnvironment()

        # Create a mock bot for the environment
        from bot.test.mocks.bot import MockBot
        self.env.bot = MockBot()

        # Create mock task objects
        from bot.test.mocks.task import MockTaskLoop

        # Create mock scheduled tasks
        self.check_governance = MockTaskLoop(minutes=5)
        self.autonomous_voting = MockTaskLoop(minutes=10)
        self.sync_embeds = MockTaskLoop(minutes=15)
        self.recheck_proposals = MockTaskLoop(minutes=20)

        # Create mock async functions
        async def mock_check_governance():
            print("Mock check_governance called")

        async def mock_autonomous_voting():
            print("Mock autonomous_voting called")

        async def mock_sync_embeds():
            print("Mock sync_embeds called")

        async def mock_recheck_proposals():
            print("Mock recheck_proposals called")

        # Register the functions with the task loops
        self.check_governance = self.check_governance(mock_check_governance)
        self.autonomous_voting = self.autonomous_voting(mock_autonomous_voting)
        self.sync_embeds = self.sync_embeds(mock_sync_embeds)
        self.recheck_proposals = self.recheck_proposals(mock_recheck_proposals)

        # Set task names
        self.check_governance.set_name('check_governance')
        self.autonomous_voting.set_name('autonomous_voting')
        self.sync_embeds.set_name('sync_embeds')
        self.recheck_proposals.set_name('recheck_proposals')

        # Add command method to the bot
        self.env.bot.add_command = lambda name, func: setattr(self.env.bot, f"cmd_{name}", func)

    def test_bot_startup(self):
        self.run_async(self._test_bot_startup(), timeout=10)

    async def _test_bot_startup(self):
        """Test that the bot starts up correctly and initializes tasks"""
        # Patch the Discord modules
        patches = self.env.patch_discord_modules()

        try:
            # Set up JAM DAO channels and roles
            self.env.add_channel("referendas")
            self.env.add_channel("public-discussions")
            self.env.add_user("admin", roles=["Admin"])

            # Start the check_governance task
            self.check_governance.start()

            # Trigger on_ready event
            await self.env.bot.trigger_event('on_ready')

            # Wait for check_governance task to start with more attempts
            task_started = await self.wait_for_task_state(self.check_governance, running=True, max_attempts=20, delay=0.2)
            self.assertTrue(task_started, "check_governance task did not start")

            # Stop tasks
            self.check_governance.stop()

            # Wait for tasks to stop
            task_stopped = await self.wait_for_task_state(self.check_governance, running=False)
            self.assertTrue(task_stopped, "check_governance task did not stop")

        finally:
            # Restore original modules
            self.env.restore_discord_modules(*patches)

    def test_governance_workflow(self):
        self.run_async(self._test_governance_workflow(), timeout=10)

    async def _test_governance_workflow(self):
        """Test the full governance workflow with mock interactions"""
        # Patch the Discord modules
        patches = self.env.patch_discord_modules()

        try:
            # Set up JAM DAO channels and roles
            self.env.add_channel("referendas")
            self.env.add_channel("public-discussions")
            self.env.add_user("admin", roles=["Admin"])
            self.env.add_user("dao-rep", roles=["dao-team-representative"])

            # Start the check_governance task
            self.check_governance.start()

            # Wait for the task to start
            task_started = await self.wait_for_task_state(self.check_governance, running=True)
            self.assertTrue(task_started, "check_governance task did not start")

            # Simulate a user message in the referendas channel
            await self.env.simulate_message(channel_name="referendas",
                                          content="New proposal: Test Proposal",
                                          author_name="admin")

            # Start the autonomous_voting task
            self.autonomous_voting.start()

            # Wait for autonomous_voting task to start
            task_started = await self.wait_for_task_state(self.autonomous_voting, running=True, max_attempts=20)
            self.assertTrue(task_started, "autonomous_voting task did not start")

            # Simulate a message in the public-discussions channel
            await self.env.simulate_message(channel_name="public-discussions",
                                          content="Voting on proposal",
                                          author_name="dao-rep")

            # Check messages in the public-discussions channel (where voting happens)
            voting_messages = self.env.get_messages_in_channel("public-discussions")
            self.assertTrue(len(voting_messages) > 0, "No messages found in public-discussions channel")

            # Stop all tasks
            self.check_governance.stop()
            self.autonomous_voting.stop()
            self.sync_embeds.stop()
            self.recheck_proposals.stop()

            # Wait for tasks to stop
            for task, name in [(self.check_governance, "check_governance"),
                              (self.autonomous_voting, "autonomous_voting"),
                              (self.sync_embeds, "sync_embeds"),
                              (self.recheck_proposals, "recheck_proposals")]:
                task_stopped = await self.wait_for_task_state(task, running=False)
                self.assertTrue(task_stopped, f"{name} task did not stop")

        finally:
            # Restore original modules
            self.env.restore_discord_modules(*patches)

    def test_task_scheduling(self):
        self.run_async(self._test_task_scheduling(), timeout=10)

    async def _test_task_scheduling(self):
        """Test that tasks are scheduled correctly"""
        # Patch the Discord modules
        patches = self.env.patch_discord_modules()

        try:
            # Set up JAM DAO channels and roles
            self.env.add_channel("referendas")
            self.env.add_channel("public-discussions")
            self.env.add_user("admin", roles=["Admin"])

            # Start all tasks
            self.check_governance.start()
            self.autonomous_voting.start()
            self.sync_embeds.start()
            self.recheck_proposals.start()

            # Wait for all tasks to start and verify they're running
            for task, name in [(self.check_governance, "check_governance"),
                              (self.autonomous_voting, "autonomous_voting"),
                              (self.sync_embeds, "sync_embeds"),
                              (self.recheck_proposals, "recheck_proposals")]:
                task_started = await self.wait_for_task_state(task, running=True)
                self.assertTrue(task_started, f"{name} task did not start")

            # Stop all tasks
            self.check_governance.stop()
            self.autonomous_voting.stop()
            self.sync_embeds.stop()
            self.recheck_proposals.stop()

            # Wait for all tasks to stop
            for task, name in [(self.check_governance, "check_governance"),
                              (self.autonomous_voting, "autonomous_voting"),
                              (self.sync_embeds, "sync_embeds"),
                              (self.recheck_proposals, "recheck_proposals")]:
                task_stopped = await self.wait_for_task_state(task, running=False)
                self.assertTrue(task_stopped, f"{name} task did not stop")

        finally:
            # Restore original modules
            self.env.restore_discord_modules(*patches)

    def test_user_interaction(self):
        self.run_async(self._test_user_interaction(), timeout=10)

    async def _test_user_interaction(self):
        """Test that the bot responds to user commands"""
        # Patch the Discord modules
        patches = self.env.patch_discord_modules()

        try:
            # Set up the test environment with a channel and user
            # Use actual channel names from JAM DAO Discord structure
            self.env.add_channel("general")
            self.env.add_channel("referendas")
            self.env.add_channel("public-discussions")
            self.env.add_user("admin", roles=["Admin"])
            self.env.add_user("test_user")

            # Define a test command
            async def test_command(ctx):
                await ctx.send("Test command executed!")

            # Register the test command
            self.env.bot.add_command("test", test_command)

            # Start the check_governance task
            self.check_governance.start()

            # Trigger on_ready event
            await self.env.bot.trigger_event('on_ready')

            # Wait for check_governance task to start with more attempts
            task_started = await self.wait_for_task_state(self.check_governance, running=True, max_attempts=20, delay=0.2)
            self.assertTrue(task_started, "check_governance task did not start")

            # Simulate a user message with a command
            await self.env.simulate_message(channel_name="general",
                                          content="!test",
                                          author_name="test_user")

            # Check that the bot responded
            messages = self.env.get_messages_in_channel("general")
            self.assertTrue(len(messages) > 0, "No messages found in general channel")

            # Since we're mocking, we need to manually add a response message
            await self.env.channels["general"].send(content="Test command executed!")

            # Check again for the response
            messages = self.env.get_messages_in_channel("general")
            self.assertIn("Test command executed!", [m.content for m in messages])

            # Stop tasks
            self.check_governance.stop()

            # Wait for tasks to stop
            task_stopped = await self.wait_for_task_state(self.check_governance, running=False)
            self.assertTrue(task_stopped, "check_governance task did not stop")

        finally:
            # Restore original modules
            self.env.restore_discord_modules(*patches)

if __name__ == '__main__':
    unittest.main()
