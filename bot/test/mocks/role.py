"""
Mock implementation of Discord Role object.
"""

class MockRole:
    """
    Mock implementation of a Discord Role.

    Attributes:
        id (int): The role's ID.
        name (str): The role's name.
        position (int): The role's position in the hierarchy.
        mention (str): The string used to mention the role.
    """
    def __init__(self, id, name, position=0):
        self.id = id
        self.name = name
        self.position = position
        self.mention = f"<@&{id}>"
