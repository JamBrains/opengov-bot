"""
Mock Discord components for testing.
This package contains mock implementations of Discord objects for testing purposes.
"""

from .user import MockUser
from .member import MockMember
from .role import MockRole
from .message import MockMessage
from .thread import MockThread
from .channel import MockTextChannel
from .guild import MockGuild
from .bot import MockBot
from .task import MockTaskLoop, MockDiscordTasks

__all__ = [
    'MockUser',
    'MockMember',
    'MockRole',
    'MockMessage',
    'MockThread',
    'MockTextChannel',
    'MockGuild',
    'MockBot',
    'MockTaskLoop',
    'MockDiscordTasks'
]
