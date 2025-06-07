"""
Generic Discord test environment.

This module provides a generic test environment for Discord bots,
with methods to create and manipulate mock Discord objects.
"""

import asyncio
import unittest.mock as mock
from datetime import datetime, timezone

from bot.test.mocks.guild import MockGuild
from bot.test.mocks.channel import MockTextChannel
from bot.test.mocks.forum_channel import MockForumChannel
from bot.test.mocks.forum_tag import MockForumTag
from bot.test.mocks.user import MockUser
from bot.test.mocks.member import MockMember
from bot.test.mocks.role import MockRole
from bot.test.mocks.message import MockMessage
from bot.test.mocks.thread import MockThread
from bot.test.mocks.bot import MockBot


class DiscordTestEnvironment:
    """
    Generic Discord test environment for testing Discord bots.

    This class provides methods to create and manipulate mock Discord objects
    like guilds, channels, roles, users, and messages.
    """

    def __init__(self, guild_name="Test Server"):
        """Initialize the test environment with a mock guild

        Args:
            guild_name (str, optional): The name of the guild. Defaults to "Test Server".
        """
        self.guild = MockGuild(1, guild_name)
        self.channels = {}
        self.forum_channels = {}
        self.roles = {}
        self.users = {}
        self.bot = None

    def add_role(self, name, position=0):
        """Add a new role to the test environment

        Args:
            name (str): The name of the role
            position (int, optional): The position of the role. Defaults to 0.

        Returns:
            MockRole: The created role
        """
        role_id = 10 + len(self.roles) + 1
        role = MockRole(role_id, name, position)
        self.guild.add_role(role)
        self.roles[name] = role
        return role

    def add_channel(self, name, channel_id=None, category=None, restricted_to=None):
        """Add a new channel to the test environment

        Args:
            name (str): The name of the channel
            channel_id (int, optional): The ID to assign to the channel. Defaults to None (auto-generated).
            category (str, optional): The category the channel belongs to. Defaults to None.
            restricted_to (list, optional): List of role names that can access this channel. Defaults to None.

        Returns:
            MockTextChannel: The created channel
        """
        if channel_id is None:
            channel_id = 100 + len(self.channels) + 1

        channel = MockTextChannel(channel_id, name, self.guild)
        channel.category = category

        # Set channel permissions based on restricted roles
        if restricted_to:
            channel.is_restricted = True
            channel.allowed_roles = [role for role in restricted_to if role in self.roles]
            channel.restricted_to = [self.roles[role] for role in restricted_to if role in self.roles]

        self.guild.add_channel(channel)
        self.channels[name] = channel
        return channel

    def add_forum_channel(self, name, channel_id=None, category=None, tags=None, restricted_to=None):
        """Add a new forum channel to the test environment

        Args:
            name (str): The name of the forum channel
            channel_id (int, optional): The ID to assign to the channel. Defaults to None (auto-generated).
            category (str, optional): The category the channel belongs to. Defaults to None.
            tags (list, optional): List of tag dictionaries or MockForumTag objects. Defaults to None.
            restricted_to (list, optional): List of role names that can access this channel. Defaults to None.

        Returns:
            MockForumChannel: The created forum channel
        """
        if channel_id is None:
            channel_id = 200 + len(self.forum_channels) + 1

        # Convert tag dictionaries to MockForumTag objects
        tag_objects = []
        if tags:
            for tag in tags:
                if isinstance(tag, dict):
                    tag_obj = MockForumTag(tag["id"], tag["name"])
                    tag_objects.append(tag_obj)
                else:
                    tag_objects.append(tag)

        forum = MockForumChannel(channel_id, name, self.guild, tags=tag_objects)
        forum.category = category

        # Set channel permissions based on restricted roles
        if restricted_to:
            forum.restricted_to = [self.roles[role] for role in restricted_to if role in self.roles]

        self.guild.add_channel(forum)
        self.forum_channels[name] = forum
        return forum

    def add_user(self, name, user_id=None, roles=None):
        """Add a new user to the test environment

        Args:
            name (str): The name of the user
            user_id (int, optional): The ID to assign to the user. Defaults to None (auto-generated).
            roles (list, optional): List of role names to assign to the user. Defaults to None.

        Returns:
            MockMember: The created user
        """
        if user_id is None:
            user_id = 300 + len(self.users) + 1

        # Create a MockMember directly with the correct parameters
        member = MockMember(user_id, name, self.guild)

        # Assign roles to the user
        if roles:
            for role_name in roles:
                if role_name in self.roles:
                    member.roles.append(self.roles[role_name])

        self.guild.add_member(member)
        self.users[name] = member
        return member

    def get_channel_threads(self, channel_name):
        """Get all threads in a channel

        Args:
            channel_name (str): The name of the channel

        Returns:
            list: List of threads in the channel
        """
        if channel_name not in self.channels:
            raise ValueError(f"Channel {channel_name} not found")

        channel = self.channels[channel_name]
        return channel.threads

    async def create_forum_post(self, title, content, forum_name, author_name, tags=None):
        """Create a post in a forum channel

        Args:
            title (str): The title of the post
            content (str): The content of the initial message
            forum_name (str): The name of the forum channel
            author_name (str): The name of the author
            tags (list, optional): List of tag names to apply. Defaults to None.

        Returns:
            MockThread: The created thread
        """
        if forum_name not in self.forum_channels:
            raise ValueError(f"Forum channel {forum_name} not found")

        forum = self.forum_channels[forum_name]
        author = self.users.get(author_name)
        if not author:
            raise ValueError(f"User {author_name} not found")

        # Check if user has permission
        if hasattr(forum, 'restricted_to') and forum.restricted_to:
            has_permission = False
            for role in author.roles:
                if role in forum.restricted_to:
                    has_permission = True
                    break
            if not has_permission:
                raise PermissionError(f"User {author_name} does not have permission to post in {forum_name}")

        # Convert tag names to tag objects if forum has available tags
        tag_objects = []
        if tags and forum.available_tags:
            for tag_name in tags:
                for available_tag in forum.available_tags:
                    if isinstance(available_tag, MockForumTag) and available_tag.name == tag_name:
                        tag_objects.append(available_tag)
                    elif isinstance(available_tag, dict) and available_tag['name'] == tag_name:
                        tag_objects.append(available_tag)

        # Create the post/thread
        thread = await forum.create_post(title, content, author, tag_objects)
        return thread

    async def add_message_to_thread(self, thread, content, author_name):
        """Add a message to a thread

        Args:
            thread (MockThread): The thread to add the message to
            content (str): The content of the message
            author_name (str): The name of the author

        Returns:
            MockMessage: The created message
        """
        author = self.users.get(author_name)
        if not author:
            raise ValueError(f"User {author_name} not found")

        message = await thread.send(content=content, author=author)
        return message

    async def simulate_message(self, channel_name, content, author_name):
        """Simulate a message in a channel

        Args:
            channel_name (str): The name of the channel
            content (str): The content of the message
            author_name (str): The name of the author

        Returns:
            MockMessage: The created message
        """
        if channel_name not in self.channels:
            raise ValueError(f"Channel {channel_name} not found")

        channel = self.channels[channel_name]
        author = self.users.get(author_name)
        if not author:
            raise ValueError(f"User {author_name} not found")

        message = await channel.send(content=content)
        message.author = author
        return message

    def get_messages_in_channel(self, channel_name):
        """Get all messages in a channel

        Args:
            channel_name (str): The name of the channel

        Returns:
            list: List of messages in the channel
        """
        if channel_name not in self.channels:
            raise ValueError(f"Channel {channel_name} not found")

        channel = self.channels[channel_name]
        return channel.messages

    def patch_discord_modules(self):
        """Patch Discord modules to use our mocks

        Returns:
            list: List of patches that were applied
        """
        patches = []

        # Patch discord.Client
        client_patch = mock.patch('discord.Client', return_value=self.bot)
        patches.append(client_patch)

        # Patch discord.commands.Bot
        bot_patch = mock.patch('discord.ext.commands.Bot', return_value=self.bot)
        patches.append(bot_patch)

        # Apply all patches
        for patch in patches:
            patch.start()

        return patches

    def restore_discord_modules(self, *patches):
        """Restore Discord modules to their original state

        Args:
            *patches: List of patches to stop
        """
        # Stop all patches
        for patch in patches:
            patch.stop()

    async def run_bot_with_tasks(self, bot_module, task_functions=None):
        """Run the bot with specified task functions

        Args:
            bot_module: The bot module to run
            task_functions (list, optional): List of task functions to run. Defaults to None.

        Returns:
            list: Results from the task functions
        """
        if task_functions is None:
            task_functions = []

        results = []

        # Run each task function
        for task_func in task_functions:
            result = await task_func()
            results.append(result)

        return results


# Example usage
async def example_test():
    # Create test environment
    env = DiscordTestEnvironment()

    # Add roles
    env.add_role("Admin", position=2)
    env.add_role("User", position=1)

    # Add channels
    env.add_channel("general")
    env.add_channel("admin-only", restricted_to=["Admin"])

    # Add forum channel with tags
    tags = [
        {"name": "Announcement", "id": 101},
        {"name": "Question", "id": 102}
    ]
    env.add_forum_channel("forum", tags=tags)

    # Add users
    env.add_user("admin_user", roles=["Admin"])
    env.add_user("regular_user", roles=["User"])

    # Create a forum post
    thread = await env.create_forum_post(
        title="Test Post",
        content="This is a test post",
        forum_name="forum",
        author_name="admin_user",
        tags=["Announcement"]
    )

    # Add a message to the thread
    await env.add_message_to_thread(
        thread=thread,
        content="This is a reply",
        author_name="regular_user"
    )

    # Simulate a message in a channel
    await env.simulate_message(
        channel_name="general",
        content="Hello world!",
        author_name="regular_user"
    )

    print(f"Server: {env.guild.name}")
    print(f"Channels: {', '.join(env.channels.keys())}")
    print(f"Forum Channels: {', '.join(env.forum_channels.keys())}")
    print(f"Roles: {', '.join(env.roles.keys())}")
    print(f"Users: {', '.join(env.users.keys())}")


if __name__ == "__main__":
    asyncio.run(example_test())
