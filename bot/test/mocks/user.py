"""
Mock implementation of Discord User object.
"""

class MockUser:
    """
    Mock implementation of a Discord User.

    Attributes:
        id (int): The user's ID.
        name (str): The user's name.
        bot (bool): Whether the user is a bot.
        mention (str): The string used to mention the user.
        display_name (str): The user's display name.
    """
    def __init__(self, id, name, bot=False):
        self.id = id
        self.name = name
        self.bot = bot
        self.mention = f"<@{id}>"
        self.display_name = name
