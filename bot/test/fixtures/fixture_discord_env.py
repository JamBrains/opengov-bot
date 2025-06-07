"""
Test fixtures for Discord test environment.
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import patch

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import our mock components
from test.mocks import (
    MockGuild, MockTextChannel, MockUser, MockMember,
    MockRole, MockMessage, MockBot, MockDiscordTasks
)

@pytest.fixture
def mock_guild():
    """Fixture that provides a mock Discord guild."""
    return MockGuild(1, "Test Server")

@pytest.fixture
def mock_channels(mock_guild):
    """Fixture that provides mock Discord channels."""
    channels = {
        "general": mock_guild.add_channel(MockTextChannel(101, "general", mock_guild)),
        "governance": mock_guild.add_channel(MockTextChannel(102, "governance", mock_guild)),
        "proposals": mock_guild.add_channel(MockTextChannel(103, "proposals", mock_guild)),
        "voting": mock_guild.add_channel(MockTextChannel(104, "voting", mock_guild)),
    }
    return channels

@pytest.fixture
def mock_roles(mock_guild):
    """Fixture that provides mock Discord roles."""
    roles = {
        "admin": mock_guild.add_role(MockRole(201, "Admin", 3)),
        "moderator": mock_guild.add_role(MockRole(202, "Moderator", 2)),
        "member": mock_guild.add_role(MockRole(203, "Member", 1)),
    }
    return roles

@pytest.fixture
def mock_users(mock_guild, mock_roles):
    """Fixture that provides mock Discord users."""
    users = {
        "admin": mock_guild.add_member(MockMember(301, "Admin User", mock_guild, [mock_roles["admin"]])),
        "mod": mock_guild.add_member(MockMember(302, "Moderator User", mock_guild, [mock_roles["moderator"]])),
        "user1": mock_guild.add_member(MockMember(303, "Regular User 1", mock_guild, [mock_roles["member"]])),
        "user2": mock_guild.add_member(MockMember(304, "Regular User 2", mock_guild, [mock_roles["member"]])),
    }
    return users

@pytest.fixture
def mock_bot(mock_guild):
    """Fixture that provides a mock Discord bot."""
    bot = MockBot()
    bot.add_guild(mock_guild)
    return bot

@pytest.fixture
def discord_patches():
    """Fixture that patches Discord modules for testing."""
    discord_patch = patch('discord.ext.tasks', MockDiscordTasks)
    commands_patch = patch('discord.ext.commands.Bot', lambda **kwargs: MockBot())

    discord_patch.start()
    commands_patch.start()

    yield (discord_patch, commands_patch)

    discord_patch.stop()
    commands_patch.stop()

@pytest.fixture
async def discord_test_env(mock_guild, mock_channels, mock_roles, mock_users, mock_bot):
    """Fixture that provides a complete Discord test environment."""
    class TestEnv:
        def __init__(self):
            self.guild = mock_guild
            self.channels = mock_channels
            self.roles = mock_roles
            self.users = mock_users
            self.bot = mock_bot
            self.message_history = []

        async def simulate_message(self, content, author_name="user1", channel_name="general"):
            """Simulate a user sending a message in a channel."""
            author = self.users.get(author_name)
            channel = self.channels.get(channel_name)

            if not author or not channel:
                raise ValueError(f"Author '{author_name}' or channel '{channel_name}' not found")

            message_id = len(channel.messages) + 1
            message = MockMessage(message_id, content, author, channel, self.guild)
            channel.messages.append(message)
            self.message_history.append(message)

            # If it's a command, process it
            if content.startswith('!'):
                await self.bot.process_command(message)

            return message

        async def simulate_reaction(self, emoji, message_index=-1, user_name="user1"):
            """Simulate a user adding a reaction to a message."""
            if not self.message_history:
                raise ValueError("No messages in history to react to")

            message = self.message_history[message_index]
            user = self.users.get(user_name)

            if not user:
                raise ValueError(f"User '{user_name}' not found")

            await message.add_reaction(emoji)
            return message

        def get_messages_in_channel(self, channel_name, limit=None):
            """Get messages sent in a specific channel."""
            channel = self.channels.get(channel_name)
            if not channel:
                raise ValueError(f"Channel '{channel_name}' not found")

            if limit:
                return channel.messages[-limit:]
            return channel.messages

        def get_threads_in_channel(self, channel_name):
            """Get threads created in a specific channel."""
            channel = self.channels.get(channel_name)
            if not channel:
                raise ValueError(f"Channel '{channel_name}' not found")

            return channel.threads

    return TestEnv()
