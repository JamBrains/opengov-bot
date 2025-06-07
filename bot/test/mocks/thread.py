"""
Mock implementation of Discord Thread object.
"""

from .user import MockUser
from .message import MockMessage

class MockThread:
    """
    Mock implementation of a Discord Thread.

    Attributes:
        id (int): The thread's ID.
        name (str): The thread's name.
        parent (MockTextChannel): The parent channel of the thread.
        owner (MockUser): The owner of the thread.
        guild (MockGuild): The guild the thread belongs to.
        messages (list): The messages in the thread.
        applied_tags (list): Tags applied to the thread (for forum posts).
        created_at (datetime): When the thread was created.
        archived (bool): Whether the thread is archived.
        locked (bool): Whether the thread is locked.
        mention (str): The string used to mention the thread.
    """
    def __init__(self, id, name, parent, guild=None, owner=None):
        from datetime import datetime, timezone

        self.id = id
        self.name = name
        self.parent = parent
        self.parent_id = parent.id if parent else None
        self.owner = owner
        self.guild = guild or parent.guild
        self.messages = []
        self.applied_tags = []
        self.created_at = datetime.now(timezone.utc)
        self.archived = False
        self.locked = False
        self.mention = f"<#{id}>"
        self.type = 11  # Discord thread type

    async def send(self, content=None, embed=None, author=None):
        """Send a message to the thread.

        Args:
            content (str, optional): The content of the message. Defaults to None.
            embed (MockEmbed, optional): The embed to send. Defaults to None.
            author (MockUser, optional): The author of the message. Defaults to a bot user.

        Returns:
            MockMessage: The created message
        """
        if author is None:
            author = MockUser(0, "Bot", True)

        msg_id = len(self.messages) + 1
        message = MockMessage(msg_id, content, author, self, self.guild, embeds=[embed] if embed else [])
        self.messages.append(message)
        return message
