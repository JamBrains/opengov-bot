def calculate_current_participation_rate(votes, members):
    # Calculate total number of ACTIVE proposals
    total_proposals = len(votes)
    
    members_votes = {}
    for member in members:
        member_username = member['username']
        member_display_name = member['display name']
        members_votes[member_username] = {
            'votes': 0,
            'participation_rate': 0.0,
            'display_name': member_display_name
        }
    
    for proposal_id, proposal_data in votes.items():
            for user_id, user_data in proposal_data.get('users', {}).items():
                username = user_data.get('username')[:-2]  # Remove last two characters
                if username in members_votes:
                    members_votes[username]['votes'] += 1
    
    # Calculate participation rate for each member
    for username, stats in members_votes.items():
        stats['participation_rate'] = (stats['votes'] / total_proposals * 100) if total_proposals > 0 else 0
    
    content = []
    content.append("\nParticipation Statistics:")
    content.append(f"Total number of active proposals: {total_proposals}")
    content.append("\nMember Participation:")
    
    for username, stats in sorted(members_votes.items(), key=lambda x: x[1]['votes'], reverse=True):
        content.append(f"{stats['display_name']} ({username}): {stats['votes']} votes out of {total_proposals} proposals ({stats['participation_rate']:.1f}%)")
    
    return content