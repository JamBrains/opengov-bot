"""
Mock implementation of Discord Member object.
"""

from .user import MockUser

class MockMember(MockUser):
    """
    Mock implementation of a Discord Member (User in a Guild).

    Attributes:
        id (int): The member's ID.
        name (str): The member's name.
        guild (MockGuild): The guild the member belongs to.
        roles (list): The roles the member has.
        bot (bool): Whether the member is a bot.
        mention (str): The string used to mention the member.
        display_name (str): The member's display name.
    """
    def __init__(self, id, name, guild, roles=None, bot=False):
        super().__init__(id, name, bot)
        self.guild = guild
        self.roles = roles or []

    async def add_roles(self, *roles):
        """Add roles to the member."""
        self.roles.extend(roles)

    async def remove_roles(self, *roles):
        """Remove roles from the member."""
        for role in roles:
            if role in self.roles:
                self.roles.remove(role)
