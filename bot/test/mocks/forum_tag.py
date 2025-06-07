"""
Mock implementation of Discord Forum Tag.
"""

class MockForumTag:
    """
    Mock implementation of a Discord Forum Tag.

    Attributes:
        id (int): The tag's ID.
        name (str): The tag's name.
        emoji (str, optional): The emoji associated with the tag.
        moderated (bool): Whether the tag is moderated.
    """
    def __init__(self, id, name, emoji=None, moderated=False):
        self.id = id
        self.name = name
        self.emoji = emoji
        self.moderated = moderated

    def __eq__(self, other):
        if isinstance(other, MockForumTag):
            return self.id == other.id
        elif isinstance(other, str):
            return self.name == other
        elif isinstance(other, int):
            return self.id == other
        return False

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<MockForumTag id={self.id} name='{self.name}'>"
