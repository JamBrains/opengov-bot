"""
Mock implementation of Discord Interaction for testing slash commands.
"""

from unittest.mock import MagicMock


class MockInteraction:
    """Mock implementation of a Discord Interaction object."""

    def __init__(self, user, guild, channel=None):
        """
        Initialize a mock interaction.

        Args:
            user (MockUser): The user who triggered the interaction
            guild (MockGuild): The guild where the interaction was triggered
            channel (MockTextChannel or MockThread, optional): The channel where the interaction was triggered
        """
        self.user = user
        self.guild = guild
        self.channel = channel

        # Create mock response and followup objects
        self.response = MagicMock()
        self.followup = MagicMock()

        # Add async methods to response
        self.response.defer = MagicMock(return_value=None)
        self.response.send_message = MagicMock(return_value=None)

        # Add async methods to followup
        self.followup.send = MagicMock(return_value=None)

        # Original response for deletion
        self.delete_original_response = MagicMock(return_value=None)

        # Command data
        self.data = {}
        self.options = []

    async def fetch_member(self, user_id):
        """
        Fetch a member from the guild.

        Args:
            user_id: The ID of the user to fetch

        Returns:
            MockMember: The member object
        """
        for member in self.guild.members:
            if member.id == user_id:
                return member
        return None
