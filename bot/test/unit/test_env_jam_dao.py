#!/usr/bin/env python3
"""
Unit tests for the JAM DAO Discord test environment.

These tests verify that the JAM DAO Discord structure is correctly set up
and that forum functionality works as expected.
"""

import asyncio
import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the test environment
try:
    from bot.test.core.test_env_jam_dao import JamDaoDiscordTestEnvironment
    from bot.test.mocks.forum_channel import MockForumChannel
    from bot.test.mocks.forum_tag import MockForumTag
    from bot.test.mocks.thread import MockThread
except ImportError:
    try:
        from test.core.test_env_jam_dao import JamDaoDiscordTestEnvironment
        from test.mocks.forum_channel import MockForumChannel
        from test.mocks.forum_tag import MockForumTag
        from test.mocks.thread import MockThread
    except ImportError:
        from core.test_env_generic import DiscordTestEnvironment
        from mocks.forum_channel import MockForumChannel
        from mocks.forum_tag import MockForumTag
        from mocks.thread import MockThread


class TestJamDaoEnvironment(unittest.TestCase):
    """Test cases for the JAM DAO Discord test environment"""

    def setUp(self):
        """Set up the test environment"""
        self.env = JamDaoDiscordTestEnvironment()
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.env.setup_jam_dao_structure())

    def test_jam_dao_roles_created(self):
        """Test that all JAM DAO roles are created."""
        expected_roles = [
            "Admin", "dao-team-representative", "dao-participant",
            "jam-implementer", "JAM-DAO-Bot", "DOT-GOV", "jam-search"
        ]
        for role in expected_roles:
            self.assertIn(role, self.env.roles)
            self.assertEqual(role, self.env.roles[role].name)

    def test_jam_dao_channels_created(self):
        """Test that all JAM DAO channels are created."""
        expected_channels = [
            "general", "announcements", "implementers", "jam-experience",
            "dao-updates", "coordination-all-members", "coordination-representatives",
            "public-room", "summarize-channel-test", "summarizer"
        ]
        for channel in expected_channels:
            self.assertIn(channel, self.env.channels)
            self.assertEqual(channel, self.env.channels[channel].name)

    def test_jam_dao_forum_channels_created(self):
        """Test that all JAM DAO forum channels are created."""
        expected_forum_channels = ["administrative-forum", "referendas", "public-discussions"]
        for forum in expected_forum_channels:
            self.assertIn(forum, self.env.forum_channels)
            self.assertEqual(forum, self.env.forum_channels[forum].name)

    def test_referendas_forum_tags(self):
        """Test that the referendas forum has the correct tags."""
        referendas = self.env.forum_channels["referendas"]
        tag_names = [tag.name for tag in referendas.available_tags]
        expected_tags = ["SmallSpender", "MediumSpender", "BigSpender", "Root", "WhitelistedCaller"]
        for tag in expected_tags:
            self.assertIn(tag, tag_names)

    def test_restricted_channels(self):
        """Test that restricted channels have the correct permissions."""
        # Test coordination-all-members is restricted to dao-team-representative
        coord_all = self.env.channels["coordination-all-members"]
        self.assertTrue(coord_all.is_restricted)
        self.assertIn("dao-team-representative", coord_all.allowed_roles)

        # Test coordination-representatives is restricted to dao-team-representative
        coord_rep = self.env.channels["coordination-representatives"]
        self.assertTrue(coord_rep.is_restricted)
        self.assertIn("dao-team-representative", coord_rep.allowed_roles)

    def test_users_with_roles(self):
        """Test that users have the correct roles."""
        # Test dao_rep1 has dao-team-representative role
        dao_rep1 = self.env.users["dao_rep1"]
        role_names = [role.name for role in dao_rep1.roles]
        self.assertIn("dao-team-representative", role_names)

        # Test participant1 has dao-participant role
        participant1 = self.env.users["participant1"]
        role_names = [role.name for role in participant1.roles]
        self.assertIn("dao-participant", role_names)

        # Test implementer1 has jam-implementer role
        implementer1 = self.env.users["implementer1"]
        role_names = [role.name for role in implementer1.roles]
        self.assertIn("jam-implementer", role_names)

    async def async_test_create_forum_post(self):
        """Test creating a forum post."""
        # Create a referendum post
        post = await self.env.create_forum_post(
            title="Test Referendum",
            content="This is a test referendum",
            forum_name="referendas",
            author_name="dao_rep1",
            tags=["MediumSpender"]
        )

        # Check post was created
        self.assertEqual("Test Referendum", post.name)
        self.assertEqual(1, len(post.applied_tags))
        self.assertEqual("MediumSpender", post.applied_tags[0].name)

        # Check post is in the forum
        referendas = self.env.forum_channels["referendas"]
        self.assertIn(post, referendas.threads)

        return post

    async def async_test_add_message_to_thread(self, post):
        """Test adding a message to a thread."""
        # Add a message to the thread
        message = await self.env.add_message_to_thread(
            content="This is a test message",
            thread_id=post.id,
            author_name="dao_rep1",
            forum_name="referendas"
        )

        # Check message was added
        self.assertEqual("This is a test message", message.content)
        self.assertEqual("dao_rep1", message.author.name)
        self.assertIn(message, post.messages)

        return message

    async def async_test_permission_checks(self, post):
        """Test permission checks for forum posts and threads."""
        # Test that a non-representative can't post in a restricted forum
        with self.assertRaises(ValueError):
            await self.env.create_forum_post(
                title="Unauthorized Post",
                content="This should fail",
                forum_name="coordination-representatives",
                author_name="participant1"
            )

        # Test that a non-representative can post in public-discussions
        public_post = await self.env.create_forum_post(
            title="Public Post",
            content="This should work",
            forum_name="public-discussions",
            author_name="participant1"
        )
        self.assertEqual("Public Post", public_post.name)

    def test_forum_functionality(self):
        """Test forum functionality including creating posts and adding messages."""
        # Run the async tests in the event loop
        post = self.loop.run_until_complete(self.async_test_create_forum_post())
        message = self.loop.run_until_complete(self.async_test_add_message_to_thread(post))
        self.loop.run_until_complete(self.async_test_permission_checks(post))


if __name__ == "__main__":
    unittest.main()
