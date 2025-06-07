"""
Mock implementation of Discord Bot object.
"""

from .user import MockUser

class MockBot:
    """
    Mock implementation of a Discord Bot.

    Attributes:
        user (MockUser): The bot's user.
        guilds (list): The guilds the bot is in.
        commands (dict): The commands registered with the bot.
        listeners (dict): The event listeners registered with the bot.
        event_handlers (dict): The event handlers registered with the bot.
    """
    def __init__(self):
        self.user = MockUser(0, "TestBot", True)
        self.guilds = []
        self.commands = {}
        self.listeners = {}
        self.event_handlers = {}

    def add_guild(self, guild):
        """Add a guild to the bot."""
        self.guilds.append(guild)
        return guild

    def get_guild(self, guild_id):
        """Get a guild by ID."""
        for guild in self.guilds:
            if guild.id == guild_id:
                return guild
        return None

    def command(self, name=None):
        """Decorator to register a command."""
        def decorator(func):
            cmd_name = name or func.__name__
            self.commands[cmd_name] = func
            return func
        return decorator

    def event(self, func):
        """Decorator to register an event handler."""
        self.event_handlers[func.__name__] = func
        return func

    def listen(self, name=None):
        """Decorator to register an event listener."""
        def decorator(func):
            event_name = name or func.__name__
            if event_name not in self.listeners:
                self.listeners[event_name] = []
            self.listeners[event_name].append(func)
            return func
        return decorator

    async def process_command(self, message):
        """Process a command from a message."""
        if message.content.startswith('!'):
            cmd_parts = message.content[1:].split()
            cmd_name = cmd_parts[0]
            if cmd_name in self.commands:
                await self.commands[cmd_name](self, message)

    async def trigger_event(self, event_name, *args, **kwargs):
        """Trigger an event."""
        if event_name in self.event_handlers:
            await self.event_handlers[event_name](*args, **kwargs)

        if event_name in self.listeners:
            for listener in self.listeners[event_name]:
                await listener(*args, **kwargs)
