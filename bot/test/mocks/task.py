"""
Mock implementation of Discord Task objects.
"""

import asyncio
from datetime import datetime, timedelta, timezone

class MockTaskLoop:
    """
    Mock implementation of a Discord Task Loop.

    Attributes:
        minutes (int): The minutes between loop iterations.
        seconds (int): The seconds between loop iterations.
        hours (int): The hours between loop iterations.
        callback (callable): The function to call on each iteration.
        _task (asyncio.Task): The underlying asyncio task.
        _running (bool): Whether the task is running.
        _name (str): The name of the task.
        next_iteration (datetime): When the next iteration will run.
    """
    def __init__(self, minutes=0, seconds=0, hours=0):
        self.minutes = minutes
        self.seconds = seconds
        self.hours = hours
        self.callback = None
        self._task = None
        self._running = False
        self._name = None
        self.next_iteration = datetime.now(timezone.utc) + timedelta(
            minutes=minutes, seconds=seconds, hours=hours
        )

    def __call__(self, func):
        """Register the callback function."""
        self.callback = func
        return self

    def start(self):
        """Start the task loop."""
        self._running = True
        self._task = asyncio.create_task(self._run())
        return self._task

    async def _run(self):
        """Run the task loop."""
        while self._running:
            await self.callback()
            self.next_iteration = datetime.now(timezone.utc) + timedelta(
                minutes=self.minutes, seconds=self.seconds, hours=self.hours
            )
            await asyncio.sleep(0.1)  # Short sleep for testing purposes

    def stop(self):
        """Stop the task loop."""
        self._running = False
        if self._task:
            self._task.cancel()

    def is_running(self):
        """Check if the task loop is running."""
        return self._running

    def get_task(self):
        """Get the task object."""
        return self

    def get_name(self):
        """Get the name of the task."""
        return self._name

    def set_name(self, name):
        """Set the name of the task."""
        self._name = name

    def before_loop(self, func):
        """Register a function to run before the loop starts."""
        return func

    def after_loop(self, func):
        """Register a function to run after the loop ends."""
        return func

class MockDiscordTasks:
    """
    Mock implementation of Discord Tasks module.
    """
    @staticmethod
    def loop(minutes=0, seconds=0, hours=0):
        """Create a task loop."""
        return MockTaskLoop(minutes=minutes, seconds=seconds, hours=hours)
