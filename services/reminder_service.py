import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot
from services.coffee_service import coffee_service

logger = logging.getLogger(__name__)

async def poll_reminder_worker(bot: Bot):
    """Фоновое задание, работающее раз в минуту."""
    while True:
        try:
            now = datetime.now()
            active_polls = await coffee_service.get_all_active_polls()

            for poll in active_polls:
                # Используем ваше поле meeting_at вместо end_date
                if not poll.meeting_at:
                    continue

                time_left = poll.meeting_at - now

                # Условие 1: До конца больше 1 часа -> тегаем в начале часа (00 минут)
                if time_left > timedelta(hours=1):
                    if now.minute == 0:
                        if getattr(poll, 'last_reminder_hour', -1) != now.hour:
                            await send_later_tags(bot, poll)
                            poll.last_reminder_hour = now.hour

                # Условие 2: До конца меньше 1 часа -> тегаем ровно за 10 минут
                elif timedelta(minutes=9) <= time_left <= timedelta(minutes=10):
                    if not getattr(poll, 'final_reminder_sent', False):
                        await send_later_tags(bot, poll)
                        poll.final_reminder_sent = True

        except Exception as e:
            logger.error(f"Ошибка в воркере напоминаний: {e}")

        await asyncio.sleep(60)


async def send_later_tags(bot: Bot, poll):
    """Вспомогательная функция для сбора пользователей и отправки сообщения."""
    votes_to_tag = await coffee_service.get_later_voters(poll.id)
    
    if not votes_to_tag:
        return

    mentions = []
    for v in votes_to_tag:
        # Используем v.user_id и v.full_name, так как они сохраняются в вашей таблице Vote
        mentions.append(f'<a href="tg://user?id={v.user_id}">{v.full_name}</a>')

    tag_text = ", ".join(mentions)
    
    text = (
        f"🔔 Напоминание для ответивших «Отвечу позже»:\n"
        f"{tag_text}\n\n"
        f"Пора определиться с выбором! ☕"
    )

    try:
        await bot.send_message(
            chat_id=poll.chat_id,
            text=text,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Не удалось отправить напоминание в чат {poll.chat_id}: {e}")