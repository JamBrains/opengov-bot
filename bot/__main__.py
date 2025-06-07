#!/usr/bin/env python
"""
Main entry point for the JAM DAO Discord Bot when run as a module.
This allows the bot to be run using `python -m bot` command.
"""

import sys
from bot.cli_module import main

if __name__ == "__main__":
    sys.exit(main())
