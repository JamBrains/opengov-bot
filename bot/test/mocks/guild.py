"""
Mock implementation of Discord Guild object.
"""

class MockGuild:
    """
    Mock implementation of a Discord Guild (Server).

    Attributes:
        id (int): The guild's ID.
        name (str): The guild's name.
        channels (list): The channels in the guild.
        members (list): The members in the guild.
        roles (list): The roles in the guild.
    """
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.channels = []
        self.members = []
        self.roles = []

    def add_channel(self, channel):
        """Add a channel to the guild."""
        self.channels.append(channel)
        return channel

    def add_member(self, member):
        """Add a member to the guild."""
        self.members.append(member)
        return member

    def add_role(self, role):
        """Add a role to the guild."""
        self.roles.append(role)
        return role

    def get_channel(self, channel_id):
        """Get a channel by ID."""
        for channel in self.channels:
            if channel.id == channel_id:
                return channel
        return None

    def get_member(self, user_id):
        """Get a member by ID."""
        for member in self.members:
            if member.id == user_id:
                return member
        return None
