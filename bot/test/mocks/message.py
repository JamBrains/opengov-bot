"""
Mock implementation of Discord Message object.
"""

from datetime import datetime, timezone

class MockMessage:
    """
    Mock implementation of a Discord Message.

    Attributes:
        id (int): The message's ID.
        content (str): The message's content.
        author (MockUser): The user who sent the message.
        channel (MockTextChannel): The channel the message was sent in.
        guild (MockGuild): The guild the message was sent in.
        attachments (list): The attachments in the message.
        embeds (list): The embeds in the message.
        created_at (datetime): When the message was created.
        reactions (list): The reactions on the message.
    """
    def __init__(self, id, content, author, channel, guild=None, attachments=None, embeds=None):
        self.id = id
        self.content = content
        self.author = author
        self.channel = channel
        self.guild = guild
        self.attachments = attachments or []
        self.embeds = embeds or []
        self.created_at = datetime.now(timezone.utc)
        self.reactions = []

    async def add_reaction(self, emoji):
        """Add a reaction to the message."""
        self.reactions.append(emoji)

    async def remove_reaction(self, emoji, user):
        """Remove a reaction from the message."""
        if emoji in self.reactions:
            self.reactions.remove(emoji)

    async def edit(self, content=None, embed=None):
        """Edit the message's content or embed."""
        if content is not None:
            self.content = content
        if embed is not None:
            if not self.embeds:
                self.embeds = [embed]
            else:
                self.embeds[0] = embed

    async def delete(self):
        """Delete the message."""
        # Simulate message deletion
        self.channel.messages.remove(self)
