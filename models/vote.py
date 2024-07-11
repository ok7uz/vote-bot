from tortoise import models, fields


class Vote(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="votes")
    poll = fields.ForeignKeyField("models.Poll", related_name="votes")

    class Meta:
        table = "votes"

    @staticmethod
    async def create_vote(user_id: int, poll_id: int) -> 'Vote':
        return await Vote.create(user_id=user_id, poll_id=poll_id)

    @staticmethod
    async def vote_exists(user_id: int, poll_id: int) -> bool:
        return await Vote.filter(user_id=user_id, poll_id=poll_id).exists()
