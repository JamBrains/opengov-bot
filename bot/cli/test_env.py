#!/usr/bin/env python3
"""
Test environment runner for JAM DAO Discord Bot.

This module provides functionality to set up and run a test environment
for the JAM DAO Discord bot, simulating Discord server structure and interactions.
"""

import asyncio
import sys
import os
import time
import types
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# Global variables for test configuration
TEST_SCENARIO = 'default'  # default, voting, custom
TEST_DURATION = 30  # seconds
DEBUG = False

# Add the project root to the path so we can import our modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Setup mock Discord modules before importing anything Discord-related
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
            self._name = None
            self._running = False
            self._task = None

        def __call__(self, func):
            self.func = func
            return self

        def start(self):
            self._running = True
            return self

        def stop(self):
            self._running = False

        def is_running(self):
            return self._running

        def get_task(self):
            return self

        def set_name(self, name):
            self._name = name

        def get_name(self):
            return self._name

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
    sys.modules['discord'] = discord_mock
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

# Set up Discord mocks before importing anything else
patches = setup_discord_mocks()

# Now import test environment components
from bot.test.core.test_env_jam_dao import JamDaoDiscordTestEnvironment
from bot.test.mocks import (
    MockGuild, MockTextChannel, MockUser, MockMember,
    MockRole, MockMessage, MockBot, MockDiscordTasks, MockThread
)
from bot.test.mocks.forum_channel import MockForumChannel
from bot.test.mocks.forum_tag import MockForumTag


async def run_test_scenario():
    """Run the test scenario based on global configuration"""
    print("Setting up test environment...")

    # Create the test environment
    # Note: Discord modules are already patched by setup_discord_mocks()
    env = JamDaoDiscordTestEnvironment()

    # Setup the JAM DAO structure based on the stored memory
    # This includes channels like general, announcements, referendas, etc.
    # and roles like Admin, dao-team-representative, etc.
    await env.setup_jam_dao_structure()

    print("Discord test environment ready!")
    print(f"Server: {env.guild.name}")
    print(f"Standard Channels: {', '.join(env.channels.keys())}")
    print(f"Forum Channels: {', '.join(env.forum_channels.keys())}")
    print(f"Roles: {', '.join(env.roles.keys())}")
    print(f"Users: {', '.join(env.users.keys())}")

    print("\nStarting bot with scheduled tasks...")

    try:
        # Import the module with patched discord modules
        from bot.test.scheduled_tasks import check_governance, autonomous_voting, sync_embeds, recheck_proposals

        # Set task names
        check_governance.get_task().set_name('check_governance')
        autonomous_voting.get_task().set_name('autonomous_governance')
        sync_embeds.get_task().set_name('sync_embeds')
        recheck_proposals.get_task().set_name('recheck_proposals')

        # Trigger on_ready event to start the bot
        print("Triggering bot on_ready event...")
        await env.bot.trigger_event('on_ready')

        print(f"\n--- Starting JAM DAO test scenario: {TEST_SCENARIO} ---")
        print(f"--- Test will run for {TEST_DURATION} seconds ---")

        # Wait a bit for the bot to initialize
        await asyncio.sleep(1)

        # Run scenario-specific code based on TEST_SCENARIO
        referendum = None
        public_post = None

        if TEST_SCENARIO == 'default':
            referendum, public_post = await run_default_scenario(env)
        elif TEST_SCENARIO == 'voting':
            referendum, public_post = await run_voting_scenario(env)
        elif TEST_SCENARIO == 'custom':
            referendum, public_post = await run_custom_scenario(env)
        else:
            print(f"Unknown scenario: {TEST_SCENARIO}, running default scenario")
            referendum, public_post = await run_default_scenario(env)

        # Wait for scheduled tasks to run
        print("\nWaiting for scheduled tasks to run...")
        await asyncio.sleep(2)

        # Run for the specified duration
        if TEST_DURATION > 5:
            print(f"\nRunning test environment for {TEST_DURATION} seconds...")
            await asyncio.sleep(TEST_DURATION - 5)  # Subtract time already used

        # Print task status
        print("\n--- Task Status ---")
        print(f"check_governance running: {check_governance.is_running()}")
        print(f"autonomous_voting running: {autonomous_voting.is_running()}")
        print(f"sync_embeds running: {sync_embeds.is_running()}")
        print(f"recheck_proposals running: {recheck_proposals.is_running()}")

        # If we have referendum and public_post from the scenario, print their messages
        if referendum:
            print("\n--- Referendum Thread Messages ---")
            for i, msg in enumerate(referendum.messages):
                print(f"{i+1}. {msg.author.name}: {msg.content[:50]}{'...' if len(msg.content) > 50 else ''}")

        if public_post:
            print("\n--- Public Discussion Thread Messages ---")
            for i, msg in enumerate(public_post.messages):
                print(f"{i+1}. {msg.author.name}: {msg.content[:50]}{'...' if len(msg.content) > 50 else ''}")

        print("\nTest scenario completed!")

        # Stop all tasks
        print("\nStopping all tasks...")
        check_governance.stop()
        autonomous_voting.stop()
        sync_embeds.stop()
        recheck_proposals.stop()

    finally:
        # Restore original modules
        # Clean up our global patches
        for p in patches:
            p.stop()

        # Clear mocked modules from sys.modules
        for module_name in ['discord', 'discord.ext', 'discord.ext.commands', 'discord.ext.tasks']:
            if module_name in sys.modules:
                del sys.modules[module_name]

        print("Test environment cleaned up.")


async def run_default_scenario(env):
    """Run the default test scenario."""
    print("\n--- Running DEFAULT scenario ---")

    # Create a referendum post in the referendas forum
    print("\n1. Creating a new referendum in the referendas forum")
    referendum = await env.create_forum_post(
        title="123: Treasury Spend for Development",
        content="This referendum proposes to spend 100 DOT on development work.",
        forum_name="referendas",
        author_name="dao_rep1",
        tags=["MediumSpender"]
    )
    print(f"Created referendum post: {referendum.name}")

    # Wait for the bot to process
    await asyncio.sleep(1)

    # Create a public discussion post
    print("\n2. Creating a public discussion thread for the referendum")
    public_post = await env.create_forum_post(
        title="Ref 123: Treasury Spend for Development",
        content="This is the public discussion thread for Referendum #123.",
        forum_name="public-discussions",
        author_name="dao_rep1"
    )
    print(f"Created public discussion post: {public_post.name}")

    # Test the feedback command
    print("\n3. Testing the /feedback slash command")

    # Test feedback from a dao-team-representative (should succeed)
    print("  3.1. Testing feedback from dao-team-representative (should succeed)")
    try:
        await env.simulate_slash_command(
            command_name="feedback",
            options={"message": "This is a test feedback message"},
            user_name="dao_rep1",
            thread_id=referendum.id,
            channel_name="referendas",
            public_thread=public_post
        )
        print("  SUCCESS: Feedback command executed successfully")
    except Exception as e:
        print(f"  ERROR: {e}")

    # Test feedback from a non-representative user (should fail)
    print("  3.2. Testing feedback from non-representative user (should fail)")
    try:
        result = await env.simulate_slash_command(
            command_name="feedback",
            options={"message": "I think this is a good proposal."},
            user_name="participant1",
            thread_id=referendum.id,
            channel_name="referendas",
            public_thread=public_post
        )
        if "don't have permission" in result["response_content"]:
            print("  SUCCESS: Permission check worked correctly")
        else:
            print(f"  FAILED: Permission check failed - {result['response_content']}")
    except Exception as e:
        print(f"  ERROR: {e}")

    # Test feedback in wrong channel (should fail)
    print("  3.3. Testing feedback in wrong channel (should fail)")
    try:
        result = await env.simulate_slash_command(
            command_name="feedback",
            options={"message": "This is feedback in the wrong channel."},
            user_name="dao_rep1",
            channel_name="general",
            public_thread=public_post
        )
        if "must be used in a thread" in result["response_content"]:
            print("  SUCCESS: Channel check worked correctly")
        else:
            print(f"  FAILED: Channel check failed - {result['response_content']}")
    except Exception as e:
        print(f"  ERROR: {e}")

    # Check if the feedback was posted to the public-discussions channel
    print("  3.4. Checking if feedback was posted to public-discussions channel")
    # Debug prints
    print(f"  DEBUG: public_post.name = {public_post.name}")
    print(f"  DEBUG: public_post.id = {public_post.id}")
    print(f"  DEBUG: Number of messages in public_post = {len(public_post.messages)}")
    for i, msg in enumerate(public_post.messages):
        print(f"  DEBUG: Message {i}: {msg.__class__.__name__}, content = {msg.content if hasattr(msg, 'content') else 'No content'}")

    public_thread_messages = [msg.content for msg in public_post.messages]
    feedback_messages = [msg for msg in public_thread_messages if msg.startswith("**Feedback:**")]
    if feedback_messages:
        print(f"  SUCCESS: Found feedback message: {feedback_messages[0][:50]}...")
    else:
        print("  FAILED: No feedback message found in public-discussions thread")

    # Test discussions from different roles in the referendum thread
    print("\n4. Testing discussion permissions in referendum thread")

    # Add discussion from dao-team-representatives to the referendum
    print("  4.1. Adding discussion from dao-team-representatives to referendum")
    await env.add_message_to_thread(
        content="I support this proposal because it aligns with our goals.",
        thread_id=referendum.id,
        author_name="dao_rep2",
        forum_name="referendas"
    )
    print("  - dao_rep2 successfully added a comment")

    # Add discussion from dao-participants to the referendum
    print("  4.2. Adding discussion from dao-participants to referendum")
    await env.add_message_to_thread(
        content="I think this is a good use of treasury funds.",
        thread_id=referendum.id,
        author_name="participant1",
        forum_name="referendas"
    )
    print("  - participant1 successfully added a comment")

    # Add discussion from jam-implementer to the referendum
    print("  4.3. Adding discussion from jam-implementer to referendum")
    await env.add_message_to_thread(
        content="I can help with the technical implementation if needed.",
        thread_id=referendum.id,
        author_name="implementer1",
        forum_name="referendas"
    )
    print("  - implementer1 successfully added a comment")

    # Simulate votes from dao-team-representatives (should succeed)
    print("\n5. Testing voting permissions - dao-team-representatives vote (should succeed)")
    votes = []
    for rep_name in ["dao_rep1", "dao_rep2", "dao_rep3", "dao_rep4", "dao_rep5"]:
        try:
            vote_message = await env.add_vote_to_referendum(
                thread=referendum,
                vote_content=f"!vote {'yes' if rep_name != 'dao_rep3' else 'no'}",
                author_name=rep_name
            )
            votes.append(vote_message)
            print(f"  - {rep_name} successfully voted")
            # Trigger the bot's message handler
            await env.bot.trigger_event('on_message', vote_message)
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"  - ERROR: {rep_name} failed to vote: {e}")

    # Calculate and display quorum
    eligible_users = env.get_quorum_eligible_users()
    quorum_percentage = env.calculate_quorum_percentage(len(votes))
    print(f"\n6. Quorum calculation: {len(votes)} votes out of {len(eligible_users)} eligible representatives")
    print(f"  - Quorum percentage: {quorum_percentage:.1f}%")
    print(f"  - Eligible users for quorum: {[user.name for user in eligible_users]}")

    # Test a non-representative (participant) trying to vote (should fail)
    print("\n7. Testing permission restrictions - dao-participant tries to vote (should fail)")
    try:
        non_rep_vote = await env.add_vote_to_referendum(
            thread=referendum,
            vote_content="!vote yes",
            author_name="participant1"
        )
        print("  ERROR: Participant was able to vote when they shouldn't be allowed to!")
    except PermissionError as e:
        print(f"  SUCCESS: {e}")

    # Test a non-representative (implementer) trying to vote (should fail)
    print("\n8. Testing permission restrictions - jam-implementer tries to vote (should fail)")
    try:
        non_rep_vote = await env.add_vote_to_referendum(
            thread=referendum,
            vote_content="!vote yes",
            author_name="implementer1"
        )
        print("  ERROR: Implementer was able to vote when they shouldn't be allowed to!")
    except PermissionError as e:
        print(f"  SUCCESS: {e}")

    # Test a bot trying to vote (should fail)
    print("\n9. Testing permission restrictions - bots try to vote (should fail)")
    for bot_name in ["bot_user", "dotgov_bot", "search_bot", "booster_bot"]:
        try:
            bot_vote = await env.add_vote_to_referendum(
                thread=referendum,
                vote_content="!vote yes",
                author_name=bot_name
            )
            print(f"  ERROR: Bot {bot_name} was able to vote when it shouldn't be allowed to!")
        except PermissionError as e:
            print(f"  SUCCESS: {bot_name} - {e}")

    # Add messages to the public discussion that was created earlier
    print("\n10. Adding messages to the public discussion thread")

    # Add messages to the public discussion from different roles
    await env.add_message_to_thread(
        content="What do community members think about this proposal?",
        thread_id=public_post.id,
        author_name="dao_rep1",
        forum_name="public-discussions"
    )
    print("  - dao_rep1 successfully added a comment to public discussion")

    await env.add_message_to_thread(
        content="I think this is a good use of treasury funds.",
        thread_id=public_post.id,
        author_name="participant1",
        forum_name="public-discussions"
    )
    print("  - participant1 successfully added a comment to public discussion")

    await env.add_message_to_thread(
        content="I can help with the technical implementation if needed.",
        thread_id=public_post.id,
        author_name="implementer1",
        forum_name="public-discussions"
    )
    print("  - implementer1 successfully added a comment to public discussion")

    # Test bot interaction in public discussion
    print("\n11. Testing bot interaction in public discussion")
    await env.add_message_to_thread(
        content="I'll help track this proposal's status.",
        thread_id=public_post.id,
        author_name="bot_user",
        forum_name="public-discussions"
    )
    print("  - bot_user successfully added a comment to public discussion")

    print("\n--- Test scenario completed successfully ---")
    print("\nSummary of role-based permissions:")
    print("  - @dao-team-representative: Can read, comment, and vote in #referendas")
    print("  - @dao-participant: Can read and comment in #referendas, but cannot vote")
    print("  - @jam-implementer: Can read and comment in #referendas, but cannot vote")
    print("  - Bots (@JAM-DAO-Bot, @DOT-GOV, @Server Booster, @jam-search): Cannot vote")
    print("  - Quorum calculation only includes users with @dao-team-representative role")

    # Return the created threads for potential further testing
    return referendum, public_post


async def run_voting_scenario(env):
    """Run the voting test scenario"""
    print("\n--- Running VOTING scenario ---")

    # Create a referendum post in the referendas forum
    print("\n1. Creating a new referendum in the referendas forum")
    referendum = await env.create_forum_post(
        title="Referendum #123: Treasury Spend for Development",
        content="This referendum proposes to spend 100 DOT on development work.",
        forum_name="referendas",
        author_name="dao_rep1",
        tags=["MediumSpender"]
    )
    print(f"Created referendum post: {referendum.name}")

    # Wait for the bot to process
    await asyncio.sleep(1)

    # Add some discussion to the referendum
    print("\n2. Adding discussion to the referendum thread")
    await env.add_message_to_thread(
        content="I support this proposal as it aligns with our roadmap.",
        thread_id=referendum.id,
        author_name="dao_rep2",
        forum_name="referendas"
    )

    # Simulate a vote command
    print("\n3. Team representative votes on the referendum")
    vote_message = await env.add_message_to_thread(
        content="!vote yes",
        thread_id=referendum.id,
        author_name="dao_rep1",
        forum_name="referendas"
    )

    # Trigger the bot's message handler
    await env.bot.trigger_event('on_message', vote_message)
    await asyncio.sleep(1)

    # Create a public discussion post
    print("\n4. Creating a public discussion thread for the referendum")
    public_post = await env.create_forum_post(
        title="Public Discussion: Referendum #123",
        content="This is the public discussion thread for Referendum #123 about treasury spending.",
        forum_name="public-discussions",
        author_name="dao_rep1"
    )
    print(f"Created public discussion post: {public_post.name}")

    # Add a message to the public discussion
    await env.add_message_to_thread(
        content="What do community members think about this proposal?",
        thread_id=public_post.id,
        author_name="dao_rep1",
        forum_name="public-discussions"
    )

    # Simulate a regular user responding in the public discussion
    await env.add_message_to_thread(
        content="I think this is a good use of treasury funds.",
        thread_id=public_post.id,
        author_name="participant1",
        forum_name="public-discussions"
    )

    # Test a non-representative trying to vote (should fail)
    print("\n5. Testing permission restrictions - non-representative tries to vote")
    non_rep_vote = await env.add_message_to_thread(
        content="!vote yes",
        thread_id=referendum.id,
        author_name="participant1",
        forum_name="referendas"
    )

    # Trigger the bot's message handler
    await env.bot.trigger_event('on_message', non_rep_vote)
    await asyncio.sleep(1)

    return referendum, public_post


async def run_custom_scenario(env):
    """Run a custom test scenario"""
    print("\n--- Running CUSTOM scenario ---")
    print("This is a placeholder for a custom scenario.")
    print("You can modify this function to test specific bot behaviors.")

    # Create a basic forum post for testing
    referendum = await env.create_forum_post(
        title="Custom Test Post",
        content="This is a custom test post.",
        forum_name="referendas",
        author_name="admin_user",
        tags=["BigSpender"]
    )

    # No public post in this scenario
    public_post = None

    return referendum, public_post


def main():
    """Main entry point for running the test environment"""
    # Set global variables from environment variables
    global TEST_SCENARIO, DEBUG, TEST_DURATION

    TEST_SCENARIO = os.environ.get('TEST_SCENARIO', 'default')
    DEBUG = os.environ.get('DEBUG', '').lower() in ['true', '1', 'yes']

    try:
        TEST_DURATION = int(os.environ.get('TEST_DURATION', '30'))
    except ValueError:
        TEST_DURATION = 30

    print(f"Starting JAM DAO Discord Bot in test environment with scenario: {TEST_SCENARIO}")
    if DEBUG:
        print("Debug mode: ON")
    print(f"Test duration: {TEST_DURATION} seconds")

    # Run the test scenario
    asyncio.run(run_test_scenario())

    return 0


if __name__ == "__main__":
    sys.exit(main())
