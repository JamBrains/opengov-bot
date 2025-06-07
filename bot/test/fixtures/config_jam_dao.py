"""
JAM DAO Discord server configuration fixture.

This module contains the configuration for the JAM DAO Discord server structure,
including roles, channels, categories, and forum tags.
"""

# Roles configuration with position (higher position = higher priority)
ROLES = [
    {"name": "Admin", "position": 8},
    {"name": "dao-team-representative", "position": 7},
    {"name": "dao-participant", "position": 6},
    {"name": "jam-implementer", "position": 5},
    {"name": "JAM-DAO-Bot", "position": 4},
    {"name": "DOT-GOV", "position": 3},
    {"name": "Server Booster", "position": 2},
    {"name": "jam-search", "position": 1}
]

# Standard text channels
STANDARD_CHANNELS = [
    {"name": "general", "category": None},
    {"name": "announcements", "category": None}
]

# Channels with categories
CATEGORIZED_CHANNELS = [
    {"name": "implementers", "category": "Implementers Collective"},
    {"name": "jam-experience", "category": "Implementers Collective"},
    {"name": "dao-updates", "category": "DAO"}
]

# Restricted channels with role permissions
RESTRICTED_CHANNELS = [
    {"name": "coordination-all-members", "restricted_to": ["dao-team-representative"]},
    {"name": "coordination-representatives", "restricted_to": ["dao-team-representative"]}
]

# Other miscellaneous channels
OTHER_CHANNELS = [
    {"name": "public-room", "category": None},
    {"name": "summarize-channel-test", "category": None},
    {"name": "summarizer", "category": None}
]

# Forum tags for referenda
REFERENDUM_TAGS = [
    {"name": "MediumSpender", "id": 101},
    {"name": "BigSpender", "id": 102},
    {"name": "Root", "id": 103},
    {"name": "SmallSpender", "id": 104},
    {"name": "WhitelistedCaller", "id": 105},
    {"name": "Treasurer", "id": 106},
    {"name": "BigTipper", "id": 107},
    {"name": "SmallTipper", "id": 108},
    {"name": "GeneralAdmin", "id": 109},
    {"name": "ReferendumCanceller", "id": 110}
]

# Forum channels
FORUM_CHANNELS = [
    {
        "name": "referendas",
        "category": "DAO",
        "tags": REFERENDUM_TAGS,
        "read_access": ["dao-team-representative", "dao-participant", "Admin", "jam-implementer"],
        "write_access": ["dao-team-representative", "dao-participant", "Admin"],
        "vote_access": ["dao-team-representative", "Admin"]
    },
    {"name": "administrative-forum", "category": "DAO", "tags": None},
    {"name": "public-discussions", "category": "DAO", "tags": None}
]

# Users with their roles
USERS = [
    {"name": "admin_user", "roles": ["Admin"]},
    # Representatives for voting and quorum calculation
    {"name": "dao_rep1", "roles": ["dao-team-representative"]},
    {"name": "dao_rep2", "roles": ["dao-team-representative"]},
    {"name": "dao_rep3", "roles": ["dao-team-representative"]},
    {"name": "dao_rep4", "roles": ["dao-team-representative"]},
    {"name": "dao_rep5", "roles": ["dao-team-representative"]},
    # Participants who can comment but not vote
    {"name": "participant1", "roles": ["dao-participant"]},
    {"name": "participant2", "roles": ["dao-participant"]},
    {"name": "participant3", "roles": ["dao-participant"]},
    # Implementers with basic access
    {"name": "implementer1", "roles": ["jam-implementer"]},
    {"name": "implementer2", "roles": ["jam-implementer"]},
    # Bots
    {"name": "bot_user", "roles": ["JAM-DAO-Bot"]},
    {"name": "dotgov_bot", "roles": ["DOT-GOV"]},
    {"name": "search_bot", "roles": ["jam-search"]},
    {"name": "booster_bot", "roles": ["Server Booster"]}
]

# All channels combined for convenience
ALL_CHANNELS = STANDARD_CHANNELS + CATEGORIZED_CHANNELS + RESTRICTED_CHANNELS + OTHER_CHANNELS

def get_all_roles():
    """Return all roles configuration."""
    return ROLES

def get_all_channels():
    """Return all channels configuration."""
    return ALL_CHANNELS

def get_forum_channels():
    """Return forum channels configuration."""
    return FORUM_CHANNELS

def get_users():
    """Return users configuration."""
    return USERS
