"""
Mock implementation of a Discord Forum Channel.

This mock simulates a Discord forum channel with posts and threads.
"""

from datetime import datetime, timezone
from .channel import MockTextChannel
from .thread import MockThread
from .message import MockMessage

class MockForumChannel(MockTextChannel):
    """
    Mock implementation of a Discord Forum Channel.

    Attributes:
        id (int): The channel's ID.
        name (str): The channel's name.
        guild (MockGuild): The guild the channel belongs to.
        posts (dict): Dictionary of thread_id -> thread for forum posts.
        available_tags (list): List of available tags for forum posts.
    """
    def __init__(self, id, name, guild, tags=None):
        super().__init__(id, name, guild)
        self.posts = {}  # Dictionary of thread_id -> thread for forum posts
        self.available_tags = tags or []
        self.type = 15  # Discord forum channel type

    async def create_post(self, title, content, author, tags=None):
        """
        Create a new post in the forum channel.

        Args:
            title (str): The title of the post.
            content (str): The content of the initial message.
            author (MockUser): The author of the post.
            tags (list): List of tag IDs to apply to the post.

        Returns:
            MockThread: The created thread.
        """
        thread_id = len(self.posts) + 1000
        thread = MockThread(thread_id, title, self, self.guild)
        thread.created_at = datetime.now(timezone.utc)
        self.posts[thread_id] = thread
        # Also add to the threads list inherited from MockTextChannel
        self.threads.append(thread)

        # Create initial message in thread
        message_id = len(thread.messages) + 1
        message = MockMessage(message_id, content, author, thread, self.guild)
        thread.messages.append(message)

        # Add tags to the thread
        thread.applied_tags = tags or []

        return thread

    def get_thread(self, thread_id):
        """
        Get a thread by its ID.

        Args:
            thread_id (int): The ID of the thread.

        Returns:
            MockThread: The thread with the given ID, or None if not found.
        """
        return self.posts.get(thread_id)

    async def get_active_threads(self):
        """
        Get all active threads in the forum channel.

        Returns:
            list: List of active threads.
        """
        return list(self.posts.values())

    async def archived_threads(self):
        """
        Get archived threads in the forum channel.

        Returns:
            list: List of archived threads (empty for now).
        """
        # In our mock, we don't implement thread archiving yet
        return []
