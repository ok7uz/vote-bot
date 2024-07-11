from tortoise import models, fields


class PollChannel(models.Model):
    id = fields.BigIntField(pk=True)
    poll = fields.ForeignKeyField("models.Poll", related_name="channels")
    channel_id = fields.BigIntField()
    name = fields.CharField(max_length=255)
    link = fields.CharField(max_length=1024)

    class Meta:
        table = "channels"

    @staticmethod
    async def create_poll_channel(poll_id: int, channel_id: int, name: str, link: str) -> 'PollChannel':
        return await PollChannel.create(poll_id=poll_id, channel_id=channel_id, name=name, link=link)
