from aiogram import Bot
from loguru import logger
from tortoise import fields, models

from keyboards.inline import create_channel_poll_keyboard


class Poll(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    creator_id = fields.BigIntField()
    message_id = fields.IntField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    ended_at = fields.DatetimeField(null=True)
    is_active = fields.BooleanField(default=True)

    options = fields.ReverseRelation["PollOption"]

    class Meta:
        table = "polls"
        ordering = ["id"]

    @staticmethod
    async def create_poll(title: str, creator_id: int, message_id: int) -> 'Poll':
        poll = await Poll.create(title=title, creator_id=creator_id, message_id=message_id)
        logger.success(f"{poll} created")
        return poll

    @staticmethod
    async def get_poll_by_id(poll_id: int) -> 'Poll':
        poll = await Poll.get_or_none(id=poll_id)
        return poll

    @staticmethod
    async def get_all_polls() -> list['Poll']:
        polls = await Poll.all()
        return polls

    @staticmethod
    async def delete_by_id(poll_id: int) -> None:
        poll = await Poll.get(id=poll_id)
        await poll.delete()
        logger.success(f"{poll} deleted")

    def __str__(self):
        return f'Poll #{self.id}'


class PollOption(models.Model):
    id = fields.IntField(pk=True)
    title = fields.TextField()
    poll = fields.ForeignKeyField("models.Poll", related_name="options")
    votes = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "poll_options"
        ordering = ["id"]

    @staticmethod
    async def create_poll_option(title: str, poll: Poll) -> 'PollOption':
        poll_option = await PollOption.create(title=title, poll=poll)
        return poll_option

    async def increase_votes(self, bot: Bot) -> None:
        self.votes = self.votes + 1
        await self.save()
        poll = await self.poll
        messages = await poll.messages.all()
        options = await poll.options.all()
        bot_info = await bot.get_me()
        bot_link = f"https://t.me/{bot_info.username}"
        for message in messages:
            await bot.edit_message_reply_markup(
                message.chat_id, message.message_id,
                reply_markup=create_channel_poll_keyboard(
                    options, poll.id, bot_link
                ))
