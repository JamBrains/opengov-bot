import unittest
import asyncio
from datetime import datetime, timezone, timedelta
import sys
import os
from unittest.mock import patch, MagicMock

# Import discord modules first before patching
import discord
import discord.ext
import discord.ext.tasks
import discord.ext.commands

# Custom test case that supports async tests
class AsyncTestCase(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        # Clean up any pending tasks
        pending = asyncio.all_tasks(self.loop)
        if pending:
            self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        self.loop.close()

    def run_async(self, coro):
        return self.loop.run_until_complete(coro)

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Try to import with different module paths depending on where the script is run from
try:
    # When run from project root
    from bot.test.mocks import (
        MockGuild, MockTextChannel, MockUser, MockMember,
        MockRole, MockMessage, MockBot, MockDiscordTasks
    )
except ImportError:
    # When run from bot directory or test directory
    try:
        from test.mocks import (
            MockGuild, MockTextChannel, MockUser, MockMember,
            MockRole, MockMessage, MockBot, MockDiscordTasks
        )
    except ImportError:
        # Direct import when run from unit directory
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from mocks import (
            MockGuild, MockTextChannel, MockUser, MockMember,
            MockRole, MockMessage, MockBot, MockDiscordTasks
        )

class TestScheduledTasks(AsyncTestCase):
    def setUp(self):
        # Call parent setUp to set up the event loop
        super().setUp()

        # Set up mock environment
        self.mock_tasks = patch('discord.ext.tasks', new=MockDiscordTasks())
        self.mock_tasks.start()

        # Import the scheduled tasks module - this is safe now that we've patched discord.ext.tasks
        import sys
        import importlib
        if 'bot.test.scheduled_tasks' in sys.modules:
            importlib.reload(sys.modules['bot.test.scheduled_tasks'])
        else:
            import bot.test.scheduled_tasks

        # Create mock Discord environment
        self.guild = MockGuild(1, "Test Server")

        # Create channels
        self.general_channel = self.guild.add_channel(MockTextChannel(101, "general", self.guild))
        self.governance_channel = self.guild.add_channel(MockTextChannel(102, "governance", self.guild))

        # Create roles
        self.admin_role = self.guild.add_role(MockRole(201, "Admin", 2))
        self.member_role = self.guild.add_role(MockRole(202, "Member", 1))

        # Create users/members
        self.admin_user = self.guild.add_member(MockMember(301, "Admin User", self.guild, [self.admin_role]))
        self.regular_user = self.guild.add_member(MockMember(302, "Regular User", self.guild, [self.member_role]))

        # Create bot
        self.bot = MockBot()
        self.bot.add_guild(self.guild)

        # Replace discord.ext.tasks with our mock version
        self.original_tasks = None

    async def asyncSetUp(self):
        # This will run before each test
        pass

    async def asyncTearDown(self):
        # This will run after each test
        pass

    def test_check_governance(self):
        self.run_async(self._test_check_governance())

    async def _test_check_governance(self):
        """Test the check_governance task"""
        # Get the tasks from the imported module
        import bot.test.scheduled_tasks as tasks

        # Create a mock function to pass to the task
        async def mock_check_governance():
            # Using a counter to limit prints to just once
            if not hasattr(mock_check_governance, "_called"):
                mock_check_governance._called = True
                print("check_governance mock function called")

        # Set up the task with the mock function
        tasks.check_governance = tasks.check_governance(mock_check_governance)

        # Set task names
        tasks.check_governance.get_task().set_name('check_governance')

        # Start the task
        tasks.check_governance.start()

        # Wait a bit for the task to run
        await asyncio.sleep(0.1)

        # Verify task behavior
        self.assertTrue(tasks.check_governance.is_running())

        # Stop the task
        tasks.check_governance.stop()

        # Verify the task is stopped
        self.assertFalse(tasks.check_governance.is_running())

    def test_autonomous_voting(self):
        self.run_async(self._test_autonomous_voting())

    async def _test_autonomous_voting(self):
        """Test the autonomous_voting task"""
        # Get the tasks from the imported module
        import bot.test.scheduled_tasks as tasks

        # Create a mock function to pass to the task
        async def mock_autonomous_voting():
            # Using a counter to limit prints to just once
            if not hasattr(mock_autonomous_voting, "_called"):
                mock_autonomous_voting._called = True
                print("autonomous_voting mock function called")

        # Set up the task with the mock function
        tasks.autonomous_voting = tasks.autonomous_voting(mock_autonomous_voting)

        # Set task names
        tasks.autonomous_voting.get_task().set_name('autonomous_voting')

        # Start the task
        tasks.autonomous_voting.start()

        # Wait a bit for the task to run
        await asyncio.sleep(0.1)

        # Verify task behavior
        self.assertTrue(tasks.autonomous_voting.is_running())

        # Stop the task
        tasks.autonomous_voting.stop()

        # Verify the task is stopped
        self.assertFalse(tasks.autonomous_voting.is_running())

    def test_sync_embeds(self):
        self.run_async(self._test_sync_embeds())

    async def _test_sync_embeds(self):
        """Test the sync_embeds task"""
        # Get the tasks from the imported module
        import bot.test.scheduled_tasks as tasks

        # Create a mock function to pass to the task
        async def mock_sync_embeds():
            # Using a counter to limit prints to just once
            if not hasattr(mock_sync_embeds, "_called"):
                mock_sync_embeds._called = True
                print("sync_embeds mock function called")

        # Set up the task with the mock function
        tasks.sync_embeds = tasks.sync_embeds(mock_sync_embeds)

        # Set task names
        tasks.sync_embeds.get_task().set_name('sync_embeds')

        # Start the task
        tasks.sync_embeds.start()

        # Wait a bit for the task to run
        await asyncio.sleep(0.1)

        # Verify task behavior
        self.assertTrue(tasks.sync_embeds.is_running())

        # Stop the task
        tasks.sync_embeds.stop()

        # Verify the task is stopped
        self.assertFalse(tasks.sync_embeds.is_running())

    def test_recheck_proposals(self):
        self.run_async(self._test_recheck_proposals())

    async def _test_recheck_proposals(self):
        """Test the recheck_proposals task"""
        # Get the tasks from the imported module
        import bot.test.scheduled_tasks as tasks

        # Create a mock function to pass to the task
        async def mock_recheck_proposals():
            # Using a counter to limit prints to just once
            if not hasattr(mock_recheck_proposals, "_called"):
                mock_recheck_proposals._called = True
                print("recheck_proposals mock function called")

        # Set up the task with the mock function
        tasks.recheck_proposals = tasks.recheck_proposals(mock_recheck_proposals)

        # Set task name
        tasks.recheck_proposals.get_task().set_name('recheck_proposals')

        # Start the task
        tasks.recheck_proposals.start()

        # Wait a bit for the task to run
        await asyncio.sleep(0.1)

        # Verify task behavior
        self.assertTrue(tasks.recheck_proposals.is_running())

        # Stop the task
        tasks.recheck_proposals.stop()

        # Verify the task is stopped
        self.assertFalse(tasks.recheck_proposals.is_running())

    def test_task_dependencies(self):
        self.run_async(self._test_task_dependencies())

    async def _test_task_dependencies(self):
        """Test task dependencies and interactions"""
        # Get the tasks from the imported module
        import bot.test.scheduled_tasks as tasks

        # Create mock functions for each task
        async def mock_check_governance():
            # Using a counter to limit prints to just once
            if not hasattr(mock_check_governance, "_called"):
                mock_check_governance._called = True
                print("check_governance mock function called")

        async def mock_autonomous_voting():
            # Using a counter to limit prints to just once
            if not hasattr(mock_autonomous_voting, "_called"):
                mock_autonomous_voting._called = True
                print("autonomous_voting mock function called")

        async def mock_sync_embeds():
            # Using a counter to limit prints to just once
            if not hasattr(mock_sync_embeds, "_called"):
                mock_sync_embeds._called = True
                print("sync_embeds mock function called")

        async def mock_recheck_proposals():
            # Using a counter to limit prints to just once
            if not hasattr(mock_recheck_proposals, "_called"):
                mock_recheck_proposals._called = True
                print("recheck_proposals mock function called")

        # Set up tasks with mock functions
        tasks.check_governance = tasks.check_governance(mock_check_governance)
        tasks.autonomous_voting = tasks.autonomous_voting(mock_autonomous_voting)
        tasks.sync_embeds = tasks.sync_embeds(mock_sync_embeds)
        tasks.recheck_proposals = tasks.recheck_proposals(mock_recheck_proposals)

        # Set task names
        tasks.check_governance.get_task().set_name('check_governance')
        tasks.autonomous_voting.get_task().set_name('autonomous_voting')
        tasks.sync_embeds.get_task().set_name('sync_embeds')
        tasks.recheck_proposals.get_task().set_name('recheck_proposals')

        # Start all tasks
        tasks.check_governance.start()
        tasks.autonomous_voting.start()
        tasks.sync_embeds.start()
        tasks.recheck_proposals.start()

        # Wait a bit for tasks to run
        await asyncio.sleep(0.1)

        # Verify all tasks are running
        self.assertTrue(tasks.check_governance.is_running())
        self.assertTrue(tasks.autonomous_voting.is_running())
        self.assertTrue(tasks.sync_embeds.is_running())
        self.assertTrue(tasks.recheck_proposals.is_running())

        # Stop all tasks
        tasks.check_governance.stop()
        tasks.autonomous_voting.stop()
        tasks.sync_embeds.stop()
        tasks.recheck_proposals.stop()

    def test_evaluate_task_schedule(self):
        self.run_async(self._test_evaluate_task_schedule())

    async def _test_evaluate_task_schedule(self):
        """Test the evaluate_task_schedule function"""
        # Get the tasks from the imported module
        import bot.test.scheduled_tasks as tasks

        # Create a mock task for testing within the time window
        mock_task_within = MagicMock()
        mock_task_within.next_iteration = datetime.now(timezone.utc) + timedelta(minutes=1)
        mock_task_within.get_task().get_name.return_value = 'mock_task_within'
        mock_task_within.is_running.return_value = True
        mock_task_within.stop = MagicMock()

        # Test the function with a task that should be within the time window (should return True)
        result_within = await tasks.evaluate_task_schedule(mock_task_within, minutes=5)
        self.assertTrue(result_within, "Task within time window should return True")

        # Create a mock task for testing outside the time window
        mock_task_outside = MagicMock()
        mock_task_outside.next_iteration = datetime.now(timezone.utc) + timedelta(minutes=10)
        mock_task_outside.get_task().get_name.return_value = 'mock_task_outside'
        mock_task_outside.is_running.return_value = True
        mock_task_outside.stop = MagicMock()

        # Test the function with a task that should be outside the time window (should return False)
        result_outside = await tasks.evaluate_task_schedule(mock_task_outside, minutes=5)
        self.assertFalse(result_outside, "Task outside time window should return False")

if __name__ == '__main__':
    unittest.main()
