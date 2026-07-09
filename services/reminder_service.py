import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot
from database.models import PollStatus
from services.coffee_service import coffee_service
from services.settings_service import settings_service

logger = logging.getLogger(__name__)

async def poll_reminder_worker(bot: Bot):
    """Фоновое задание, работающее раз в минуту."""
    while True:
        try:
            now = datetime.now()
            # Запрашиваем опросы, требующие внимания
            polls = await coffee_service.get_polls_for_worker()

            for poll in polls:
                if not poll.meeting_at:
                    continue

                # --- ЛОГИКА ДЛЯ АКТИВНЫХ ОПРОСОВ ---
                if poll.status == PollStatus.ACTIVE:
                    time_left = poll.meeting_at - now

                    # 1. Время встречи наступило -> АВТОМАТИЧЕСКИ ЗАКРЫВАЕМ
                    if time_left <= timedelta(0):
                        await coffee_service.close_poll(poll.id)
                        
                        try:
                            await bot.send_message(
                                chat_id=poll.chat_id, 
                                text="🔒 Время голосования вышло! Сбор ответов завершен."
                            )
                            from services.poll_sender import update_poll_message
                            await update_poll_message(bot=bot, poll_id=poll.id)
                        except Exception as e:
                            logger.error(f"Ошибка при закрытии опроса {poll.id}: {e}")
                        continue

                    # Получаем настройки интервала для этого чата
                    settings = await settings_service.get(poll.chat_id)
                    interval_hours = settings.min_vote_hours
                    
                    # Вычисляем точное время дедлайна для кнопки "Отвечу позже"
                    deadline = poll.meeting_at - timedelta(hours=interval_hours)

                    # 2. Финальный тег ровно за 10 минут до конца (высший приоритет)
                    if time_left <= timedelta(minutes=10):
                        if not poll.final_reminder_sent:
                            await send_later_tags(bot, poll)
                            await coffee_service.update_reminder_state(poll.id, final_sent=True)

                    # 3. Ежечасный тег, если дедлайн "Отвечу позже" уже пройден
                    elif now >= deadline:
                        if poll.last_reminder_hour != now.hour:
                            await send_later_tags(bot, poll)
                            await coffee_service.update_reminder_state(poll.id, last_hour=now.hour)

                # --- ЛОГИКА ДЛЯ ЗАКРЫТЫХ ОПРОСОВ (ОТКРЕПЛЕНИЕ ЧЕРЕЗ 2 ЧАСА) ---
                elif poll.status == PollStatus.CLOSED and not poll.is_unpinned:
                    if now - poll.meeting_at >= timedelta(hours=2):
                        if poll.message_id:
                            try:
                                await bot.unpin_chat_message(
                                    chat_id=poll.chat_id, 
                                    message_id=poll.message_id
                                )
                                logger.info(f"Сообщение {poll.message_id} успешно откреплено в чате {poll.chat_id}")
                            except Exception as e:
                                logger.error(f"Не удалось открепить сообщение {poll.message_id}: {e}")
                        
                        await coffee_service.mark_as_unpinned(poll.id)

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