import json
import io
from bot.utils.participation_rate import calculate_current_participation_rate

def calculate_participation_rate_test():
    votes = {}
    members = {}
    try:
        with io.open("bot/test/fixtures/vote_counts.json", "r") as file:
            data = file.read()
            votes = json.loads(data)
    except FileNotFoundError:
        return "Votes file not found"

    try:
        with io.open("bot/test/fixtures/members.json", "r") as file:
            data = file.read()
            members = json.loads(data)
    except FileNotFoundError:
        return "Members file not found"

    return calculate_current_participation_rate(votes, members)

if __name__ == "__main__":
    content = calculate_participation_rate_test()
    print("\n".join(content))
