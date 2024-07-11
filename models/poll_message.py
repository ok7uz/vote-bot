from loguru import logger
from tortoise import fields, models


class PollMessage(models.Model):
    id = fields.IntField(pk=True)
    poll = fields.ForeignKeyField("models.Poll", related_name="messages")
    chat_id = fields.BigIntField()
    message_id = fields.BigIntField()

    class Meta:
        table = "poll_messages"
