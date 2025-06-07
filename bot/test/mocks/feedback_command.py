"""
Mock implementation of the feedback command for testing.
"""

import re
import logging
from unittest.mock import MagicMock

# Use a simple print for logging in tests
def log_error(message):
    print(f"ERROR: {message}")

async def mock_feedback(interaction, message, config, client, public_thread=None):
    """
    Mock implementation of the feedback command for testing.

    Args:
        interaction: The mock interaction object
        message: The feedback message
        config: The configuration object
        client: The mock client object
        public_thread: Optional thread to post the feedback to
    """
    print("DEBUG: Starting mock_feedback function")

    try:
        # First, check if the user has the dao-team-representative role
        user = interaction.user
        has_representative_role = False
        for role in user.roles:
            if role.name == "dao-team-representative" or role.name == "Admin":
                has_representative_role = True
                break

        if not has_representative_role:
            print("DEBUG: User does not have dao-team-representative role")
            interaction.followup.send(
                content="You don't have permission to use this command. Only users with the @dao-team-representative role can provide feedback.",
                ephemeral=True
            )
            return

        # Check if the command is being used in a thread in the referendas channel
        channel = interaction.channel
        print(f"DEBUG: Channel: {channel}, has parent_id: {hasattr(channel, 'parent_id')}")

        # First check if this is a thread (has parent_id attribute)
        if not hasattr(channel, 'parent_id'):
            print("DEBUG: Command not used in a thread")
            interaction.followup.send(
                content="This command can only be used in threads within the #referendas channel.",
                ephemeral=True
            )
            return

        # Then check if it's in the referendas channel
        print(f"DEBUG: Channel parent_id: {channel.parent_id}, config.DISCORD_FORUM_CHANNEL_ID: {config.DISCORD_FORUM_CHANNEL_ID}")
        if channel.parent_id != config.DISCORD_FORUM_CHANNEL_ID:
            print("DEBUG: Command not used in a thread in the referendas channel")
            interaction.followup.send(
                content="This command can only be used in threads within the #referendas channel.",
                ephemeral=True
            )
            return

        # Extract the referendum number from the thread name
        thread_name = channel.name
        referendum_number = None

        # Try to extract the referendum number from the referenda number in the thread name
        match = re.search(r'^#?(\d+):', thread_name)
        if match:
            referendum_number = match.group(1)
            print(f"DEBUG: Extracted referendum number: {referendum_number}")
        else:
            print("DEBUG: Could not extract referendum number from thread name")
            interaction.followup.send(
                content="Could not determine the referendum number from this thread's name.",
                ephemeral=True
            )
            return

        # Use the provided public_thread if available
        existing_thread = public_thread
        print(f"DEBUG: Using provided public_thread: {existing_thread.name if existing_thread else 'None'}")

        if not existing_thread:
            print("DEBUG: No public_thread provided, looking for it")
            # Find the public-discussions channel
            guild = interaction.guild
            public_channel = None
            for channel in guild.channels:
                if channel.name == "public-discussions":
                    public_channel = channel
                    break

            if not public_channel:
                print("DEBUG: public-discussions channel not found")
                interaction.followup.send(
                    content="Error: Could not find the public-discussions channel",
                    ephemeral=True
                )
                return

            # Look for an existing thread in public-discussions with the format 'Ref 123:'
            pattern = rf'^Ref\s+{re.escape(str(referendum_number))}:'
            for thread in public_channel.threads:
                if re.match(pattern, thread.name):
                    existing_thread = thread
                    break

            # If no thread found, create a new one
            if not existing_thread:
                print("DEBUG: Creating new thread in public-discussions")
                new_thread = MagicMock()
                new_thread.name = f"Ref {thread_name}"
                new_thread.id = len(public_channel.threads) + 1000
                new_thread.messages = []
                new_thread.guild = guild
                public_channel.threads.append(new_thread)
                existing_thread = new_thread

        # Add the feedback message to the thread
        if existing_thread:
            print(f"DEBUG: Adding feedback to thread: {existing_thread.name}, ID: {existing_thread.id}")
            print(f"DEBUG: Thread has {len(existing_thread.messages)} messages before adding feedback")

            # Import the necessary mock classes
            from bot.test.mocks.message import MockMessage
            from bot.test.mocks.user import MockUser

            # Create a bot user to be the author of the feedback message
            bot_user = MockUser(0, "JAM-DAO-Bot", True)

            # Create the feedback message
            msg_id = len(existing_thread.messages) + 1
            feedback_content = f"**Feedback:** {message}"
            print(f"DEBUG: Creating feedback message with content: {feedback_content}")

            # Create a MockMessage object and add it to the thread's messages list
            feedback_msg = MockMessage(
                id=msg_id,
                content=feedback_content,
                author=bot_user,
                channel=existing_thread,
                guild=existing_thread.guild
            )

            existing_thread.messages.append(feedback_msg)
            print(f"DEBUG: Thread now has {len(existing_thread.messages)} messages after adding feedback")
            print(f"DEBUG: Last message content: {existing_thread.messages[-1].content}")

            # Confirm to the user that their feedback was posted
            interaction.followup.send(
                content="Your feedback has been anonymously posted to the public-discussions channel.",
                ephemeral=True
            )
        else:
            print("DEBUG: No thread found in public-discussions channel and couldn't create one")
            interaction.followup.send(
                content="Error: Could not find or create a thread in public-discussions channel.",
                ephemeral=True
            )

    except Exception as e:
        print(f"DEBUG: Exception in mock_feedback: {e}")
        interaction.followup.send(
            content=f"Error in feedback command: {e}",
            ephemeral=True
        )
