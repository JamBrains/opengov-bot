"""
JAM DAO specific Discord test environment.

This module extends the generic Discord test environment with
JAM DAO specific structure and functionality.
"""

import asyncio
from bot.test.mocks.bot import MockBot
from bot.test.fixtures.config_jam_dao import (
    get_all_roles, get_all_channels, get_forum_channels, get_users
)

from bot.test.core.test_env_generic import DiscordTestEnvironment


class JamDaoDiscordTestEnvironment(DiscordTestEnvironment):
    """
    JAM DAO specific Discord test environment.

    This class extends the generic DiscordTestEnvironment with methods
    specific to the JAM DAO Discord server structure.
    """

    async def setup_jam_dao_structure(self):
        """
        Set up the full JAM DAO Discord server structure with roles, channels, and users
        using the configuration from the jam_dao_config fixture.

        Returns:
            JamDaoDiscordTestEnvironment: The configured environment
        """
        # Create roles
        for role_config in get_all_roles():
            self.add_role(role_config["name"], position=role_config["position"])

        # Create standard and categorized channels
        for channel_config in get_all_channels():
            restricted_to = channel_config.get("restricted_to")
            self.add_channel(
                channel_config["name"],
                category=channel_config.get("category"),
                restricted_to=restricted_to
            )

        # Create forum channels with tags
        for forum_config in get_forum_channels():
            self.add_forum_channel(
                forum_config["name"],
                category=forum_config.get("category"),
                tags=forum_config.get("tags")
            )

        # Create users with roles
        for user_config in get_users():
            self.add_user(user_config["name"], roles=user_config["roles"])

        # Set up the bot
        self.bot = MockBot()
        self.bot.user = self.users["bot_user"]
        self.bot.add_guild(self.guild)

        return self

    async def create_referendum_post(self, title, content, author_name="dao_rep1", tags=None):
        """
        Create a referendum post in the referendas forum channel.

        Args:
            title (str): The title of the referendum post
            content (str): The content of the initial message
            author_name (str, optional): The name of the author. Defaults to "dao_rep1".
            tags (list, optional): List of tag names to apply. Defaults to ["SmallSpender"].

        Returns:
            MockThread: The created thread
        """
        if tags is None:
            tags = ["SmallSpender"]

        return await self.create_forum_post(
            title=title,
            content=content,
            forum_name="referendas",
            author_name=author_name,
            tags=tags
        )

    async def add_vote_to_referendum(self, thread, vote_content, author_name="dao_rep1"):
        """
        Add a vote message to a referendum thread.

        Args:
            thread (MockThread): The referendum thread
            vote_content (str): The vote content (e.g., "!vote aye")
            author_name (str, optional): The name of the voter. Defaults to "dao_rep1".

        Returns:
            MockMessage: The created message

        Raises:
            PermissionError: If the user does not have the dao-team-representative role
            ValueError: If the user is not found
        """
        author = self.users.get(author_name)
        if not author:
            raise ValueError(f"User {author_name} not found")

        # Check if the user has the dao-team-representative role
        # Only dao-team-representative can vote (Admin is allowed for administrative purposes)
        has_vote_permission = False
        for role in author.roles:
            if role.name in ["dao-team-representative", "Admin"]:
                has_vote_permission = True
                break

        if not has_vote_permission:
            raise PermissionError(f"User {author_name} does not have permission to vote. Only users with dao-team-representative role can vote.")

        message = await thread.send(content=vote_content, author=author)
        return message

    def get_quorum_eligible_users(self):
        """
        Get the list of users who are eligible for quorum calculation.
        In JAM DAO, only users with the dao-team-representative role are counted.

        Returns:
            list: List of user objects with dao-team-representative role
        """
        eligible_users = []
        for user_name, user in self.users.items():
            for role in user.roles:
                if role.name == "dao-team-representative":
                    eligible_users.append(user)
                    break
        return eligible_users

    def calculate_quorum_percentage(self, votes_count):
        """
        Calculate the quorum percentage based on the number of votes and eligible users.

        Args:
            votes_count (int): The number of votes cast

        Returns:
            float: The percentage of eligible users who voted (0-100)
        """
        eligible_users = self.get_quorum_eligible_users()
        if not eligible_users:
            return 0.0

        return (votes_count / len(eligible_users)) * 100.0

    async def add_message_to_thread(self, thread=None, content=None, author_name=None, thread_id=None, forum_name=None):
        """
        Add a message to a thread. This overrides the parent method to handle both direct thread objects
        and thread_id + forum_name combinations.

        Args:
            thread (MockThread, optional): The thread to add the message to. Defaults to None.
            content (str, optional): The content of the message. Defaults to None.
            author_name (str, optional): The name of the author. Defaults to None.
            thread_id (int, optional): The ID of the thread. Defaults to None.
            forum_name (str, optional): The name of the forum channel. Defaults to None.

        Returns:
            MockMessage: The created message
        """
        # If thread is not provided directly, look it up by ID and forum name
        if thread is None and thread_id is not None and forum_name is not None:
            if forum_name not in self.forum_channels:
                raise ValueError(f"Forum channel {forum_name} not found")

            forum = self.forum_channels[forum_name]
            for thread_obj in forum.threads:
                if thread_obj.id == thread_id:
                    thread = thread_obj
                    break

            if thread is None:
                raise ValueError(f"Thread with ID {thread_id} not found in forum {forum_name}")

        # Now call the parent method with the resolved thread
        return await super().add_message_to_thread(thread, content, author_name)
