from collections import defaultdict
from datetime import timedelta

from database.models import VoteType
from utils.dto import PollDTO


def build_poll_text(
    poll: PollDTO,
    show_later: bool = True,
    later_hours: int = 3,
):
    votes = defaultdict(list)

    for vote in poll.votes:
        votes[vote.vote].append(vote.full_name)

    later = poll.meeting_at - timedelta(
        hours=later_hours,
    )

    def render(title: str, vote_type: VoteType):
        users = votes[vote_type.value]

        lines = [
            f"{title} ({len(users)})",
        ]

        for user in users:
            lines.append(f"• {user}")

        return "\n".join(lines)

    text = (
        "☕\n\n"
        "<b>Сбор на кофе</b>\n\n"
        f"📅 {poll.meeting_at:%d.%m.%Y}\n"
        f"🕘 {poll.meeting_at:%H:%M}\n"
        f"📍 {poll.place}\n\n"
        "──────────────\n\n"
        f"{render('✅ Да', VoteType.YES)}\n\n"
        "──────────────\n\n"
        f"{render('❌ Нет', VoteType.NO)}"
    )

    if show_later:
        text += (
            "\n\n──────────────\n\n"
            f"{render(f'🤔 Отвечу до {later:%H:%M}', VoteType.LATER)}"
        )

    return text