from collections import defaultdict
from datetime import timedelta, datetime

from database.models import VoteType
from utils.dto import PollDTO

def later_deadline(
    meeting_at,
    hours: int,
) -> str:
    now = datetime.now()
    deadline_dt = meeting_at - timedelta(hours=hours)
    
    # Жесткий предохранитель: если расчетное время дедлайна оказалось в прошлом, 
    # сдвигаем его на 5 минут вперед от текущего момента времени
    if deadline_dt <= now:
        deadline_dt = now + timedelta(minutes=5)
        
    return deadline_dt.strftime("%H:%M")


def build_poll_text(
    dto: PollDTO,
    later_hours: int,
) -> str:

    votes = defaultdict(list)

    for vote in dto.votes:
        votes[vote.vote].append(
            vote.full_name,
        )

    def render(
        title: str,
        vote_type: VoteType,
    ) -> str:

        users = votes[vote_type.value]

        lines = [
            f"{title} ({len(users)})",
        ]

        for user in users:
            lines.append(
                f"• {user}",
            )

        return "\n".join(lines)

    text = (
        "☕\n\n"
        "<b>Сбор на кофе</b>\n\n"
        f"📅 {dto.meeting_at:%d.%m.%Y}\n"
        f"🕘 {dto.meeting_at:%H:%M}\n"
        f"📍 {dto.place}\n\n"

        "──────────────\n\n"

        f"{render('✅ Да', VoteType.YES)}\n\n"

        "──────────────\n\n"

        f"{render('❌ Нет', VoteType.NO)}"
    )

    deadline = later_deadline(
        dto.meeting_at,
        later_hours,
    )

    text += (
        "\n\n──────────────\n\n"
        f"{render(f'🤔 Отвечу до {deadline}', VoteType.LATER)}"
    )

    return text