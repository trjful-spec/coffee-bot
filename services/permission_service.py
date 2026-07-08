from aiogram import Bot

from database.models import Poll


class PermissionService:

    async def can_manage(
        self,
        bot: Bot,
        poll: Poll,
        chat_id: int,
        user_id: int,
    ) -> bool:

        if poll.author_id == user_id:
            return True

        member = await bot.get_chat_member(
            chat_id,
            user_id,
        )

        return member.status in (
            "administrator",
            "creator",
        )


permission_service = PermissionService()