"""
Mock implementation of the /vote slash command for testing.
"""
import asyncio
import discord
from discord import Embed
from datetime import datetime, timezone

async def mock_vote(interaction, referendum, conviction, decision, config, client=None):
    """
    Mock implementation of the /vote slash command for testing.

    Args:
        interaction: The Discord interaction object
        referendum: The referendum number to vote on
        conviction: The conviction choice (app_commands.Choice object with name and value)
        decision: The decision choice (app_commands.Choice object with name and value)
        config: The bot configuration
        client: The Discord client
    """
    print(f"DEBUG: Starting mock_vote function")
    print(f"DEBUG: Referendum: {referendum}, Conviction: {conviction}, Decision: {decision}")

    try:
        print("DEBUG: Starting permission check")
        # Check if user has permission to vote (must have dao-team-representative role)
        user_id = interaction.user.id
        member = interaction.user

        # Check if the user has the required role
        has_required_role = False
        for role in member.roles:
            if role.name == config.DISCORD_VOTER_ROLE_NAME:
                has_required_role = True
                break

        if not has_required_role:
            print(f"DEBUG: User does not have {config.DISCORD_VOTER_ROLE_NAME} role")
            # In the test environment, we'll just set the response content directly
            # instead of using await
            interaction.followup.send.return_value = None
            interaction.followup.send(
                content=f"You don't have permission to vote. Only users with the @{config.DISCORD_VOTER_ROLE_NAME} role can vote.",
                ephemeral=True
            )
            return

        print("DEBUG: User has permission, proceeding with vote")
        # Simulate vote processing
        try:
            print("DEBUG: About to sleep")
            await asyncio.sleep(0.1)
            print("DEBUG: Sleep completed")
        except Exception as e:
            print(f"DEBUG: Error during sleep: {str(e)}")

        # Send confirmation message
        print("DEBUG: About to send confirmation message")
        # In the test environment, we'll just set the response content directly
        # instead of using await
        interaction.followup.send.return_value = None
        interaction.followup.send(
            content="Initializing extrinsic, please wait...",
            ephemeral=True
        )
        print("DEBUG: Confirmation message sent")

        # Simulate blockchain interaction
        try:
            print("DEBUG: About to sleep again")
            await asyncio.sleep(0.1)
            print("DEBUG: Second sleep completed")
        except Exception as e:
            print(f"DEBUG: Error during second sleep: {str(e)}")

        # Create a mock extrinsic hash
        extrinsic_hash = f"0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"

        # Determine color based on decision
        color = 0x00FF00  # Green for AYE
        emoji = "✅"
        if decision.value == "nay":
            color = 0xFF0000  # Red for NAY
            emoji = "❌"
        elif decision.value == "abstain":
            color = 0xFFFF00  # Yellow for ABSTAIN
            emoji = "⚠️"

        # Create embed for vote confirmation
        extrinsic_embed = Embed(
            color=color,
            title='An on-chain vote has been cast',
            description=f'{emoji} {decision.value.upper()} on proposal **#{referendum}**',
            timestamp=datetime.now(timezone.utc)
        )

        # Add fields to embed
        short_extrinsic_hash = f"{extrinsic_hash[:8]}...{extrinsic_hash[-8:]}"
        extrinsic_embed.add_field(
            name='Extrinsic hash',
            value=f'[{short_extrinsic_hash}](https://{config.NETWORK_NAME}.subscan.io/extrinsic/{extrinsic_hash})',
            inline=True
        )
        extrinsic_embed.add_field(name='Executed by', value=f'<@{interaction.user.id}>', inline=True)
        extrinsic_embed.add_field(name='\u200b', value='\u200b', inline=False)
        extrinsic_embed.add_field(name='Decision', value=f"{decision.value.upper()}", inline=True)
        extrinsic_embed.add_field(name='Conviction', value=f"{conviction.value.upper()}", inline=True)
        extrinsic_embed.set_footer(text="This vote was made using /vote")

        # In the test environment, we'll just log that we would send an embed
        # instead of actually trying to send it to the channel
        if hasattr(interaction.channel, 'parent_id'):
            print(f"DEBUG: Would send vote confirmation to thread with ID {interaction.channel.id}")
        else:
            print(f"DEBUG: Would send vote confirmation to channel {interaction.channel.name if hasattr(interaction.channel, 'name') else 'unknown'}")

        # For testing purposes, we'll just send a followup message instead
        interaction.followup.send.return_value = None
        interaction.followup.send(
            content=f"Vote {decision.value.upper()} with {conviction.value} conviction on referendum #{referendum} has been cast!",
            ephemeral=False
        )

        print(f"DEBUG: mock_vote completed successfully")
        return True

    except Exception as e:
        print(f"DEBUG: Error in mock_vote: {str(e)}")
        interaction.followup.send(
            content=f"An error occurred while processing your vote: {str(e)}",
            ephemeral=True
        )
        return False
