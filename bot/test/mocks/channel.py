"""
Mock implementation of Discord TextChannel object.
"""

from .user import MockUser
from .message import MockMessage
from .thread import MockThread

class MockTextChannel:
    """
    Mock implementation of a Discord TextChannel.

    Attributes:
        id (int): The channel's ID.
        name (str): The channel's name.
        guild (MockGuild): The guild the channel belongs to.
        messages (list): The messages in the channel.
        threads (list): The threads in the channel.
        mention (str): The string used to mention the channel.
    """
    def __init__(self, id, name, guild):
        self.id = id
        self.name = name
        self.guild = guild
        self.messages = []
        self.threads = []
        self.mention = f"<#{id}>"
        self.is_restricted = False
        self.allowed_roles = []

    async def send(self, content=None, embed=None):
        """Send a message to the channel."""
        author = MockUser(0, "Bot", True)
        msg_id = len(self.messages) + 1
        message = MockMessage(msg_id, content, author, self, self.guild, embeds=[embed] if embed else [])
        self.messages.append(message)
        return message

    async def create_thread(self, name, message=None, auto_archive_duration=1440):
        """Create a thread in the channel."""
        thread_id = len(self.threads) + 1
        thread = MockThread(thread_id, name, self)
        self.threads.append(thread)
        return thread

    async def history(self, limit=100):
        """Get the message history of the channel."""
        return self.messages[-limit:]
